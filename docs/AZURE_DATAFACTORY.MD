# Azure Data Factory Pipeline

This project uses Azure Data Factory to orchestrate incremental data loading from Azure SQL Database to Azure Data Lake Storage Gen2.

## Key Features

### 1. Incremental Load with JSON Watermark

The pipeline uses a JSON-based watermark technique to track and load only changed data:

- **Watermark Files**: Each table maintains its own CDC (Change Data Capture) tracking through JSON files
  - `empty.json` - Contains `{}` for initial state
  - `cdc.json` - Stores the last processed timestamp, e.g., `{"cdc":"1900-01-01"}`

- **How it works**:
  - The pipeline queries data where the CDC column is greater than the timestamp in `cdc.json`
  - After loading, two copy activities capture the `max(cdc_date)` and overwrite the `cdc.json` file
  - Each table has its own CDC file for independent tracking (tables without CDC columns are handled differently)

This approach ensures only new or modified records are processed, reducing load times and resource consumption.

### 2. Backdate Refresh

The pipeline supports custom date inputs for historical data loads:

- Compare a custom input date against the stored `cdc.json` timestamp
- Load data from the specified date range
- Useful for reprocessing historical data or handling data corrections

### 3. Dynamic Data Loading

The pipeline can dynamically load data from Azure SQL to ADLS Gen2:

- **Single Table Mode**: Use the `data_ingestion` pipeline to load specific tables
- **Bulk Mode**: Use the `ingest_all_table` pipeline to process all tables at once
- Dynamic parameter handling for flexible execution
- Automated schema detection and processing