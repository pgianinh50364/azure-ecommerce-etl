# Azure E-Commerce ETL Pipeline

An end-to-end data engineering project implementing a modern lakehouse architecture on Azure, featuring incremental data loading, CDC tracking, and automated transformations using Azure Data Factory and Databricks.

## Project Overview

This project processes Brazilian e-commerce data from Olist through a medallion architecture (Bronze → Silver → Gold) using Azure cloud services. It demonstrates real-world data engineering practices including incremental loading, slowly changing dimensions, and metadata-driven transformations.

### Architecture Components

- **Azure SQL Database**: Source transactional database with CDC-enabled tables
- **Azure Data Factory**: Orchestration layer for incremental data ingestion
- **Azure Data Lake Storage Gen2**: Medallion architecture storage (Bronze, Silver, Gold)
- **Azure Databricks**: Transformation engine with Spark structured streaming
- **Terraform**: Infrastructure as Code for automated deployment

---

## Key Features

### Azure Data Factory

#### 1. Incremental Load with JSON Watermark

The pipeline uses a JSON-based watermark technique to track and load only changed data:

- **Watermark Files**: Each table maintains its own CDC (Change Data Capture) tracking through JSON files
  - `empty.json` - Contains `{}` for initial state
  - `cdc.json` - Stores the last processed timestamp, e.g., `{"cdc":"1900-01-01"}`

- **How it works**:
  - The pipeline queries data where the CDC column is greater than the timestamp in `cdc.json`
  - After loading, two copy activities capture the `max(cdc_date)` and overwrite the `cdc.json` file
  - Each table has its own CDC file for independent tracking (tables without CDC columns are handled differently)

This approach ensures only new or modified records are processed, reducing load times and resource consumption.

#### 2. Backdate Refresh

The pipeline supports custom date inputs for historical data loads:

- Compare a custom input date against the stored `cdc.json` timestamp
- Load data from the specified date range
- Useful for reprocessing historical data or handling data corrections

#### 3. Dynamic Data Loading

The pipeline can dynamically load data from Azure SQL to ADLS Gen2:

- **Single Table Mode**: Use the `data_ingestion` pipeline to load specific tables
- **Bulk Mode**: Use the `ingest_all_table` pipeline to process all tables at once
- Dynamic parameter handling for flexible execution
- Automated schema detection and processing

### Azure Databricks

#### 1. Auto Loader for Incremental Ingestion

The pipeline uses Databricks Auto Loader for efficient streaming data ingestion:

- Automatically detects and processes new files as they arrive in ADLS Gen2
- Handles schema evolution and inference
- Provides exactly-once processing guarantees
- Reduces costs by processing only new data

#### 2. Lakeflow Declarative Pipeline with SCD

Implements Slowly Changing Dimensions using Lakeflow:

- **SCD Type I**: Overwrites historical data with current values
- **SCD Type II**: Maintains full history by creating new records for changes
- Declarative approach simplifies complex transformations
- Built-in checkpointing and recovery mechanisms

#### 3. Metadata-Driven Views with Jinja Templates

Dynamic view generation for business and analytical layers:

- Uses Jinja templates for code generation
- Metadata-driven approach reduces manual coding
- Creates both business-level and analytical views
- Easy to maintain and extend as requirements change

#### 4. Databricks Asset Bundle for CI/CD

Modern deployment approach using Databricks Asset Bundles:

- Version-controlled infrastructure and code
- Automated deployment across environments (dev, staging, prod)
- Consistent configuration management
- Streamlined collaboration and testing workflows

---

## Project Structure

