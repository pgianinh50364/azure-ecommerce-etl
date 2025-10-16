# Brazilian E-Commerce Dataset - Data Description

## Dataset Overview

### Source
**Kaggle Dataset:** [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?select=olist_order_payments_dataset.csv)

**Provider:** Olist  
**License:** CC BY-NC-SA 4.0  
**Period:** September 2016 to August 2018  
**Domain:** E-commerce transactions from Brazilian marketplace

---

## Original Dataset Structure

The original dataset consists of **9 CSV files** containing information about 100,000 orders made at the Olist Store in Brazil.

### 1. **olist_orders_dataset.csv**
Core order information tracking the order lifecycle.

| Column | Type | Description |
|--------|------|-------------|
| `order_id` | String | Unique identifier for the order |
| `customer_id` | String | Customer unique identifier |
| `order_status` | String | Order status (delivered, shipped, canceled, etc.) |
| `order_purchase_timestamp` | Datetime | Purchase timestamp |
| `order_approved_at` | Datetime | Payment approval timestamp |
| `order_delivered_carrier_date` | Datetime | Order posting timestamp to carrier |
| `order_delivered_customer_date` | Datetime | Actual order delivery date to customer |
| `order_estimated_delivery_date` | Datetime | Estimated delivery date |

**Total Records:** ~99,441 orders

---

### 2. **olist_order_items_dataset.csv**
Items purchased within each order.

| Column | Type | Description |
|--------|------|-------------|
| `order_id` | String | Order unique identifier |
| `order_item_id` | Integer | Sequential number identifying item within order |
| `product_id` | String | Product unique identifier |
| `seller_id` | String | Seller unique identifier |
| `shipping_limit_date` | Datetime | Seller shipping limit date |
| `price` | Decimal | Item price |
| `freight_value` | Decimal | Item freight value |

**Total Records:** ~112,650 order items

---

### 3. **olist_order_payments_dataset.csv**
Payment information for orders (orders can have multiple payment methods).

| Column | Type | Description |
|--------|------|-------------|
| `order_id` | String | Order unique identifier |
| `payment_sequential` | Integer | Sequential number of payment method used |
| `payment_type` | String | Method of payment (credit_card, boleto, voucher, debit_card) |
| `payment_installments` | Integer | Number of installments |
| `payment_value` | Decimal | Transaction value |

**Total Records:** ~103,886 payment records

---

### 4. **olist_customers_dataset.csv**
Customer information and location.

| Column | Type | Description |
|--------|------|-------------|
| `customer_id` | String | Key to orders dataset (unique identifier) |
| `customer_unique_id` | String | Unique identifier for customer |
| `customer_zip_code_prefix` | Integer | First 5 digits of customer zip code |
| `customer_city` | String | Customer city name |
| `customer_state` | String | Customer state (2-letter code) |

**Total Records:** ~99,441 customers

---

### 5. **olist_products_dataset.csv**
Product information and attributes.

| Column | Type | Description |
|--------|------|-------------|
| `product_id` | String | Product unique identifier |
| `product_category_name` | String | Root category of product (Portuguese) |
| `product_name_lenght` | Integer | Number of characters in product name |
| `product_description_lenght` | Integer | Number of characters in product description |
| `product_photos_qty` | Integer | Number of product photos |
| `product_weight_g` | Integer | Product weight in grams |
| `product_length_cm` | Integer | Product length in centimeters |
| `product_height_cm` | Integer | Product height in centimeters |
| `product_width_cm` | Integer | Product width in centimeters |

**Total Records:** ~32,951 products

---

### 6. **olist_sellers_dataset.csv**
Seller information and location.

| Column | Type | Description |
|--------|------|-------------|
| `seller_id` | String | Seller unique identifier |
| `seller_zip_code_prefix` | Integer | First 5 digits of seller zip code |
| `seller_city` | String | Seller city name |
| `seller_state` | String | Seller state (2-letter code) |

**Total Records:** ~3,095 sellers

---

### 7. **olist_order_reviews_dataset.csv**
Customer reviews and ratings.

| Column | Type | Description |
|--------|------|-------------|
| `review_id` | String | Review unique identifier |
| `order_id` | String | Order unique identifier |
| `review_score` | Integer | Rating score (1-5) |
| `review_comment_title` | String | Review comment title (Portuguese) |
| `review_comment_message` | String | Review comment message (Portuguese) |
| `review_creation_date` | Datetime | Review creation timestamp |
| `review_answer_timestamp` | Datetime | Review answer timestamp |

**Total Records:** ~99,224 reviews

---

### 8. **olist_geolocation_dataset.csv**
Brazilian zip codes with latitude/longitude coordinates.

| Column | Type | Description |
|--------|------|-------------|
| `geolocation_zip_code_prefix` | Integer | First 5 digits of zip code |
| `geolocation_lat` | Decimal | Latitude |
| `geolocation_lng` | Decimal | Longitude |
| `geolocation_city` | String | City name |
| `geolocation_state` | String | State (2-letter code) |

**Total Records:** ~1,000,163 geolocation entries

---

