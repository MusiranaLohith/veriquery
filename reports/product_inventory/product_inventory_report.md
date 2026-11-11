# Product Inventory and StockCode Analysis Report

## 1. Objective

This report documents the StockCode inventory in the consolidated Online Retail II dataset. It investigates identifier patterns, description consistency, missing descriptions, operational-entry candidates, and product-condition annotations.

The purpose is to establish a reliable foundation for downstream natural-language analytics without assuming that every StockCode represents a merchandise product.

## 2. Inventory Overview

| Metric | Result |
|---|---:|
| Total transaction records | 1,044,848 |
| Distinct StockCodes | 5,305 |
| Numeric-only StockCodes | 3,590 |
| Non-numeric StockCodes | 1,715 |
| Codes with exactly one distinct non-NULL description | 3,736 |
| Codes with multiple distinct non-NULL descriptions | 1,214 |
| Codes with no non-NULL description | 355 |
| Codes affected by missing descriptions | 2,451 |
| Transaction rows with missing descriptions | 4,275 |

Numeric and non-numeric StockCodes are identifier-format groups, not confirmed product and operational categories.

## 3. Description Consistency

The inventory contains:

- Codes with one consistent non-NULL description.
- Codes associated with multiple distinct descriptions.
- Codes whose descriptions are entirely missing.
- Codes with both missing and non-missing descriptions.

Multiple descriptions may represent spelling or naming variations, condition annotations, corrections, or other inconsistencies. They must not automatically be treated as separate products or as interchangeable descriptions.

The original recorded descriptions are preserved.

## 4. Operational-Entry Candidates

Twelve StockCodes have strong evidence of representing operational or adjustment entries.

| StockCode | Recorded description | Records |
|---|---|---:|
| POST | POSTAGE | 2,086 |
| DOT | DOTCOM POSTAGE | 1,425 |
| M | Manual | 1,398 |
| C2 | CARRIAGE | 277 |
| D | Discount | 173 |
| BANK CHARGES | Bank Charges | 100 |
| ADJUST | Adjustment by John / Peter | 67 |
| AMAZONFEE | AMAZON FEE | 36 |
| CRUK | CRUK Commission | 16 |
| B | Adjust bad debt | 6 |
| m | Manual | 5 |
| ADJUST2 | Adjustment by Peter | 3 |
| **Total** | | **5,592** |

These classifications are based on the recorded StockCode and description. They do not establish the exact accounting treatment of the transactions.

StockCodes `M` and `m` are distinct identifiers and must remain case-sensitive.

## 5. Description Annotations

Exploratory keyword analysis identified 439 StockCode-description combinations for further review:

| Preliminary annotation | Combinations | Distinct StockCodes | Transaction occurrences |
|---|---:|---:|---:|
| Condition / adjustment candidates | 247 | 233 | 324 |
| Channel-reference candidates | 88 | 78 | 173 |
| Operational-entry candidates | 9 | 9 | 5,504 |
| Other / ambiguous | 95 | 91 | 381 |

These categories are mutually exclusive outputs of a keyword-based CASE expression. They are not definitive business classifications.

Examples of condition or correction descriptions include `damaged`, `missing`, `broken`, `mouldy`, and `wrongly marked`.

Channel-related descriptions include references to `dotcom` and `amazon`. Such references do not automatically establish that a StockCode is an operational entry.

## 6. Quantity Pattern Observations

Operational-entry candidates contain both positive and negative quantities.

For example:

- POST: 228 negative and 1,858 positive quantity records.
- D: 168 negative and 5 positive quantity records.
- ADJUST: 31 negative and 36 positive quantity records.
- B: 6 positive and 0 negative quantity records.

Consequently, quantity sign alone is insufficient to classify transaction purpose.

## 7. Classification Policy

The inventory uses a conservative evidence-based classification approach:

1. **Operational-entry candidate:** Strong evidence from identifier and recorded description.
2. **Merchandise candidate:** Description appears to identify merchandise, but is not independently verified.
3. **Condition/adjustment annotation:** Description records a condition, correction, or adjustment note.
4. **Ambiguous:** Available evidence is insufficient or conflicting.
5. **Unidentified:** No usable non-NULL description is available.

The classification is intended to guide downstream schema-grounded analytics. It does not overwrite original data or claim that every identifier has a verified business meaning.

## 8. Analytical Safeguards

- Preserve StockCode values exactly, including letter case.
- Preserve all original descriptions and their variants.
- Do not assume every numeric StockCode is merchandise.
- Do not assume every non-numeric StockCode is operational.
- Do not automatically fill missing descriptions.
- Do not interpret every negative quantity as a customer return.
- Do not interpret quantity signs as definitive evidence of accounting treatment.
- Do not calculate sales revenue by blindly multiplying all quantities by prices.
- Treat keyword classifications as investigation evidence, not ground truth.

## 9. Supporting Artifacts

The following artifacts support this investigation:

- `stockcode_inventory.csv`
- `numeric_stockcodes.csv`
- `non_numeric_stockcodes.csv`
- `master_stockcode_inventory.csv`
- `annotation_candidates.csv`
- `operational_code_inventory.csv`

SQL investigation scripts are maintained under `sql/analysis/`, and supporting Python analysis scripts are maintained under `scripts/inspection/`.

## 10. Conclusion

The consolidated dataset contains 5,305 distinct StockCodes, but the identifier inventory is not equivalent to a verified product catalog.

The analysis identified a set of operational-entry candidates, inconsistent descriptions, condition annotations, and missing product descriptions. A conservative classification policy is therefore necessary to prevent downstream natural-language analytics from assigning unsupported meanings to transaction records.