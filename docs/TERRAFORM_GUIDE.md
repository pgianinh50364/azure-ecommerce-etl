# Terraform Deployment Guide

## Prerequisites

1. **Install Terraform**: Download from [terraform.io](https://www.terraform.io/downloads)
2. **Install Azure CLI**: Download from [Microsoft](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
3. **Azure Subscription**: Active Azure subscription required

## Deployment Steps

### 1. Authenticate with Azure

```powershell
az login
az account set --subscription "Remember to Delete Azure student"
```

### 2. Configure Variables

Create `terraform.tfvars`:

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
sql_admin_login    = "<your-username>"
sql_admin_password = "<your-password>"
```

### 3. Initialize and Deploy

```powershell
terraform init
terraform plan
terraform apply
```

## Export Outputs to .env

### Method 1: Using Script (Bash)

```bash
bash export_terraform_outputs.sh
```

### Method 2: Manual Selection

Export specific values:

```powershell
# SQL Server
terraform output -raw sql_server_fqdn

# Databricks URL
terraform output -raw databricks_workspace_url

# Storage Account
terraform output -raw storage_account_name
```

## Resources Created

| Resource | Name | Configuration |
|----------|------|---------------|
| **Resource Group** | RG-EcommerceETE | Region: Southeast Asia |
| **Storage Account** | storageecommerceete | Type: ADLS Gen2, Tier: Standard, Redundancy: LRS |
| **Containers** | bronze, silver, gold, metastore | Access: Private |
| **Data Factory** | df-ecommerceete | Version: V2 |
| **SQL Server** | sqlecommerceete | Version: 12.0, Auth: SQL + Microsoft Entra |
| **SQL Database** | dbecommerceete | SKU: GP_S_Gen5_1, Min Capacity: 1 vCore, Max Size: 1GB, Auto-pause: 60 min |
| **Databricks Workspace** | databricksecommerceete | SKU: Trial |
| **Databricks Access Connector** | databricks-ecommerceete-conn | Identity: SystemAssigned |
| **Storage Folders** | DimCustomer, DimProduct, DimSeller, FactOrder | Each with cdc subfolder and cdc.json/empty.json files |

## Destroy Resources

```powershell
terraform destroy
```
