from pathlib import Path
import json
from datetime import datetime, timezone

import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "online_retail_II.xlsx"
)

REPORT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "data_quality"
    / "duplicate_overlap_analysis.json"
)

# Validate dataset

if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATASET_PATH}"
    )

print("Dataset found:", DATASET_PATH.name)


# Load workbook

excel_file = pd.ExcelFile(
    DATASET_PATH,
    engine="openpyxl"
)

if len(excel_file.sheet_names) != 2:
    raise ValueError(
        f"Expected 2 worksheets, found {len(excel_file.sheet_names)}"
    )

print("\nWorksheets:", excel_file.sheet_names)


# Load both worksheets independently

sheet_data = {}

for sheet_name in excel_file.sheet_names:

    df = pd.read_excel(
        excel_file,
        sheet_name=sheet_name
    )

    sheet_data[sheet_name] = df

    print(f"\n{sheet_name}")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))


# Get both worksheets
sheet_names = excel_file.sheet_names

df_2009 = sheet_data[sheet_names[0]]
df_2010 = sheet_data[sheet_names[1]]


# 1. Date overlap analysis

dates_2009 = set(
    df_2009["InvoiceDate"].dt.date
)

dates_2010 = set(
    df_2010["InvoiceDate"].dt.date
)

common_dates = dates_2009.intersection(dates_2010)

print("\n--- Date Overlap Analysis ---")

print("Dates in first worksheet:", len(dates_2009))
print("Dates in second worksheet:", len(dates_2010))
print("Common dates:", len(common_dates))

if common_dates:
    print("First common date:", min(common_dates))
    print("Last common date:", max(common_dates))


# 2. Invoice overlap analysis

invoices_2009 = set(
    df_2009["Invoice"].dropna().astype(str)
)

invoices_2010 = set(
    df_2010["Invoice"].dropna().astype(str)
)

common_invoices = invoices_2009.intersection(invoices_2010)

print("\n--- Invoice Overlap Analysis ---")

print("Unique invoices in first worksheet:", len(invoices_2009))
print("Unique invoices in second worksheet:", len(invoices_2010))
print("Common invoice identifiers:", len(common_invoices))


# 3. Exact cross-sheet transaction row comparison

columns_to_compare = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country"
]

# Compare complete transaction records
common_rows = df_2009.merge(
    df_2010,
    on=columns_to_compare,
    how="inner"
)

print("\n--- Exact Cross-Sheet Row Overlap ---")

print("Matching transaction rows:", len(common_rows))

print(
    "Unique matching transaction records:",
    len(common_rows.drop_duplicates())
)


# 4. Compare exact record frequencies across worksheets

columns_to_compare = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country"
]

# Count occurrences of each exact record in each worksheet
frequency_2009 = (
    df_2009
    .groupby(columns_to_compare, dropna=False)
    .size()
    .reset_index(name="count_2009")
)

frequency_2010 = (
    df_2010
    .groupby(columns_to_compare, dropna=False)
    .size()
    .reset_index(name="count_2010")
)

# Match records and their occurrence counts
frequency_comparison = frequency_2009.merge(
    frequency_2010,
    on=columns_to_compare,
    how="inner"
)

# Calculate shared and additional occurrences
frequency_comparison["shared_occurrences"] = (
    frequency_comparison[["count_2009", "count_2010"]]
    .min(axis=1)
)

frequency_comparison["extra_in_2009"] = (
    frequency_comparison["count_2009"]
    - frequency_comparison["shared_occurrences"]
)

frequency_comparison["extra_in_2010"] = (
    frequency_comparison["count_2010"]
    - frequency_comparison["shared_occurrences"]
)

print("\n--- Cross-Sheet Frequency Comparison ---")

print(
    "Unique exact records present in both:",
    len(frequency_comparison)
)

print(
    "Shared row occurrences:",
    frequency_comparison["shared_occurrences"].sum()
)

print(
    "Additional occurrences in first worksheet:",
    frequency_comparison["extra_in_2009"].sum()
)

print(
    "Additional occurrences in second worksheet:",
    frequency_comparison["extra_in_2010"].sum()
)

# 5. Within-sheet exact duplicate analysis

print("\n--- Within-Sheet Duplicate Analysis ---")

for sheet_name, df in sheet_data.items():

    duplicate_mask = df.duplicated(
        subset=columns_to_compare,
        keep=False
    )

    duplicate_rows = df[duplicate_mask]

    duplicate_groups = (
        df.groupby(
            columns_to_compare,
            dropna=False
        )
        .size()
    )

    duplicate_groups = duplicate_groups[
        duplicate_groups > 1
    ]

    extra_duplicate_rows = (
        duplicate_groups - 1
    ).sum()

    print(f"\n{sheet_name}")

    print(
        "Rows belonging to duplicate groups:",
        len(duplicate_rows)
    )

    print(
        "Unique duplicate groups:",
        len(duplicate_groups)
    )

    print(
        "Additional repeated rows:",
        int(extra_duplicate_rows)
    )

    print(
        "Maximum occurrences of one exact record:",
        int(duplicate_groups.max())
        if not duplicate_groups.empty
        else 1
    )

# 6. Inspect the most frequently repeated exact records

print("\n--- Top Repeated Transaction Records ---")

