from pathlib import Path
import json
from datetime import datetime, timezone

import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"

REPORT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "data_quality"
    / "missing_value_deep_analysis.json"
)


if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATASET_PATH}"
    )

print("Dataset found:", DATASET_PATH.name)


# Open the workbook
excel_file = pd.ExcelFile(DATASET_PATH, engine="openpyxl")

country_analysis = {}

for sheet_name in excel_file.sheet_names:
    df = pd.read_excel(
        excel_file,
        sheet_name=sheet_name
    )

    country_stats = (
        df.groupby("Country")
        .agg(
            total_rows=("Customer ID", "size"),
            missing_customer_ids=("Customer ID", "count")
        )
    )

    # Convert non-missing counts into missing counts
    country_stats["missing_customer_ids"] = (
        country_stats["total_rows"]
        - country_stats["missing_customer_ids"]
    )

    country_stats["missing_percentage"] = (
        country_stats["missing_customer_ids"]
        / country_stats["total_rows"]
        * 100
    )

    country_stats = country_stats.sort_values(
        "missing_customer_ids",
        ascending=False
    )

    country_analysis[sheet_name] = (
        country_stats.reset_index().to_dict(orient="records")
    )

    print(f"\n--- {sheet_name} ---")
    print(country_stats.head(15))





# Investigate missing descriptions by StockCode

stockcode_analysis = {}

# Load both worksheets
all_sheets = []

for sheet_name in excel_file.sheet_names:
    df = pd.read_excel(
        excel_file,
        sheet_name=sheet_name
    )

    df["SourceSheet"] = sheet_name
    all_sheets.append(df)

# Combine worksheets for cross-sheet investigation
combined_df = pd.concat(
    all_sheets,
    ignore_index=True
)

# Rows where Description is missing
missing_description_df = combined_df[
    combined_df["Description"].isna()
]

# Count missing descriptions per StockCode
missing_stockcodes = (
    missing_description_df["StockCode"]
    .value_counts()
)

# Find descriptions available for each StockCode
known_descriptions = (
    combined_df.dropna(subset=["Description"])
    .groupby("StockCode")["Description"]
    .agg(lambda values: sorted(set(values.astype(str))))
)

for stockcode, missing_count in missing_stockcodes.items():

    descriptions = known_descriptions.get(
        stockcode,
        []
    )

    stockcode_analysis[str(stockcode)] = {
        "missing_description_rows": int(missing_count),
        "known_descriptions": descriptions,
        "description_available_elsewhere": len(descriptions) > 0
    }

print("\n--- Missing Description Investigation ---")

for stockcode, details in list(stockcode_analysis.items())[:20]:
    print(f"\nStockCode: {stockcode}")
    print("Missing rows:", details["missing_description_rows"])
    print("Known descriptions:", details["known_descriptions"])
    print(
        "Available elsewhere:",
        details["description_available_elsewhere"]
    )

# Aggregate missing-description findings

total_missing_description_rows = len(missing_description_df)

stockcodes_with_known_descriptions = sum(
    details["description_available_elsewhere"]
    for details in stockcode_analysis.values()
)

stockcodes_without_known_descriptions = (
    len(stockcode_analysis)
    - stockcodes_with_known_descriptions
)

print("\n--- Aggregate Findings ---")

print(
    "Total rows with missing descriptions:",
    total_missing_description_rows
)

print(
    "Unique StockCodes with missing descriptions:",
    len(stockcode_analysis)
)

print(
    "StockCodes with descriptions elsewhere:",
    stockcodes_with_known_descriptions
)

print(
    "StockCodes without descriptions elsewhere:",
    stockcodes_without_known_descriptions
)


# Investigate missing Customer IDs at invoice level

invoice_analysis = {}

for sheet_name in excel_file.sheet_names:

    df = pd.read_excel(
        excel_file,
        sheet_name=sheet_name
    )

    invoice_stats = (
        df.groupby("Invoice")
        .agg(
            total_rows=("Customer ID", "size"),
            missing_customer_ids=("Customer ID", lambda x: x.isna().sum()),
            identified_customer_ids=("Customer ID", "count")
        )
    )

    # Independent consistency check

    partial_invoice_count = (
        (
            invoice_stats["missing_customer_ids"] > 0
        )
        &
        (
            invoice_stats["identified_customer_ids"] > 0
        )
    ).sum()

    print(
        "Independently verified partially missing invoices:",
        int(partial_invoice_count)
    )

    # Classify invoice-level Customer ID completeness
    invoice_stats["invoice_status"] = "Complete"

    invoice_stats.loc[
        invoice_stats["missing_customer_ids"] > 0,
        "invoice_status"
    ] = "Partially Missing"

    invoice_stats.loc[
        invoice_stats["identified_customer_ids"] == 0,
        "invoice_status"
    ] = "Entirely Missing"

    # Count invoices by status
    status_counts = (
        invoice_stats["invoice_status"]
        .value_counts()
        .to_dict()
    )

    invoice_analysis[sheet_name] = {
        "total_invoices": int(len(invoice_stats)),
        "complete_invoices": int(
            status_counts.get("Complete", 0)
        ),
        "partially_missing_invoices": int(
            status_counts.get("Partially Missing", 0)
        ),
        "entirely_missing_invoices": int(
            status_counts.get("Entirely Missing", 0)
        )
    }

    print(f"\n--- Invoice Analysis: {sheet_name} ---")

    for status, count in status_counts.items():
        print(f"{status}: {count}")

    print("Total invoices:", len(invoice_stats))



# Build final report

report = {
    "source_file": DATASET_PATH.name,
    "analysis_timestamp_utc": datetime.now(timezone.utc).isoformat(),

    "country_analysis": country_analysis,

    "missing_description_analysis": {
        "total_missing_description_rows": int(
            total_missing_description_rows
        ),
        "unique_affected_stockcodes": int(
            len(stockcode_analysis)
        ),
        "stockcodes_with_known_descriptions": int(
            stockcodes_with_known_descriptions
        ),
        "stockcodes_without_known_descriptions": int(
            stockcodes_without_known_descriptions
        ),
        "stockcode_details": stockcode_analysis
    },

    "invoice_analysis": invoice_analysis
}

# Ensure report directory exists
REPORT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

# Save JSON report
with REPORT_PATH.open("w", encoding="utf-8") as file:
    json.dump(
        report,
        file,
        indent=4,
        ensure_ascii=False
    )

print("\nDeep analysis report saved:")
print(REPORT_PATH)