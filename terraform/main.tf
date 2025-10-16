terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

# Variables for sensitive data
variable "sql_admin_login" {
  description = "SQL Server administrator login"
  type        = string
  sensitive   = true
}

variable "sql_admin_password" {
  description = "SQL Server administrator password"
  type        = string
  sensitive   = true
}

# Data source for current client configuration
data "azurerm_client_config" "current" {}

# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = "RG-EcommerceETE"
  location = "Southeast Asia"

  tags = {
    Environment = "Development"
    Project     = "Ecommerce-ETE"
    ManagedBy   = "Terraform"
  }
}

# Storage Account with ADLS Gen2 and Hierarchical Namespace
resource "azurerm_storage_account" "storage" {
  name                     = "storageecommerceete"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true # Enable Hierarchical Namespace for ADLS Gen2

  tags = {
    Environment = "Development"
    Project     = "Ecommerce-ETE"
  }
}

# Storage Containers
resource "azurerm_storage_container" "bronze" {
  name                  = "bronze"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "silver" {
  name                  = "silver"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "gold" {
  name                  = "gold"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "metastore" {
  name                  = "metastore"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}

# Data Factory V2
resource "azurerm_data_factory" "df" {
  name                = "df-ecommerceete"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  tags = {
    Environment = "Development"
    Project     = "Ecommerce-ETE"
  }
}

# SQL Server
resource "azurerm_mssql_server" "sql_server" {
  name                         = "sqlecommerceete"
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location
  version                      = "12.0"
  administrator_login          = var.sql_admin_login
  administrator_login_password = var.sql_admin_password

  azuread_administrator {
    login_username = data.azurerm_client_config.current.object_id
    object_id      = data.azurerm_client_config.current.object_id
  }

  tags = {
    Environment = "Development"
    Project     = "Ecommerce-ETE"
  }
}

# Ip address
data "http" "myip" {
  url = "https://api.ipify.org"
}

# SQL Database with Serverless configuration
resource "azurerm_mssql_database" "sql_db" {
  name           = "dbecommerceete"
  server_id      = azurerm_mssql_server.sql_server.id
  collation      = "SQL_Latin1_General_CP1_CI_AS"
  max_size_gb    = 1
  sku_name       = "GP_S_Gen5_1"
  zone_redundant = false
  
  auto_pause_delay_in_minutes = 60
  min_capacity                = 1

  tags = {
    Environment = "Development"
    Project     = "Ecommerce-ETE"
  }
}

# SQL Firewall Rule - Allow Azure Services
resource "azurerm_mssql_firewall_rule" "allow_azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_mssql_server.sql_server.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# SQL Firewall Rule - Current Client IP
resource "azurerm_mssql_firewall_rule" "client_ip" {
  name             = "ClientIPAddress"
  server_id        = azurerm_mssql_server.sql_server.id
  start_ip_address = chomp(data.http.myip.response_body)
  end_ip_address   = chomp(data.http.myip.response_body)
}

# Azure Databricks Workspace
resource "azurerm_databricks_workspace" "databricks" {
  name                = "databricksecommerceete"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "trial"

  tags = {
    Environment = "Development"
    Project     = "Ecommerce-ETE"
  }
}

# Access Connector for Azure Databricks
resource "azurerm_databricks_access_connector" "databricks_connector" {
  name                = "databricks-ecommerceete-conn"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = "Development"
    Project     = "Ecommerce-ETE"
  }
}

# Role Assignment - Grant Databricks Access Connector access to Storage Account
resource "azurerm_role_assignment" "databricks_storage_blob_data_contributor" {
  scope                = azurerm_storage_account.storage.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_databricks_access_connector.databricks_connector.identity[0].principal_id
}

# ---------------------------------------
# CDC configuration (JSON watermark)
# ---------------------------------------

# List of table names (folder names)
locals {
  tables = [
    "DimCustomer",
    "DimProduct",
    "DimSeller",
    "FactOrder"
  ]
}

# Create main folder for each table
resource "azurerm_storage_data_lake_gen2_path" "table_folder" {
  for_each = toset(local.tables)

  path                = each.key
  filesystem_name     = azurerm_storage_container.bronze.name
  storage_account_id  = azurerm_storage_account.storage.id
  resource            = "directory"
}

# Create cdc subfolder under each table folder
resource "azurerm_storage_data_lake_gen2_path" "cdc_subfolder" {
  for_each = toset(local.tables)

  path                = "${each.key}/cdc"
  filesystem_name     = azurerm_storage_container.bronze.name
  storage_account_id  = azurerm_storage_account.storage.id
  resource            = "directory"

  depends_on = [azurerm_storage_data_lake_gen2_path.table_folder]
}

# Create cdc.json inside the cdc subfolder
resource "azurerm_storage_data_lake_gen2_path" "cdc_file" {
  for_each = toset(local.tables)

  path                = "${each.key}/cdc/cdc.json"
  filesystem_name     = azurerm_storage_container.bronze.name
  storage_account_id  = azurerm_storage_account.storage.id
  resource            = "file"

  content = jsonencode({
    cdc = "1900-01-01"
  })

  depends_on = [azurerm_storage_data_lake_gen2_path.cdc_subfolder]
}

# Create empty.json inside the cdc subfolder
resource "azurerm_storage_data_lake_gen2_path" "empty_file" {
  for_each = toset(local.tables)

  path                = "${each.key}/cdc/empty.json"
  filesystem_name     = azurerm_storage_container.bronze.name
  storage_account_id  = azurerm_storage_account.storage.id
  resource            = "file"

  content = jsonencode({})

  depends_on = [azurerm_storage_data_lake_gen2_path.cdc_subfolder]
}