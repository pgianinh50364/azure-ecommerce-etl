#!/bin/bash

cd terraform 2>/dev/null || cd .
outputs=$(terraform output -json)
cd - >/dev/null 2>&1 || cd ..

resource_group=$(echo $outputs | jq -r '.resource_group_name.value')
storage_account=$(echo $outputs | jq -r '.storage_account_name.value')
storage_dfs_endpoint=$(echo $outputs | jq -r '.storage_account_primary_dfs_endpoint.value')
data_factory=$(echo $outputs | jq -r '.data_factory_name.value')
sql_server_fqdn=$(echo $outputs | jq -r '.sql_server_fqdn.value')
sql_database=$(echo $outputs | jq -r '.sql_database_name.value')
databricks_url=$(echo $outputs | jq -r '.databricks_workspace_url.value')
databricks_id=$(echo $outputs | jq -r '.databricks_workspace_id.value')
databricks_connector_id=$(echo $outputs | jq -r '.databricks_access_connector_id.value')
databricks_connector_principal=$(echo $outputs | jq -r '.databricks_access_connector_principal_id.value')

sql_username=$(grep '^AZURE_SQL_USERNAME=' .env 2>/dev/null | cut -d'=' -f2)
sql_password=$(grep '^AZURE_SQL_PASSWORD=' .env 2>/dev/null | cut -d'=' -f2)
sql_driver=$(grep '^AZURE_SQL_DRIVER=' .env 2>/dev/null | cut -d'=' -f2)
sql_schema=$(grep '^AZURE_SQL_SCHEMA=' .env 2>/dev/null | cut -d'=' -f2)
data_root=$(grep '^DATA_ROOT=' .env 2>/dev/null | cut -d'=' -f2)

[ -z "$sql_username" ] && sql_username="admingia"
[ -z "$sql_password" ] && sql_password="0918620631@Go"
[ -z "$sql_driver" ] && sql_driver="ODBC Driver 17 for SQL Server"
[ -z "$sql_schema" ] && sql_schema="raw"
[ -z "$data_root" ] && data_root="c:\Users\gianinh50365\Desktop\data\cdc_test_data"

cat > .env << EOF
AZURE_RESOURCE_GROUP=$resource_group
AZURE_REGION=Southeast Asia
AZURE_STORAGE_ACCOUNT=$storage_account
AZURE_STORAGE_DFS_ENDPOINT=$storage_dfs_endpoint
AZURE_STORAGE_CONTAINER_BRONZE=bronze
AZURE_STORAGE_CONTAINER_SILVER=silver
AZURE_STORAGE_CONTAINER_GOLD=gold
AZURE_STORAGE_CONTAINER_METASTORE=metastore
AZURE_DATA_FACTORY=$data_factory
AZURE_SQL_SERVER=$sql_server_fqdn
AZURE_SQL_DATABASE=$sql_database
AZURE_SQL_USERNAME=$sql_username
AZURE_SQL_PASSWORD=$sql_password
AZURE_SQL_DRIVER=$sql_driver
AZURE_SQL_SCHEMA=$sql_schema
AZURE_DATABRICKS_WORKSPACE_URL=https://$databricks_url
AZURE_DATABRICKS_WORKSPACE_ID=$databricks_id
AZURE_DATABRICKS_CONNECTOR_ID=$databricks_connector_id
AZURE_DATABRICKS_CONNECTOR_PRINCIPAL_ID=$databricks_connector_principal
DATA_ROOT=$data_root
EOF

echo "Complete!"