### 9. **product_category_name_translation.csv**
Translation of product category names from Portuguese to English.

| Column | Type | Description |
|--------|------|-------------|
| `product_category_name` | String | Category name in Portuguese |
| `product_category_name_english` | String | Category name in English |

**Total Records:** 71 categories


## Dataset Relationships

![alt text](../assets/data_rel.png)

---

## 🛠️ Modifications for CDC Testing

### Changes Applied for Azure Data Factory + Databricks DLT Pipeline

#### 1. **Data Volume Reduction (Cost Optimization)**

**Original Dataset Size:**
- Orders: ~99,441 rows
- Order Items: ~112,650 rows
- Reviews: ~99,224 rows
- Customers: ~99,441 rows
- Products: ~32,951 rows
- Sellers: ~3,095 rows
- Payments: ~103,886 rows
- **Total: ~550,688 rows**

**Modified Dataset Size:**
The data warehouse has been simplified from the original 8 CSV files to 6 core tables:
- **3 Dimension Tables**: DimCustomer, DimProduct, DimSeller
- **1 Date Dimension**: DimDate
- **2 Fact Tables**: FactOrder, FactOrderItem
- **Total: ~1,100 rows**

**Method:**
- **Date-based sampling** for tables with datetime columns (preserves date distribution)
- **Random sampling** for tables without datetime columns
- Ensures data remains representative while drastically reducing processing costs

---

#### 2. **CDC Strategy for Azure Data Factory**

#### Incremental Load Approach

1. **Dimension Tables (DimCustomer, DimProduct, DimSeller)**:
   - Use `updated_at` column for incremental loads
   - ADF pipeline should use `WHERE updated_at > @LastLoadTimestamp`
   - Implement UPSERT (UPDATE if exists, INSERT if new)

2. **Fact Tables (FactOrder)**:
   - Track changes based on `order_status` and delivery date columns
   - Use watermark on `order_approved_at` or `order_delivered_customer_date`
   - Implement UPSERT to update order status changes

3. **Fact Tables (FactOrderItem)**:
   - Append-only pattern (no updates expected)
   - Use watermark on parent order timestamp

### Key CDC Indicators
- ✅ **Primary CDC Column**: `updated_at` (in all dimension tables)
- ✅ **Order Lifecycle Tracking**: `order_status`, `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`
- ✅ **Location Changes**: Zip code, city, state fields in customer and seller dimensions
- ✅ **Product Attribute Changes**: All product dimension measurements and counts



## 🎯 Use Case: Azure CDC Pipeline Testing

### Objective
Test **Change Data Capture (CDC)** functionality using:
- **Azure Data Factory** (orchestration and data movement)
- **Azure Data Lake Storage Gen2** (data lake storage)
- **Azure Databricks Delta Live Tables** (CDC processing with `create_auto_cdc_flow()`)

### CDC Operations Tested

1. **INSERT (Initial Load)**
   - First batch simulates initial data load
   - Subsequent batches simulate new orders arriving

2. **UPDATE**
   - Order status changes (e.g., "processing" → "delivered")
   - Price adjustments
   - Review score updates

3. **DELETE**
   - Soft deletes with `__END_AT` timestamp
   - Maintains historical records (SCD Type 2)

### Expected Pipeline Flow

```
Azure SQL database
     ↓
Azure Data Factory (Copy Activity)
     ↓
ADLS Gen2 (/bronze/)
     ↓
Databricks DLT Pipeline (CDC)
     ↓
Delta Tables (/silver/ - cleaned data)
     ↓
Delta Tables (/gold/ - business views and analytics)
```

## Data Quality Improvements

### Applied During DLT Processing

1. **Type Casting**
   - String dates → Timestamp
   - Price fields → Decimal(10,2)
   - Integer fields → Int

2. **Data Cleaning**
   - Trim whitespace from text fields
   - Uppercase state codes for consistency
   - Remove null primary keys

3. **Deduplication**
   - Based on primary key columns
   - Latest record wins (by `sequence_by`)

4. **Validation Rules** (DLT Expectations)
   - `order_id IS NOT NULL`
   - `price >= 0`
   - `freight_value >= 0`
   - Valid order status values

---

## 🔑 Primary Keys

| Table | Primary Key(s) |
|-------|---------------|
| Orders | `order_id` |
| Order Items | `order_id`, `order_item_id`, `product_id` |
| Customers | `customer_id` |
| Products | `product_id` |
| Sellers | `seller_id` |

---

## 📊 SCD Type Configuration

| Table | SCD Type | History Tracking |
|-------|----------|------------------|
| Orders | Type 2 | `order_status`, `order_approved_at`, `order_delivered_customer_date` |
| Order Items | Type 1 | No history (always current) |
| Customers | Type 2 | `customer_city`, `customer_state`, `customer_zip_code_prefix` |
| Products | Type 2 | `product_category_name`, `product_weight_g`, dimensions |
| Sellers | Type 2 | `seller_city`, `seller_state`, `seller_zip_code_prefix` |

---

## 📚 References

- **Original Dataset**: [Kaggle - Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

---

**Last Updated**: October 15, 2025  