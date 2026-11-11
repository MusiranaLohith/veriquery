
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INVENTORY_DIR = PROJECT_ROOT / "reports" / "product_inventory"

numeric_path = INVENTORY_DIR / "numeric_stockcodes.csv"
non_numeric_path = INVENTORY_DIR / "non_numeric_stockcodes.csv"

numeric = pd.read_csv(numeric_path, dtype={"stock_code": "string"})
non_numeric = pd.read_csv(non_numeric_path, dtype={"stock_code": "string"})

inventory = pd.concat(
    [numeric, non_numeric],
    ignore_index=True
)

inventory = inventory.sort_values(
    ["transaction_records", "stock_code"],
    ascending=[False, True]
)

output_path = INVENTORY_DIR / "master_stockcode_inventory.csv"
inventory.to_csv(output_path, index=False)

print("COMBINED STOCKCODE INVENTORY")
print("=" * 55)

print(f"Numeric-only codes: {len(numeric):,}")
print(f"Non-numeric codes: {len(non_numeric):,}")
print(f"Combined codes: {len(inventory):,}")

print("\n1. INTEGRITY CHECKS")

print(
    "Unique StockCodes:",
    inventory["stock_code"].nunique()
)

print(
    "Total transaction records:",
    inventory["transaction_records"].sum()
)

print("\n2. DESCRIPTION QUALITY")

print(
    "Codes with no non-null description:",
    (inventory["distinct_non_null_descriptions"] == 0).sum()
)

print(
    "Codes with exactly one description:",
    (inventory["distinct_non_null_descriptions"] == 1).sum()
)

print(
    "Codes with multiple descriptions:",
    (inventory["distinct_non_null_descriptions"] > 1).sum()
)

print("\n3. MISSING DESCRIPTION OBSERVATIONS")

print(
    "Codes affected:",
    (inventory["missing_description_rows"] > 0).sum()
)

print(
    "Total rows with missing descriptions:",
    inventory["missing_description_rows"].sum()
)

print("\n4. TOP 30 STOCKCODES")

print(
    inventory[
        [
            "stock_code",
            "transaction_records",
            "distinct_non_null_descriptions",
            "recorded_descriptions",
        ]
    ].head(30).to_string(index=False)
)

print("\nMaster inventory saved to:")
print(output_path)
