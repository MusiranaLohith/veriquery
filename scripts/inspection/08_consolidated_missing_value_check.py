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
# Load consolidated dataset
# --------------------------------------------------

df = pd.read_csv(
    CSV_PATH,
    low_memory=False
)

print("Consolidated dataset loaded.")
print(f"Total rows: {len(df):,}")

# --------------------------------------------------
# Calculate missing values
# --------------------------------------------------

missing_counts = df.isna().sum()

missing_percentages = (
    missing_counts / len(df) * 100
)

missing_summary = pd.DataFrame({
    "missing_count": missing_counts,
    "missing_percentage": missing_percentages
})

print("\nMissing-value summary")
print("---------------------")

print(missing_summary.to_string())

# --------------------------------------------------
# Verify important fields
# --------------------------------------------------

assert missing_counts["Invoice"] == 0
assert missing_counts["StockCode"] == 0
assert missing_counts["Quantity"] == 0
assert missing_counts["InvoiceDate"] == 0
assert missing_counts["Price"] == 0
assert missing_counts["Country"] == 0
assert missing_counts["source_sheet"] == 0

print("\nCritical field missing-value checks: PASSED")

# --------------------------------------------------
# Customer ID and Description relationship
# --------------------------------------------------

print("\nCustomer ID and Description missing-value relationship")
print("------------------------------------------------------")

missing_relationship = pd.crosstab(
    df["Description"].isna(),
    df["Customer ID"].isna()
)

print(missing_relationship)

print("\nAnalysis completed.")