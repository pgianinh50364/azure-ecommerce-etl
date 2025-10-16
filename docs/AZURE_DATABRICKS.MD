# Azure Databricks

This project leverages Azure Databricks for data transformation and building the lakehouse architecture.

## Key Features

### 1. Auto Loader for Incremental Ingestion

The pipeline uses Databricks Auto Loader for efficient streaming data ingestion:

- Automatically detects and processes new files as they arrive in ADLS Gen2
- Handles schema evolution and inference
- Provides exactly-once processing guarantees
- Reduces costs by processing only new data

### 2. Lakeflow Declarative Pipeline with SCD

Implements Slowly Changing Dimensions using Lakeflow:

- **SCD Type I**: Overwrites historical data with current values
- **SCD Type II**: Maintains full history by creating new records for changes
- Declarative approach simplifies complex transformations
- Built-in checkpointing and recovery mechanisms

### 3. Metadata-Driven Views with Jinja Templates

Dynamic view generation for business and analytical layers:

- Uses Jinja templates for code generation
- Metadata-driven approach reduces manual coding
- Creates both business-level and analytical views
- Easy to maintain and extend as requirements change

### 4. Databricks Asset Bundle for CI/CD

Modern deployment approach using Databricks Asset Bundles:

- Version-controlled infrastructure and code
- Automated deployment across environments (dev, staging, prod)
- Consistent configuration management
- Streamlined collaboration and testing workflows