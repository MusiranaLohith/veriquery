
from pathlib import Path
import json
from datetime import datetime, timezone

import pandas as pd


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "online_retail_II.xlsx"
)

REPORT_DIR = PROJECT_ROOT / "reports" / "data_quality"

REPORT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. VERIFY DATASET
# --------------------------------------------------

if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATASET_PATH}"
    )


# --------------------------------------------------
# 3. LOAD WORKBOOK
# --------------------------------------------------

workbook = pd.ExcelFile(
    DATASET_PATH,
    engine="openpyxl"
)

print("=" * 60)
print("VERIQUERY - WORKBOOK OVERVIEW")
print("=" * 60)

print(f"\nSource file: {DATASET_PATH.name}")
print(f"Worksheets: {workbook.sheet_names}")


# --------------------------------------------------
# 4. INSPECT EACH WORKSHEET
# --------------------------------------------------

worksheet_reports = {}

for sheet_name in workbook.sheet_names:

    print("\n" + "=" * 60)
    print(f"WORKSHEET: {sheet_name}")
    print("=" * 60)

    df = pd.read_excel(
        workbook,
        sheet_name=sheet_name
    )

    # A. Dimensions

    rows, columns = df.shape

    print(f"\nRows: {rows:,}")
    print(f"Columns: {columns}")

    print("\nColumn names:")

    for column in df.columns:
        print(f"  - {column}")

    # B. Data types

    print("\nData types:")

    data_types = {}

    for column, dtype in df.dtypes.items():

        print(f"{column}: {dtype}")

        data_types[column] = str(dtype)

    # C. Missing values

    print("\nMissing values:")

    missing_values = df.isnull().sum()

    missing_report = {}

    for column, count in missing_values.items():

        percentage = (count / rows) * 100

        print(
            f"{column}: {count:,} "
            f"({percentage:.2f}%)"
        )

        missing_report[column] = {
            "count": int(count),
            "percentage": round(percentage, 2)
        }

    # D. Date range

    date_report = {}

    if "InvoiceDate" in df.columns:

        dates = pd.to_datetime(
            df["InvoiceDate"],
            errors="coerce"
        )

        minimum_date = dates.min()
        maximum_date = dates.max()

        print("\nInvoice date range:")
        print(f"Minimum: {minimum_date}")
        print(f"Maximum: {maximum_date}")

        date_report = {
            "minimum": str(minimum_date),
            "maximum": str(maximum_date)
        }

    # E. Memory usage

    memory_mb = (
        df.memory_usage(deep=True).sum()
        / (1024 ** 2)
    )

    print(f"\nMemory usage: {memory_mb:.2f} MB")

    # F. Store worksheet findings

    worksheet_reports[sheet_name] = {
        "row_count": rows,
        "column_count": columns,
        "columns": list(df.columns),
        "data_types": data_types,
        "missing_values": missing_report,
        "date_range": date_report,
        "memory_usage_mb": round(memory_mb, 2)
    }

    del df


# --------------------------------------------------
# 5. SAVE CONSOLIDATED JSON REPORT
# --------------------------------------------------

overview = {
    "source_file": DATASET_PATH.name,
    "inspection_timestamp_utc": (
        datetime.now(timezone.utc).isoformat()
    ),
    "total_worksheets": len(workbook.sheet_names),
    "worksheet_names": workbook.sheet_names,
    "worksheets": worksheet_reports
}

report_path = REPORT_DIR / "workbook_overview.json"

with open(report_path, "w", encoding="utf-8") as file:

    json.dump(
        overview,
        file,
        indent=4
    )

print("\n" + "=" * 60)
print("INSPECTION COMPLETE")
print("=" * 60)

print(f"\nReport saved to: {report_path}")

workbook.close()