```
azure-ecommerce-etl/
├── terraform/                      # Infrastructure as Code
│   ├── main.tf                    # Main Terraform configuration
│   ├── outputs.tf                 # Output values
│   ├── terraform.tfvars.example   # Example variables
│   └── export_terraform_outputs.sh # Shell script to export outputs
├── azure_df/                       # Azure Data Factory artifacts
│   ├── pipeline/                  # ADF pipelines
│   │   ├── data_ingestion.json   # Single table ingestion
│   │   └── ingest_all_table.json # Bulk table ingestion
│   ├── dataset/                   # Dataset definitions
│   │   ├── azure_sql.json        # SQL source dataset
│   │   ├── parquet_dynamic.json  # Parquet sink dataset
│   │   └── json_dynamic.json     # JSON watermark dataset
│   └── factory/                   # Factory configuration
├── databricks_asset_bundle/        # Databricks deployment bundle
│   ├── databricks.yml             # Bundle configuration
│   ├── src/                       # Transformation notebooks
│   │   ├── silver_dims.py        # Dimension table creation
│   │   ├── jinja_notebook.py     # Template-driven views
│   │   └── Silver pipeline/       # Structured streaming
│   │       └── transformations/   # SCD implementations
│   └── resources/                 # Pipeline definitions
│       └── ecommerce_etl.pipeline.yml
├── cdc_test_data/                  # Sample data and scripts
│   ├── ecommerce_initial_load.sql # Initial data setup
│   ├── ecommerce_incremental_load.sql # CDC test data
│   ├── cdc.json                   # Sample watermark
│   ├── empty.json                 # Empty watermark
│   └── loop_input.json            # Bulk load configuration
└── docs/                           # Documentation
    ├── PROJECT_GUIDE_THROUGH.MD   # Step-by-step setup guide
    ├── DATA_DESCRIPTION.MD        # Dataset documentation
    └── TERRAFORM_GUIDE.md         # Infrastructure deployment guide
```

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Infrastructure** | Terraform | IaC for Azure resources |
| **Source Database** | Azure SQL Database | Transactional data storage |
| **Orchestration** | Azure Data Factory | Data ingestion pipelines |
| **Storage** | Azure Data Lake Gen2 | Medallion architecture storage |
| **Processing** | Azure Databricks | Spark-based transformations |
| **Deployment** | Databricks Asset Bundles | CI/CD for Databricks |
| **Language** | Python, SQL, Jinja2 | Data transformation logic |

---

## Data Model

The project works with four main tables from the Brazilian e-commerce dataset:

- **DimCustomer**: Customer dimension with geographic information
- **DimProduct**: Product dimension with category details
- **DimSeller**: Seller dimension with location data
- **FactOrder**: Fact table containing order transactions with pricing, shipping, and status

For detailed schema information, see [DATA_DESCRIPTION.MD](docs/DATA_DESCRIPTION.MD).

---

## Getting Started

### Prerequisites

- **Azure Subscription**: Active Azure account
- **Azure CLI**: Installed and configured
- **Terraform**: Version ~> 3.0
- **Databricks CLI**: For asset bundle deployment
- **Python**: For running Databricks notebooks locally (optional)

### Quick Start

1. **Deploy Infrastructure**
   ```powershell
   cd terraform
   terraform init
   terraform apply
   ```
   See [TERRAFORM_GUIDE.md](docs/TERRAFORM_GUIDE.md) for detailed instructions.

2. **Load Initial Data**
   - Navigate to Azure SQL Database Query Editor
   - Run `cdc_test_data/ecommerce_initial_load.sql`

3. **Configure Data Factory**
   - Import pipelines from `azure_df/` folder
   - Set up Linked Services for SQL and ADLS Gen2
   - Run `data_ingestion` or `ingest_all_table` pipeline

4. **Deploy Databricks Bundle**
   ```bash
   cd databricks_asset_bundle
   databricks auth login
   databricks bundle deploy --target dev
   ```

5. **Run Transformations**
   - Execute `silver_dims.py` for dimension tables
   - Execute `jinja_notebook.py` for analytical views
   - Configure Lakeflow pipeline for streaming SCD

For step-by-step instructions, see [PROJECT_GUIDE_THROUGH.MD](docs/PROJECT_GUIDE_THROUGH.MD).

---

## Medallion Architecture

### Bronze Layer
- Raw data ingested from Azure SQL
- Parquet format for efficient storage
- CDC watermark tracking per table

### Silver Layer
- Cleaned and standardized data
- Dimension tables (SCD Type II)
- Data quality checks applied

### Gold Layer
- Business-ready aggregated views
- Analytical models
- Optimized for reporting and BI tools

---

## Configuration

### Terraform Variables

Create `terraform/terraform.tfvars`:
```hcl
sql_admin_login    = "your-username"
sql_admin_password = "your-secure-password"
```

### Databricks Configuration

Update `databricks_asset_bundle/databricks.yml`:
```yaml
workspace:
  host: https://your-workspace.azuredatabricks.net
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
