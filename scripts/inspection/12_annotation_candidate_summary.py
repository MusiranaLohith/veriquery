import pandas as pd

file_path = "reports/product_inventory/annotation_candidates.csv"

df = pd.read_csv(file_path)

print("Total StockCode-description combinations:", len(df))

print("\nPreliminary annotation distribution:")
print(
    df["preliminary_annotation"]
    .value_counts()
    .to_string()
)

print("\nDistinct StockCodes per annotation:")
print(
    df.groupby("preliminary_annotation")["stock_code"]
    .nunique()
    .to_string()
)

print("\nTransaction occurrences per annotation:")
print(
    df.groupby("preliminary_annotation")["occurrences"]
    .sum()
    .to_string()
)

print("\nSample ambiguous descriptions:")
ambiguous = df[df["preliminary_annotation"] == "other"]

print(
    ambiguous[
        ["stock_code", "description", "occurrences"]
    ].head(30).to_string(index=False)
)