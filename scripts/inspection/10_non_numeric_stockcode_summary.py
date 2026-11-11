
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CSV_PATH = (
    PROJECT_ROOT
    / "reports"
    / "product_inventory"
    / "non_numeric_stockcodes.csv"
)

df = pd.read_csv(CSV_PATH)

print("NON-NUMERIC STOCKCODE INVENTORY")
print("=" * 60)

print(f"Total codes: {len(df):,}")

print("\n1. DESCRIPTION PROFILE")
print(
    df["distinct_non_null_descriptions"]
    .value_counts()
    .sort_index()
    .to_string()
)

print("\n2. CODES WITH MISSING DESCRIPTIONS")
missing = df[df["missing_description_rows"] > 0]

print(f"Codes affected: {len(missing):,}")
print(
    missing[
        [
            "stock_code",
            "transaction_records",
            "distinct_non_null_descriptions",
            "missing_description_rows",
            "recorded_descriptions",
        ]
    ].head(30).to_string(index=False)
)

print("\n3. CODES WITH MULTIPLE DESCRIPTIONS")
multiple = df[df["distinct_non_null_descriptions"] > 1]

print(f"Codes found: {len(multiple):,}")
print(
    multiple[
        [
            "stock_code",
            "transaction_records",
            "distinct_non_null_descriptions",
            "recorded_descriptions",
        ]
    ].head(30).to_string(index=False)
)

print("\n4. MOST FREQUENT NON-NUMERIC CODES")
print(
    df[
        [
            "stock_code",
            "transaction_records",
            "recorded_descriptions",
        ]
    ].head(40).to_string(index=False)
)

print("\nSummary completed.")
