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

REPORT_DIR = PROJECT_ROOT / "reports" / "data_quality"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATASET_PATH}"
    )

workbook = pd.ExcelFile(
    DATASET_PATH,
    engine="openpyxl"
)

print("=" * 60)
print("VERIQUERY - MISSING VALUE ANALYSIS")
print("=" * 60)



worksheet_reports = {}

for sheet_name in workbook.sheet_names:

    print("\n" + "=" * 60)
    print(f"WORKSHEET: {sheet_name}")
    print("=" * 60)

    df = pd.read_excel(
        workbook,
        sheet_name=sheet_name
    )

    total_records = len(df)

    # ---------------------------------------
    # 1. Missing-value relationship
    # ---------------------------------------

    missing_description = df["Description"].isna()
    missing_customer = df["Customer ID"].isna()

    relationship = pd.crosstab(
        missing_description,
        missing_customer
    )

    print("\nMissing Description vs Missing Customer ID:")
    print(relationship.to_string())

    both_missing = int(
        (missing_description & missing_customer).sum()
    )

    description_only = int(
        (missing_description & ~missing_customer).sum()
    )

    customer_only = int(
        (~missing_description & missing_customer).sum()
    )

    neither_missing = int(
        (~missing_description & ~missing_customer).sum()
    )

    print("\nRelationship summary:")
    print(f"Both missing: {both_missing:,}")
    print(f"Description only: {description_only:,}")
    print(f"Customer ID only: {customer_only:,}")
    print(f"Neither missing: {neither_missing:,}")

    # ---------------------------------------
    # 2. Missing product descriptions
    # ---------------------------------------

    missing_description_rows = df[missing_description]

    missing_description_stockcodes = (
        missing_description_rows["StockCode"]
        .value_counts()
    )

    print("\nTop StockCodes with missing descriptions:")

    print(
        missing_description_stockcodes.head(15).to_string()
    )

    # ---------------------------------------
    # 3. Missing Customer IDs by country
    # ---------------------------------------

    missing_customer_rows = df[missing_customer]

    missing_customer_countries = (
        missing_customer_rows["Country"]
        .value_counts()
    )

    print("\nTop countries with missing Customer IDs:")

    print(
        missing_customer_countries.head(15).to_string()
    )

    # ---------------------------------------
    # 4. Missing values and cancellations
    # ---------------------------------------

    cancellation_mask = (
        df["Invoice"]
        .astype("string")
        .str.startswith("C", na=False)
    )

    cancellation_count = int(cancellation_mask.sum())

    print("\nCancellation analysis:")

    print(
        f"Cancellation-prefixed rows: "
        f"{cancellation_count:,}"
    )

    print(
        f"Cancellation rows with missing Customer ID: "
        f"{int((cancellation_mask & missing_customer).sum()):,}"
    )

    print(
        f"Cancellation rows with missing Description: "
        f"{int((cancellation_mask & missing_description).sum()):,}"
    )

    # ---------------------------------------
    # 5. Store findings
    # ---------------------------------------

    worksheet_reports[sheet_name] = {
        "total_records": total_records,
        "missing_value_relationships": {
            "both_missing": both_missing,
            "description_only": description_only,
            "customer_id_only": customer_only,
            "neither_missing": neither_missing
        },
        "missing_description_stockcodes": {
            str(code): int(count)
            for code, count
            in missing_description_stockcodes.head(15).items()
        },
        "missing_customer_countries": {
            str(country): int(count)
            for country, count
            in missing_customer_countries.head(15).items()
        },
        "cancellations": {
            "total_rows": cancellation_count,
            "missing_customer_id": int(
                (cancellation_mask & missing_customer).sum()
            ),
            "missing_description": int(
                (cancellation_mask & missing_description).sum()
            )
        }
    }

    del df


# ---------------------------------------
# 6. Save consolidated report
# ---------------------------------------

report = {
    "source_file": DATASET_PATH.name,
    "inspection_timestamp_utc": (
        datetime.now(timezone.utc).isoformat()
    ),
    "worksheets": worksheet_reports
}

report_path = (
    REPORT_DIR / "missing_value_analysis.json"
)

with open(report_path, "w", encoding="utf-8") as file:
    json.dump(report, file, indent=4)

print("\n" + "=" * 60)
print("MISSING VALUE ANALYSIS COMPLETE")
print("=" * 60)

print(f"\nReport saved to: {report_path}")

workbook.close()
