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
    / "transaction_anomaly_analysis.json"
)


# Load both worksheets
sheet_data = pd.read_excel(
    DATASET_PATH,
    sheet_name=None,
    engine="openpyxl"
)


# Display basic confirmation
print("Dataset loaded successfully.")
print(f"Worksheets: {list(sheet_data.keys())}")

for sheet_name, df in sheet_data.items():
    print(f"\n{sheet_name}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

# --------------------------------------------------
# 1. Cancellation invoice analysis
# --------------------------------------------------

print("\n" + "=" * 60)
print("CANCELLATION INVOICE ANALYSIS")
print("=" * 60)

for sheet_name, df in sheet_data.items():

    cancellation_mask = (
        df["Invoice"]
        .astype(str)
        .str.startswith("C")
    )

    cancellation_df = df[cancellation_mask]

    print(f"\n{sheet_name}")
    print(f"Total rows: {len(df)}")
    print(f"C-prefixed invoice rows: {len(cancellation_df)}")

    print(
        "Unique cancellation invoices:",
        cancellation_df["Invoice"].nunique()
    )


# --------------------------------------------------
# 2. Quantity anomaly analysis
# --------------------------------------------------

print("\n" + "=" * 60)
print("QUANTITY ANOMALY ANALYSIS")
print("=" * 60)

for sheet_name, df in sheet_data.items():

    negative_quantity = df[df["Quantity"] < 0]
    zero_quantity = df[df["Quantity"] == 0]
    positive_quantity = df[df["Quantity"] > 0]

    print(f"\n{sheet_name}")

    print(f"Negative quantity rows: {len(negative_quantity)}")
    print(f"Zero quantity rows: {len(zero_quantity)}")
    print(f"Positive quantity rows: {len(positive_quantity)}")

    print(
        "Negative quantity with C-prefixed invoice:",
        negative_quantity["Invoice"]
        .astype(str)
        .str.startswith("C")
        .sum()
    )

    print(
        "Negative quantity without C-prefixed invoice:",
        (~negative_quantity["Invoice"]
         .astype(str)
         .str.startswith("C"))
        .sum()
    )

# --------------------------------------------------
# 3. Investigate negative quantities without C prefix
# --------------------------------------------------

print("\n" + "=" * 60)
print("NEGATIVE QUANTITY WITHOUT C-PREFIX ANALYSIS")
print("=" * 60)

for sheet_name, df in sheet_data.items():

    invoice_is_cancellation = (
        df["Invoice"]
        .astype(str)
        .str.startswith("C")
    )

    unusual_negative = df[
        (df["Quantity"] < 0)
        & (~invoice_is_cancellation)
    ].copy()

    print(f"\n{sheet_name}")
    print(f"Rows: {len(unusual_negative)}")

    print("\nMost frequent StockCodes:")
    print(
        unusual_negative["StockCode"]
        .value_counts()
        .head(15)
        .to_string()
    )

    print("\nMost frequent descriptions:")
    print(
        unusual_negative["Description"]
        .value_counts(dropna=False)
        .head(15)
        .to_string()
    )

    print("\nSample records:")
    print(
        unusual_negative[
            [
                "Invoice",
                "StockCode",
                "Description",
                "Quantity",
                "InvoiceDate",
                "Price",
                "Customer ID",
                "Country"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )


# --------------------------------------------------
# 4. C-prefixed invoices with non-negative quantities
# --------------------------------------------------

print("\n" + "=" * 60)
print("C-PREFIXED NON-NEGATIVE QUANTITY ANALYSIS")
print("=" * 60)

for sheet_name, df in sheet_data.items():

    cancellation_mask = (
        df["Invoice"]
        .astype(str)
        .str.startswith("C")
    )

    unusual_cancellations = df[
        cancellation_mask & (df["Quantity"] >= 0)
    ]

    print(f"\n{sheet_name}")
    print(f"Rows: {len(unusual_cancellations)}")

    if not unusual_cancellations.empty:
        print(
            unusual_cancellations.to_string(index=False)
        )


# --------------------------------------------------
# 5. Price anomaly analysis
# --------------------------------------------------

print("\n" + "=" * 60)
print("PRICE ANOMALY ANALYSIS")
print("=" * 60)

for sheet_name, df in sheet_data.items():

    zero_price = df[df["Price"] == 0]
    negative_price = df[df["Price"] < 0]
    positive_price = df[df["Price"] > 0]

    print(f"\n{sheet_name}")

    print(f"Zero-price rows: {len(zero_price)}")
    print(f"Negative-price rows: {len(negative_price)}")
    print(f"Positive-price rows: {len(positive_price)}")

    if not zero_price.empty:
        print("\nMost frequent descriptions among zero-price rows:")

        print(
            zero_price["Description"]
            .value_counts(dropna=False)
            .head(15)
            .to_string()
        )

    if not negative_price.empty:
        print("\nNegative-price records:")

        print(
            negative_price[
                [
                    "Invoice",
                    "StockCode",
                    "Description",
                    "Quantity",
                    "InvoiceDate",
                    "Price",
                    "Customer ID",
                    "Country"
                ]
            ].to_string(index=False)
        )

# --------------------------------------------------
# 6. StockCode analysis
# --------------------------------------------------

print("\n" + "=" * 60)
print("STOCK CODE ANALYSIS")
print("=" * 60)

for sheet_name, df in sheet_data.items():

    stock_code_counts = (
        df["StockCode"]
        .astype(str)
        .value_counts()
    )

    print(f"\n{sheet_name}")

    print(
        "Total unique StockCodes:",
        df["StockCode"].nunique()
    )

    print("\nMost frequent StockCodes:")
    print(stock_code_counts.head(20).to_string())

    # Inspect selected special stock codes
    special_codes = [
        "M",
        "B",
        "D",
        "POST",
        "DOT",
        "CRUK",
        "BANK CHARGES",
        "AMAZONFEE",
        "C2",
    ]

    print("\nSelected special StockCodes:")

    for code in special_codes:

        matching_rows = df[
            df["StockCode"].astype(str) == code
        ]

        if not matching_rows.empty:

            print(f"\nStockCode: {code}")
            print(f"Occurrences: {len(matching_rows)}")

            print(
                "Descriptions:",
                matching_rows["Description"]
                .value_counts(dropna=False)
                .head(5)
                .to_dict()
            )

            print(
                "Price range:",
                matching_rows["Price"].min(),
                "to",
                matching_rows["Price"].max()
            )


# --------------------------------------------------
# 7. Save transaction anomaly report
# --------------------------------------------------

anomaly_report = {
    "source_file": DATASET_PATH.name,
    "analysis_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "worksheets": {}
}

for sheet_name, df in sheet_data.items():

    invoice_c = df["Invoice"].astype(str).str.startswith("C")

    negative_quantity = df["Quantity"] < 0
    zero_quantity = df["Quantity"] == 0
    positive_quantity = df["Quantity"] > 0

    zero_price = df["Price"] == 0
    negative_price = df["Price"] < 0
    positive_price = df["Price"] > 0

    negative_without_c = negative_quantity & ~invoice_c

    c_non_negative = invoice_c & ~negative_quantity

    special_codes = [
        "M", "B", "D", "POST", "DOT",
        "BANK CHARGES", "AMAZONFEE", "C2", "CRUK"
    ]

    special_code_counts = {}

    for code in special_codes:
        special_code_counts[code] = int(
            (df["StockCode"].astype(str) == code).sum()
        )

    anomaly_report["worksheets"][sheet_name] = {
        "total_rows": int(len(df)),

        "invoice_analysis": {
            "c_prefixed_rows": int(invoice_c.sum()),
            "unique_c_prefixed_invoices": int(
                df.loc[invoice_c, "Invoice"].nunique()
            )
        },

        "quantity_analysis": {
            "negative_rows": int(negative_quantity.sum()),
            "zero_rows": int(zero_quantity.sum()),
            "positive_rows": int(positive_quantity.sum()),
            "negative_with_c_prefix": int(
                (negative_quantity & invoice_c).sum()
            ),
            "negative_without_c_prefix": int(
                negative_without_c.sum()
            ),
            "c_prefixed_non_negative": int(
                c_non_negative.sum()
            )
        },

        "price_analysis": {
            "zero_price_rows": int(zero_price.sum()),
            "negative_price_rows": int(negative_price.sum()),
            "positive_price_rows": int(positive_price.sum())
        },

        "stock_code_analysis": {
            "unique_stock_codes": int(df["StockCode"].nunique()),
            "special_code_counts": special_code_counts
        }
    }


REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

with REPORT_PATH.open("w", encoding="utf-8") as file:
    json.dump(
        anomaly_report,
        file,
        indent=4,
        ensure_ascii=False
    )

print("\n" + "=" * 60)
print("ANOMALY REPORT SAVED")
print("=" * 60)
print(REPORT_PATH)