
# VeriQuery — PostgreSQL Setup and Data Loading

## 1. Database Environment

- Database: `veriquery`
- PostgreSQL version: 18.6
- Python PostgreSQL driver: Psycopg 3.3.8
- Python environment: `veriquery`
- Database owner: `postgres`
- Loading role: `veriquery_loader`

## 2. Database Schema

Main table: `public.retail_transactions`

The table contains nine original consolidated dataset columns and one generated technical primary key.

| Column | PostgreSQL type | Nullable |
|---|---|---|
| record_id | BIGINT IDENTITY | No |
| invoice | TEXT | No |
| stock_code | TEXT | No |
| description | TEXT | Yes |
| quantity | INTEGER | No |
| invoice_date | TIMESTAMP WITHOUT TIME ZONE | No |
| price | NUMERIC(12,3) | No |
| customer_id | BIGINT | Yes |
| country | TEXT | No |
| source_sheet | TEXT | No |

Primary key: `record_id`.

Constraint: `source_sheet` accepts only the two original worksheet names.

The generated record ID is a technical database identifier, not an original invoice-line identifier.

## 3. Data Loading

Source:
`data/processed/online_retail_II_consolidated.csv`

Loader:
`scripts/database/01_load_retail_transactions.py`

Loading method: PostgreSQL COPY through Psycopg 3.

The loader:
- Maps all nine CSV columns explicitly.
- Leaves record_id generation to PostgreSQL.
- Preserves missing descriptions and customer IDs as SQL NULL.
- Refuses to load into a non-empty target table.
- Uses transaction handling and rolls back on failure.
- Checks the expected row count.

Expected records: 1,044,848.

Actual records inserted: 1,044,848.

## 4. Database Validation Results

| Validation | Result |
|---|---:|
| Total records | 1,044,848 |
| Missing descriptions | 4,275 |
| Missing customer IDs | 235,287 |
| Missing values in other columns | 0 |
| Year 2009-2010 records | 525,461 |
| Year 2010-2011 records | 519,387 |
| Minimum quantity | -80,995 |
| Maximum quantity | 80,995 |
| Minimum price | -53,594.360 |
| Maximum price | 38,970.000 |
| Negative quantities | 22,557 |
| Negative prices | 5 |
| Unique record IDs | 1,044,848 |

All executed validation queries matched the expected results.

These checks validate row counts, NULL counts, source distribution, selected numeric statistics, and primary-key uniqueness. They do not constitute a complete cell-by-cell comparison against the source CSV.

## 5. Design Decisions

- One main transaction table is used.
- Original invoice and StockCode values are stored as text.
- Customer ID and Description allow NULL.
- Negative quantities and prices are preserved.
- Exact repeated observations are not removed during loading.
- No unsupported product, customer, or invoice relationships are assumed.
- No revenue formula is introduced.

## 6. Known Environment Note

PostgreSQL reported a collation version mismatch for the existing `postgres` database (2.42 versus operating-system version 2.43). The warning did not prevent VeriQuery database creation, schema creation, or data loading. It remains a separate environment maintenance item.

## 7. Implementation Artifacts

- `sql/schema/01_create_retail_transactions.sql`
- `scripts/database/01_load_retail_transactions.py`
- `scripts/inspection/09_postgres_type_profile.py`
- `reports/data_quality/dataset_contract.md`
- `reports/database/postgresql_setup_and_loading.md`
