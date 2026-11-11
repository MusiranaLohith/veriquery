from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "online_retail_II_consolidated.csv"
)

# --------------------------------------------------
# Load saved consolidated CSV
# --------------------------------------------------

df = pd.read_csv(
    CSV_PATH,
    parse_dates=["InvoiceDate"],
    low_memory=False
)

print("Consolidated CSV loaded successfully.")

# --------------------------------------------------
# Validate dimensions
# --------------------------------------------------

assert len(df) == 1_044_848
assert len(df.columns) == 9

print("Row count: PASSED")
print("Column count: PASSED")

# --------------------------------------------------
# Validate source provenance
# --------------------------------------------------

counts = df["source_sheet"].value_counts()

assert counts["Year 2009-2010"] == 525_461
assert counts["Year 2010-2011"] == 519_387

assert df["source_sheet"].notna().all()

print("Source provenance: PASSED")

# --------------------------------------------------
# Validate original columns
# --------------------------------------------------

expected_columns = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
    "source_sheet",
]

assert df.columns.tolist() == expected_columns

print("Column structure: PASSED")

# --------------------------------------------------
# Final summary
# --------------------------------------------------

print("\nSaved CSV validation summary")
print("----------------------------")
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")

print("\nColumn data types:")
print(df.dtypes)

print("\nAll saved CSV validations passed.")