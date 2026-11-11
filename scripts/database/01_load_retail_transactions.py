
import csv
import getpass
from decimal import Decimal
from pathlib import Path
from datetime import datetime

import psycopg


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "online_retail_II_consolidated.csv"
)

EXPECTED_ROWS = 1_044_848


# --------------------------------------------------
# 2. Database configuration
# --------------------------------------------------

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "dbname": "veriquery",
    "user": "veriquery_loader",
}


# --------------------------------------------------
# 3. Convert CSV values to database-ready values
# --------------------------------------------------

def convert_row(row):
    customer_id = row["Customer ID"].strip()

    if customer_id:
        customer_decimal = Decimal(customer_id)

        if customer_decimal != customer_decimal.to_integral_value():
            raise ValueError(
                f"Non-integral Customer ID found: {customer_id}"
            )

        customer_id = int(customer_decimal)
    else:
        customer_id = None

    description = row["Description"].strip() or None

    return (
        row["Invoice"],
        row["StockCode"],
        description,
        int(row["Quantity"]),
        datetime.fromisoformat(row["InvoiceDate"]),
        Decimal(row["Price"]),
        customer_id,
        row["Country"],
        row["source_sheet"],
    )


# --------------------------------------------------
# 4. Main loading operation
# --------------------------------------------------

def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    password = getpass.getpass(
        "Enter PostgreSQL password for veriquery_loader: "
    )

    print("\nConnecting to PostgreSQL...")

    inserted_rows = 0

    with psycopg.connect(
        **DB_CONFIG,
        password=password,
    ) as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT COUNT(*) FROM retail_transactions"
            )

            existing_rows = cursor.fetchone()[0]

            if existing_rows != 0:
                raise RuntimeError(
                    "Target table is not empty. "
                    "Refusing to load duplicate data."
                )

            copy_sql = """
                COPY retail_transactions (
                    invoice,
                    stock_code,
                    description,
                    quantity,
                    invoice_date,
                    price,
                    customer_id,
                    country,
                    source_sheet
                )
                FROM STDIN
            """

            print("Starting CSV import...")

            with CSV_PATH.open(
                "r",
                encoding="utf-8",
                newline="",
            ) as csv_file:

                reader = csv.DictReader(csv_file)

                if reader.fieldnames != [
                    "Invoice",
                    "StockCode",
                    "Description",
                    "Quantity",
                    "InvoiceDate",
                    "Price",
                    "Customer ID",
                    "Country",
                    "source_sheet",
                ]:
                    raise ValueError(
                        "CSV column structure does not match "
                        "the expected dataset contract."
                    )

                with cursor.copy(copy_sql) as copy:

                    for row in reader:
                        copy.write_row(convert_row(row))
                        inserted_rows += 1

            if inserted_rows != EXPECTED_ROWS:
                raise ValueError(
                    f"Expected {EXPECTED_ROWS:,} rows, "
                    f"but processed {inserted_rows:,}."
                )

            cursor.execute(
                "SELECT COUNT(*) FROM retail_transactions"
            )

            database_rows = cursor.fetchone()[0]

            if database_rows != EXPECTED_ROWS:
                raise ValueError(
                    f"Expected {EXPECTED_ROWS:,} database rows, "
                    f"but found {database_rows:,}."
                )

        # Successful exit commits the transaction.
        # Any exception rolls it back automatically.

    print("\nDATA LOADING COMPLETED SUCCESSFULLY")
    print(f"Rows inserted: {inserted_rows:,}")
    print(f"Rows in database: {database_rows:,}")


if __name__ == "__main__":
    main()
