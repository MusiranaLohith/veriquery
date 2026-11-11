from pathlib import Path
import pandas as pd


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "online_retail_II.xlsx"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_PATH = OUTPUT_DIR / "online_retail_II_consolidated.csv"


# --------------------------------------------------
# Load source worksheets
# --------------------------------------------------

sheet_data = pd.read_excel(
    DATASET_PATH,
    sheet_name=None,
    engine="openpyxl"
)

print("Source workbook loaded.")

for sheet_name, df in sheet_data.items():
    print(f"{sheet_name}: {len(df):,} rows")


# --------------------------------------------------
# Add source worksheet information
# --------------------------------------------------

prepared_sheets = []

for sheet_name, df in sheet_data.items():

    prepared_df = df.copy()

    prepared_df["source_sheet"] = sheet_name

    prepared_sheets.append(prepared_df)

    print(
        f"\nPrepared {sheet_name}: "
        f"{len(prepared_df):,} rows"
    )


# --------------------------------------------------
# Compare exact row occurrences across worksheets
# --------------------------------------------------

first_df = prepared_sheets[0].copy()
second_df = prepared_sheets[1].copy()

# Original dataset columns (exclude provenance)
comparison_columns = list(sheet_data.values())[0].columns.tolist()

# Count how many times each exact record appears
# in the first worksheet
first_counts = (
    first_df.groupby(comparison_columns, dropna=False)
    .size()
    .reset_index(name="first_count")
)

# Count how many times each exact record appears
# in the second worksheet
second_counts = (
    second_df.groupby(comparison_columns, dropna=False)
    .size()
    .reset_index(name="second_count")
)

# Compare the occurrence counts
frequency_comparison = first_counts.merge(
    second_counts,
    on=comparison_columns,
    how="inner"
)

# 1. Check whether shared records have matching occurrence counts
frequency_mismatches = frequency_comparison[
    frequency_comparison["first_count"] != frequency_comparison["second_count"]
]

if not frequency_mismatches.empty:
    raise ValueError(
        "Cross-sheet occurrence frequencies do not match. "
        "Consolidation stopped to prevent accidental data loss."
    )

print("Cross-sheet frequency equality: PASSED")


# Calculate how many occurrences are shared
frequency_comparison["shared_count"] = (
    frequency_comparison[
        ["first_count", "second_count"]
    ].min(axis=1)
)

shared_occurrences = int(
    frequency_comparison["shared_count"].sum()
)

print("\nCross-sheet overlap verification")
print("--------------------------------")
print(
    "Unique exact records in both worksheets:",
    len(frequency_comparison)
)
print(
    "Shared row occurrences:",
    shared_occurrences
)

print(
    "Additional occurrences in first worksheet:",
    int(
        (
            frequency_comparison["first_count"]
            - frequency_comparison["shared_count"]
        ).sum()
    )
)

print(
    "Additional occurrences in second worksheet:",
    int(
        (
            frequency_comparison["second_count"]
            - frequency_comparison["shared_count"]
        ).sum()
    )
)


# --------------------------------------------------
# Construct consolidated dataset
# --------------------------------------------------

# First worksheet is retained in full.
consolidated_first = first_df.copy()

# Second worksheet has no additional occurrences
# for records shared with the first worksheet.
# Therefore, retain only records absent from
# the first worksheet.

second_only = second_counts.merge(
    first_counts[comparison_columns],
    on=comparison_columns,
    how="left",
    indicator=True
)

second_only_records = second_only[
    second_only["_merge"] == "left_only"
][comparison_columns]

# Keep source-sheet provenance when filtering.
second_consolidated = second_df.merge(
    second_only_records,
    on=comparison_columns,
    how="inner"
)

# Combine both parts.
consolidated_df = pd.concat(
    [consolidated_first, second_consolidated],
    ignore_index=True
)

print("\nConsolidation results")
print("---------------------")
print(f"First worksheet rows: {len(first_df):,}")
print(f"Second worksheet rows: {len(second_df):,}")
print(f"Shared occurrences removed: {shared_occurrences:,}")
print(f"Second worksheet rows retained: {len(second_consolidated):,}")
print(f"Consolidated rows: {len(consolidated_df):,}")


# --------------------------------------------------
# Validate consolidated dataset
# --------------------------------------------------

print("\nConsolidated dataset validation")
print("--------------------------------")

# 1. Total row count
expected_rows = (
    len(first_df)
    + len(second_df)
    - shared_occurrences
)

assert len(consolidated_df) == expected_rows

print("Total row count: PASSED")

# 2. Source worksheet provenance
provenance_counts = (
    consolidated_df["source_sheet"]
    .value_counts()
)

print("\nRows by source worksheet:")
print(provenance_counts.to_string())

assert provenance_counts["Year 2009-2010"] == 525461
assert provenance_counts["Year 2010-2011"] == 519387

print("\nSource provenance: PASSED")

# 3. Missing provenance
assert consolidated_df["source_sheet"].notna().all()

print("Missing provenance: 0")
print("Provenance validation: PASSED")

# 4. Original columns preserved
assert all(
    column in consolidated_df.columns
    for column in comparison_columns
)

print("Original columns preserved: PASSED")

print("\nAll consolidation validations passed.")


# --------------------------------------------------
# Save consolidated dataset
# --------------------------------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

consolidated_df.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8"
)

print("\nConsolidated dataset saved successfully.")
print(f"Output path: {OUTPUT_PATH}")
print(f"Final rows: {len(consolidated_df):,}")
print(f"Final columns: {len(consolidated_df.columns)}")
