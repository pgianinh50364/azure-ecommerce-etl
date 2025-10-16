# Databricks notebook source
from pyspark.sql import SparkSession
from jinja2 import Template
import json

# COMMAND ----------

gold_metadata = {
    "storage_account": "storageecommerceete",
    "silver_container": "silver",
    "gold_container": "gold",
    "target_catalog": "ecommerce",
    "target_schema": "gold",
    
    "tables": [
        {
            "name": "fact_sales_summary",
            "type": "fact",
            "source_tables": ["ecommerce.silver.factorder", "ecommerce.silver.factorderitem", "ecommerce.silver.dimproduct", "ecommerce.silver.dimcustomer"],
            "joins": [
                {"left": "ecommerce.silver.factorder", "right": "ecommerce.silver.factorderitem", "on": "order_id", "type": "inner"},
                {"left": "ecommerce.silver.factorderitem", "right": "ecommerce.silver.dimproduct", "on": "product_id", "type": "left"},
                {"left": "ecommerce.silver.factorder", "right": "ecommerce.silver.dimcustomer", "on": "customer_id", "type": "left"}
            ],
            "select_columns": [
                "o.order_id",
                "o.customer_id",
                "c.customer_city",
                "c.customer_state",
                "TO_DATE(o.order_purchase_timestamp) as order_date",
                "oi.product_id",
                "p.product_category_name",
                "oi.price",
                "oi.freight_value",
                "(oi.price + oi.freight_value) as total_amount"
            ],
            "table_aliases": {
                "ecommerce.silver.factorder": "o",
                "ecommerce.silver.factorderitem": "oi",
                "ecommerce.silver.dimproduct": "p",
                "ecommerce.silver.dimcustomer": "c"
            },
            "partition_by": ["order_date"],
            "z_order_by": ["customer_id", "product_id"],
            "quality": "gold"
        },
        {
            "name": "dim_customer_enriched",
            "type": "dimension",
            "source_tables": ["ecommerce.silver.dimcustomer", "ecommerce.silver.factorder"],
            "joins": [
                {"left": "ecommerce.silver.dimcustomer", "right": "ecommerce.silver.factorder", "on": "customer_id", "type": "left"}
            ],
            "select_columns": [
                "c.customer_id",
                "c.customer_unique_id",
                "c.customer_zip_code_prefix",
                "c.customer_city",
                "c.customer_state",
                "COUNT(o.order_id) as total_orders",
                "MAX(o.order_purchase_timestamp) as last_order_date"
            ],
            "table_aliases": {
                "ecommerce.silver.dimcustomer": "c",
                "ecommerce.silver.factorder": "o"
            },
            "group_by": [
                "c.customer_id",
                "c.customer_unique_id",
                "c.customer_zip_code_prefix",
                "c.customer_city",
                "c.customer_state"
            ],
            "partition_by": ["customer_state"],
            "z_order_by": ["customer_id"],
            "quality": "gold"
        },
        {
            "name": "agg_daily_sales",
            "type": "aggregate",
            "source_tables": ["ecommerce.silver.factorder", "ecommerce.silver.factorderitem"],
            "joins": [
                {"left": "ecommerce.silver.factorder", "right": "ecommerce.silver.factorderitem", "on": "order_id", "type": "inner"}
            ],
            "select_columns": [
                "TO_DATE(o.order_purchase_timestamp) as sale_date",
                "COUNT(DISTINCT o.order_id) as total_orders",
                "COUNT(oi.order_item_id) as total_items",
                "SUM(oi.price) as total_revenue",
                "SUM(oi.freight_value) as total_freight",
                "AVG(oi.price) as avg_item_price"
            ],
            "table_aliases": {
                "ecommerce.silver.factorder": "o",
                "ecommerce.silver.factorderitem": "oi"
            },
            "group_by": ["TO_DATE(o.order_purchase_timestamp)"],
            "partition_by": ["sale_date"],
            "quality": "gold"
        },
        {
            "name": "agg_product_performance",
            "type": "aggregate",
            "source_tables": ["ecommerce.silver.factorderitem", "ecommerce.silver.dimproduct"],
            "joins": [
                {"left": "ecommerce.silver.factorderitem", "right": "ecommerce.silver.dimproduct", "on": "product_id", "type": "left"}
            ],
            "select_columns": [
                "oi.product_id",
                "p.product_category_name",
                "COUNT(oi.order_item_id) as total_units_sold",
                "SUM(oi.price) as total_revenue",
                "AVG(oi.price) as avg_price",
                "MIN(oi.price) as min_price",
                "MAX(oi.price) as max_price"
            ],
            "table_aliases": {
                "ecommerce.silver.factorderitem": "oi",
                "ecommerce.silver.dimproduct": "p"
            },
            "group_by": [
                "oi.product_id",
                "p.product_category_name"
            ],
            "partition_by": ["product_category_name"],
            "z_order_by": ["product_id"],
            "quality": "gold"
        }
    ]
}


