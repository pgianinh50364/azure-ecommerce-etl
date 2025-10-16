# Databricks notebook source
# MAGIC %md
# MAGIC ## Bronze Ingestion

# COMMAND ----------

from pyspark.sql.functions import col, current_timestamp, to_timestamp, lit
from pyspark.sql.types import *

# Azure Data Lake Storage Gen2 paths
BRONZE_CONTAINER = "abfss://bronze@storageecommerceete.dfs.core.windows.net"
SILVER_CONTAINER = "abfss://silver@storageecommerceete.dfs.core.windows.net"

# Table names matching folder structure
TABLE_NAMES = [
    "DimCustomer",
    "DimProduct",
    "DimSeller",
    "DimDate",
    "FactOrder",
    "FactOrderItem"
]


# COMMAND ----------

# Path templates
def get_bronze_data_path(table_name):
    return f"{BRONZE_CONTAINER}/{table_name}/data"

def get_silver_checkpoint_path(table_name):
    return f"{SILVER_CONTAINER}/{table_name}/checkpoint"

def get_silver_schema_path(table_name):
    return f"{SILVER_CONTAINER}/{table_name}/schema"

def get_silver_table_path(table_name):
    return f"{SILVER_CONTAINER}/{table_name}/data"

# COMMAND ----------

# MAGIC %md
# MAGIC ### DimCustomer

# COMMAND ----------

dim_customer = (
    spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "parquet")
        .option("cloudFiles.schemaLocation", get_silver_schema_path("DimCustomer"))
        .load(get_bronze_data_path("DimCustomer"))
        .select(
            col("customer_id"),
            col("customer_unique_id"),
            col("customer_zip_code_prefix"),
            col("customer_city"),
            col("customer_state"),
            to_timestamp(col("updated_at")).alias("updated_at"),
            current_timestamp().alias("ingestion_timestamp")
        )
)

# COMMAND ----------

dim_customer.writeStream \
    .format("delta") \
    .option("checkpointLocation", get_silver_checkpoint_path("DimCustomer")) \
    .trigger(once=True) \
    .outputMode("append") \
    .option("path", get_silver_table_path("DimCustomer")) \
    .toTable("ecommerce.silver.DimCustomer")

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ### DimProduct

# COMMAND ----------

dim_product = (
    spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "parquet")
        .option("cloudFiles.schemaLocation", get_silver_schema_path("DimProduct"))
        .load(get_bronze_data_path("DimProduct"))
        .select(
            col("product_id"),
            col("product_category_name"),
            col("product_name_length").cast("int"),
            col("product_description_length").cast("int"),
            col("product_photos_qty").cast("int"),
            col("product_weight_g").cast("int"),
            col("product_length_cm").cast("int"),
            col("product_height_cm").cast("int"),
            col("product_width_cm").cast("int"),
            to_timestamp(col("updated_at")).alias("updated_at"),
            current_timestamp().alias("ingestion_timestamp")
        )
)

# COMMAND ----------

dim_product.writeStream \
    .format("delta") \
    .option("checkpointLocation", get_silver_checkpoint_path("DimProduct")) \
    .trigger(once=True) \
    .outputMode("append") \
    .option("path", get_silver_table_path("DimProduct")) \
    .toTable("ecommerce.silver.DimProduct")

# COMMAND ----------

# MAGIC %md
# MAGIC ### DimSeller

# COMMAND ----------

dim_seller = (
    spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "parquet")
        .option("cloudFiles.schemaLocation", get_silver_schema_path("DimSeller"))
        .option("cloudFiles.inferColumnTypes", "true")
        .load(get_bronze_data_path("DimSeller"))
        .select(
            col("seller_id"),
            col("seller_zip_code_prefix"),
            col("seller_city"),
            col("seller_state"),
            to_timestamp(col("updated_at")).alias("updated_at"),
            current_timestamp().alias("ingestion_timestamp")
    )
)

# COMMAND ----------

dim_seller.writeStream \
    .format("delta") \
    .option("checkpointLocation", get_silver_checkpoint_path("DimSeller")) \
    .trigger(once=True) \
    .outputMode("append") \
    .option("path", get_silver_table_path("DimSeller")) \
    .toTable("ecommerce.silver.DimSeller")

# COMMAND ----------

# MAGIC %md
# MAGIC ### FactOrder

# COMMAND ----------

fact_order= (
    spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "parquet")
        .option("cloudFiles.schemaLocation", get_silver_schema_path("FactOrder"))
        .option("cloudFiles.inferColumnTypes", "true")
        .load(get_bronze_data_path("FactOrder"))
        .select(
            col("order_id"),
            col("customer_id"),
            col("order_status"),
            to_timestamp(col("order_purchase_timestamp")).alias("order_purchase_timestamp"),
            to_timestamp(col("order_approved_at")).alias("order_approved_at"),
            to_timestamp(col("order_delivered_carrier_date")).alias("order_delivered_carrier_date"),
            to_timestamp(col("order_delivered_customer_date")).alias("order_delivered_customer_date"),
            to_timestamp(col("order_estimated_delivery_date")).alias("order_estimated_delivery_date"),
            col("total_payment_value").cast("decimal(10,2)"),
            col("payment_type"),
            current_timestamp().alias("ingestion_timestamp")
        )
)

# COMMAND ----------

fact_order.writeStream \
    .format("delta") \
    .option("checkpointLocation", get_silver_checkpoint_path("FactOrder")) \
    .trigger(once=True) \
    .outputMode("append") \
    .option("path", get_silver_table_path("FactOrder")) \
    .toTable("ecommerce.silver.FactOrder")

# COMMAND ----------

# MAGIC %md
# MAGIC ### FactOrderItem

# COMMAND ----------

fact_order_item = (
    spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "parquet")
        .option("cloudFiles.schemaLocation", get_silver_schema_path("FactOrderItem"))
        .option("cloudFiles.inferColumnTypes", "true")
        .load(get_bronze_data_path("FactOrderItem"))
        .select(
            col("order_item_id").cast("long"),
            col("order_id"),
            col("order_item_seq").cast("int"),
            col("product_id"),
            col("seller_id"),
            to_timestamp(col("shipping_limit_date")).alias("shipping_limit_date"),
            col("price").cast("decimal(10,2)"),
            col("freight_value").cast("decimal(10,2)"),
            current_timestamp().alias("ingestion_timestamp")
        )
)


# COMMAND ----------

fact_order_item.writeStream \
    .format("delta") \
    .option("checkpointLocation", get_silver_checkpoint_path("FactOrderItem")) \
    .trigger(once=True) \
    .outputMode("append") \
    .option("path", get_silver_table_path("FactOrderItem")) \
    .toTable("ecommerce.silver.FactOrderItem")