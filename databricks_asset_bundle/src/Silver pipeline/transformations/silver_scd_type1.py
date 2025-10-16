import dlt
from pyspark.sql.functions import col, current_timestamp, to_timestamp, lit
from pyspark.sql.types import *

# ====================================
# Silver Layer - Cleaned with CDC
# ====================================

@dlt.table(
    name = "dim_customer_stg"
)
def dim_customer_stg():
    return (
        dlt.read_stream("ecommerce.silver.dimcustomer")
    )

dlt.create_streaming_table(
    name="silver_dim_customer",
    table_properties={
        "quality": "silver",
        "delta.enableChangeDataFeed": "true",
    }
)

dlt.create_auto_cdc_flow(
    target="silver_dim_customer",
    source="dim_customer_stg",
    keys=["customer_id"],
    sequence_by=col("updated_at"),
    apply_as_deletes=None,
    except_column_list=["ingestion_timestamp"],
    stored_as_scd_type=2
)

@dlt.table(
    name = "dim_product_stg"
)
def dim_product_stg():
    return (
        dlt.read_stream("ecommerce.silver.dimproduct")
    )

dlt.create_streaming_table(
    name="silver_dim_product",
    table_properties={
        "quality": "silver",
        "delta.enableChangeDataFeed": "true",
        "pipelines.autoOptimize.zOrderCols": "product_id"
    }
)

dlt.create_auto_cdc_flow(
    target="silver_dim_product",
    source="dim_product_stg",
    keys=["product_id"],
    sequence_by=col("updated_at"),
    apply_as_deletes=None,
    except_column_list=["ingestion_timestamp"],
    stored_as_scd_type=2
)

@dlt.table(
    name = "dim_seller_stg"
)
def dim_seller_stg():
    return (
        dlt.read_stream("ecommerce.silver.dimseller")
    )

dlt.create_streaming_table(
    name="silver_dim_seller",
    table_properties={
        "quality": "silver",
        "delta.enableChangeDataFeed": "true",
        "pipelines.autoOptimize.zOrderCols": "seller_id"
    }
)

dlt.create_auto_cdc_flow(
    target="silver_dim_seller",
    source="dim_seller_stg",
    keys=["seller_id"],
    sequence_by=col("updated_at"),
    apply_as_deletes=None,
    except_column_list=["ingestion_timestamp"],
    stored_as_scd_type=2
)

@dlt.table(
    name = "fact_order_stg"
)
def fact_order_stg():
    return (
        dlt.read_stream("ecommerce.silver.factorder")
    )

dlt.create_streaming_table(
    name="silver_fact_order",
    table_properties={
        "quality": "silver",
        "delta.enableChangeDataFeed": "true",
        "pipelines.autoOptimize.zOrderCols": "order_id"
    }
)

dlt.create_auto_cdc_flow(
    target="silver_fact_order",
    source="fact_order_stg",
    keys=["order_id"],
    sequence_by=col("order_approved_at"),
    apply_as_deletes=None,
    except_column_list=["ingestion_timestamp"],
    stored_as_scd_type=2
)

@dlt.table(
    name="silver_fact_order_item",
    comment="Order item fact - append only - saved to silver container",
    table_properties={
        "quality": "silver",
        "delta.enableChangeDataFeed": "true"
    }
)
@dlt.expect_or_drop("valid_order_item", "order_item_id IS NOT NULL")
@dlt.expect_or_drop("valid_price", "price >= 0")
def silver_fact_order_item():
    """
    Silver layer: Clean order item data (append-only)
    """
    return (
        dlt.read_stream("ecommerce.silver.factorderitem")
        .select([c for c in dlt.read_stream("ecommerce.silver.factorderitem").columns 
                 if c != "ingestion_timestamp"])
    )