# COMMAND ----------

jinja_template = """
{% for table in tables %}
-- ================================================================
-- {{ table.name | upper }} ({{ table.type | upper }})
-- ================================================================
CREATE OR REPLACE TABLE {{ target_catalog }}.{{ target_schema }}.{{ table.name }}
USING DELTA
{% if table.partition_by -%}
PARTITIONED BY ({{ table.partition_by | join(', ') }})
{% endif -%}
LOCATION 'abfss://{{ gold_container }}@{{ storage_account }}.dfs.core.windows.net/{{ table.name }}'
TBLPROPERTIES (
  'quality' = '{{ table.quality }}',
  'delta.enableChangeDataFeed' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
)
AS
SELECT 
  {%- for col in table.select_columns %}
  {{ col }}{% if not loop.last %},{% endif %}
  {%- endfor %}
FROM {{ table.source_tables[0] }} {{ table.table_aliases[table.source_tables[0]] }}
{%- if table.joins %}
{%- for join in table.joins %}
{{ join.type | upper }} JOIN {{ join.right }} {{ table.table_aliases[join.right] }}
  ON {{ table.table_aliases[join.left] }}.{{ join.on }} = {{ table.table_aliases[join.right] }}.{{ join.on }}
{%- endfor %}
{%- endif %}
{%- if table.group_by %}
GROUP BY 
  {%- for col in table.group_by %}
  {{ col }}{% if not loop.last %},{% endif %}
  {%- endfor %}
{%- endif %};

{% if table.z_order_by -%}
-- Optimize and Z-Order
OPTIMIZE {{ target_catalog }}.{{ target_schema }}.{{ table.name }}
ZORDER BY ({{ table.z_order_by | join(', ') }});
{% endif %}

{% endfor %}
"""

# COMMAND ----------

template = Template(jinja_template)
generated_sql = template.render(
    tables=gold_metadata["tables"],
    storage_account=gold_metadata["storage_account"],
    silver_container=gold_metadata["silver_container"],
    gold_container=gold_metadata["gold_container"],
    target_catalog=gold_metadata["target_catalog"],
    target_schema=gold_metadata["target_schema"]
)
print(generated_sql)

# COMMAND ----------

# Split and execute each SQL statement separately
sql_statements = [stmt.strip() for stmt in generated_sql.split(';') if stmt.strip()]

for i, sql_stmt in enumerate(sql_statements, 1):
    print(f"\n{'='*60}")
    print(f"Executing statement {i}/{len(sql_statements)}")
    print(f"{'='*60}")
    print(sql_stmt[:100] + "..." if len(sql_stmt) > 100 else sql_stmt)
    spark.sql(sql_stmt)
    print(f"Statement {i} executed successfully")

print(f"\n{'='*60}")
print(f"All {len(sql_statements)} statements executed successfully!")
print(f"{'='*60}")