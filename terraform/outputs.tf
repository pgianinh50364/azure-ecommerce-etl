# Outputs for easy reference after deployment

output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.rg.name
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.storage.name
}

output "storage_account_primary_dfs_endpoint" {
  description = "Primary DFS endpoint for ADLS Gen2"
  value       = azurerm_storage_account.storage.primary_dfs_endpoint
}

output "data_factory_name" {
  description = "Name of the Data Factory"
  value       = azurerm_data_factory.df.name
}

output "sql_server_name" {
  description = "Name of the SQL Server"
  value       = azurerm_mssql_server.sql_server.name
}

output "sql_server_fqdn" {
  description = "Fully qualified domain name of the SQL Server"
  value       = azurerm_mssql_server.sql_server.fully_qualified_domain_name
}

output "sql_database_name" {
  description = "Name of the SQL Database"
  value       = azurerm_mssql_database.sql_db.name
}

output "databricks_workspace_url" {
  description = "URL of the Databricks workspace"
  value       = azurerm_databricks_workspace.databricks.workspace_url
}

output "databricks_workspace_id" {
  description = "ID of the Databricks workspace"
  value       = azurerm_databricks_workspace.databricks.workspace_id
}

output "databricks_access_connector_id" {
  description = "ID of the Databricks Access Connector"
  value       = azurerm_databricks_access_connector.databricks_connector.id
}

output "databricks_access_connector_principal_id" {
  description = "Principal ID of the Databricks Access Connector"
  value       = azurerm_databricks_access_connector.databricks_connector.identity[0].principal_id
}
