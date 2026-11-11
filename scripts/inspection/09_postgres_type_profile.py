
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT_ROOT / "data" / "processed" / "online_retail_II_consolidated.csv"

print("Loading consolidated dataset...")

df = pd.read_csv(
    CSV_PATH,
    dtype={
        "Invoice": "string",
        "StockCode": "string",
        "Description": "string",
        "Customer ID": "string",
        "Country": "string",
        "source_sheet": "string",
        "Price": "string",
    },
    parse_dates=["InvoiceDate"],
)

print(f"\nRows: {len(df):,}")
print(f"Columns: {len(df.columns)}")

print("\n1. TEXT COLUMN MAXIMUM LENGTHS")
for column in ["Invoice", "StockCode", "Description", "Country", "source_sheet"]:
    print(f"{column}: {df[column].str.len().max()}")

print("\n2. QUANTITY PROFILE")
print(f"Minimum: {df['Quantity'].min()}")
print(f"Maximum: {df['Quantity'].max()}")
print(f"Zero values: {(df['Quantity'] == 0).sum():,}")
print(f"Negative values: {(df['Quantity'] < 0).sum():,}")

print("\n3. PRICE PROFILE")
prices = df["Price"].dropna().map(Decimal)

print(f"Minimum: {min(prices)}")
print(f"Maximum: {max(prices)}")
print(f"Distinct decimal scales: {sorted({max(0, -p.as_tuple().exponent) for p in prices})}")
print(f"Maximum decimal scale: {max(max(0, -p.as_tuple().exponent) for p in prices)}")

print("\n4. CUSTOMER ID PROFILE")
customer_ids = df["Customer ID"].dropna().map(Decimal)

non_integral = [value for value in customer_ids if value != value.to_integral_value()]

print(f"Non-null IDs: {len(customer_ids):,}")
print(f"Null IDs: {df['Customer ID'].isna().sum():,}")
print(f"Non-integral IDs: {len(non_integral):,}")

if customer_ids.size:
    print(f"Minimum ID: {min(customer_ids)}")
    print(f"Maximum ID: {max(customer_ids)}")

print("\n5. DATE PROFILE")
print(f"Minimum: {df['InvoiceDate'].min()}")
print(f"Maximum: {df['InvoiceDate'].max()}")

print("\n6. SOURCE SHEET VALUES")
print(df["source_sheet"].value_counts(dropna=False).to_string())

print("\n7. NULL COUNTS")
print(df.isna().sum().to_string())

print("\nInspection completed.")