for sheet_name, df in sheet_data.items():

    duplicate_groups = (
        df.groupby(
            columns_to_compare,
            dropna=False
        )
        .size()
        .reset_index(name="occurrences")
    )

    duplicate_groups = duplicate_groups[
        duplicate_groups["occurrences"] > 1
    ]

    duplicate_groups = duplicate_groups.sort_values(
        "occurrences",
        ascending=False
    )

    print(f"\n{sheet_name}")

    print(
        duplicate_groups.head(15).to_string(index=False)
    )

# 7. Classify duplicate groups by invoice prefix and quantity sign

print("\n--- Duplicate Group Classification ---")

for sheet_name, df in sheet_data.items():

    # Count exact record occurrences
    duplicate_groups = (
        df.groupby(
            columns_to_compare,
            dropna=False
        )
        .size()
        .reset_index(name="occurrences")
    )

    # Keep only records appearing more than once
    duplicate_groups = duplicate_groups[
        duplicate_groups["occurrences"] > 1
    ].copy()

    # Classify invoice identifiers
    invoice_values = (
        duplicate_groups["Invoice"]
        .astype("string")
    )

    duplicate_groups["invoice_type"] = (
        invoice_values.str.startswith("C", na=False)
        .map({
            True: "C-prefixed",
            False: "Other"
        })
    )

    # Classify quantity sign
    duplicate_groups["quantity_type"] = (
        duplicate_groups["Quantity"]
        .apply(
            lambda quantity:
                "Negative" if quantity < 0
                else "Zero" if quantity == 0
                else "Positive"
        )
    )

    # Aggregate duplicate groups
    classification = (
        duplicate_groups
        .groupby(
            ["invoice_type", "quantity_type"]
        )
        .agg(
            duplicate_groups=("occurrences", "size"),
            rows_in_groups=("occurrences", "sum"),
            additional_repeated_rows=(
                "occurrences",
                lambda values: (values - 1).sum()
            ),
            maximum_occurrences=("occurrences", "max")
        )
        .reset_index()
    )

    print(f"\n{sheet_name}")
    print(classification.to_string(index=False))

# 8. Build and save the duplicate/overlap report

duplicate_report = {
    "source_file": DATASET_PATH.name,
    "analysis_timestamp_utc": datetime.now(timezone.utc).isoformat(),

    "date_overlap": {
        "dates_in_first_sheet": len(dates_2009),
        "dates_in_second_sheet": len(dates_2010),
        "common_dates_count": len(common_dates),
        "common_dates": [
            date.isoformat()
            for date in sorted(common_dates)
        ]
    },

    "invoice_overlap": {
        "unique_invoices_first_sheet": len(invoices_2009),
        "unique_invoices_second_sheet": len(invoices_2010),
        "common_invoice_identifiers": len(common_invoices)
    },

    "cross_sheet_exact_overlap": {
        "unique_matching_records": len(frequency_comparison),
        "shared_row_occurrences": int(
            frequency_comparison["shared_occurrences"].sum()
        ),
        "additional_occurrences_first_sheet": int(
            frequency_comparison["extra_in_2009"].sum()
        ),
        "additional_occurrences_second_sheet": int(
            frequency_comparison["extra_in_2010"].sum()
        )
    },

    "within_sheet_duplicates": {}
}


# Recalculate and store within-sheet duplicate statistics

for sheet_name, df in sheet_data.items():

    duplicate_groups = (
        df.groupby(
            columns_to_compare,
            dropna=False
        )
        .size()
    )

    duplicate_groups = duplicate_groups[
        duplicate_groups > 1
    ]

    duplicate_report["within_sheet_duplicates"][sheet_name] = {
        "rows_belonging_to_duplicate_groups": int(
            (duplicate_groups).sum()
        ),
        "unique_duplicate_groups": int(
            len(duplicate_groups)
        ),
        "additional_repeated_rows": int(
            (duplicate_groups - 1).sum()
        ),
        "maximum_occurrences": int(
            duplicate_groups.max()
        ) if not duplicate_groups.empty else 1
    }


# Recalculate and store duplicate classifications

duplicate_report["duplicate_classification"] = {}

for sheet_name, df in sheet_data.items():

    groups = (
        df.groupby(
            columns_to_compare,
            dropna=False
        )
        .size()
        .reset_index(name="occurrences")
    )

    groups = groups[
        groups["occurrences"] > 1
    ].copy()

    invoice_values = groups["Invoice"].astype("string")

    groups["invoice_type"] = invoice_values.str.startswith(
        "C",
        na=False
    ).map({
        True: "C-prefixed",
        False: "Other"
    })

    groups["quantity_type"] = groups["Quantity"].apply(
        lambda quantity:
            "Negative" if quantity < 0
            else "Zero" if quantity == 0
            else "Positive"
    )

    classification = (
        groups.groupby(
            ["invoice_type", "quantity_type"]
        )
        .agg(
            duplicate_groups=("occurrences", "size"),
            additional_repeated_rows=(
                "occurrences",
                lambda values: (values - 1).sum()
            )
        )
        .reset_index()
    )

    duplicate_report["duplicate_classification"][sheet_name] = (
        classification.to_dict(orient="records")
    )


# Ensure report directory exists

REPORT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


# Save JSON

with REPORT_PATH.open("w", encoding="utf-8") as file:
    json.dump(
        duplicate_report,
        file,
        indent=4,
        ensure_ascii=False
    )

print("\nDuplicate/overlap report saved:")
print(REPORT_PATH)