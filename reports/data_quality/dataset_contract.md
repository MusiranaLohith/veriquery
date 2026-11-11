# VeriQuery — Formal Dataset Contract

**Dataset:** UCI Online Retail II
**Source:** [UCI Machine Learning Repository — Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
**Raw file:** `data/raw/online_retail_II.xlsx`
**Consolidated file:** `data/processed/online_retail_II_consolidated.csv`
**Status:** Draft — under formal review
**Scope:** Worker 01 — Phase 1

---

## 1. Dataset Identity and Grain

### 1.1 Dataset identity

VeriQuery uses the UCI Online Retail II dataset, provided as an Excel workbook containing two worksheets:

- `Year 2009-2010`
- `Year 2010-2011`

Both worksheets contain the same eight original business columns:

1. Invoice
2. StockCode
3. Description
4. Quantity
5. InvoiceDate
6. Price
7. Customer ID
8. Country

The consolidated dataset additionally contains `source_sheet`, which records the source worksheet associated with each retained row.

### 1.2 Dataset grain

The intended grain is **one row per recorded invoice-line observation**.

A row represents a recorded product or operational line associated with an invoice. However, the dataset does not provide a dedicated unique invoice-line identifier.

Consequently:

- An invoice can contain multiple rows.
- An invoice can contain multiple products.
- The same product code can appear multiple times within an invoice.
- Exact repeated rows exist in the source worksheets.
- An identical combination of invoice and product code must not be assumed to identify a unique line.

Exact repeated records are retained unless they are verified cross-worksheet overlap removed during consolidation.

### 1.3 Consolidated dataset size

| Property | Value |
|---|---:|
| Original worksheet 1 rows | 525,461 |
| Original worksheet 2 rows | 541,910 |
| Cross-worksheet shared occurrences removed | 22,523 |
| Consolidated rows | 1,044,848 |
| Original business columns | 8 |
| Provenance column | 1 |
| Total consolidated columns | 9 |

### 1.4 Date coverage

The observed date ranges are:

- `Year 2009-2010`: 2009-12-01 to 2010-12-09
- `Year 2010-2011`: 2010-12-01 to 2011-12-09

The overall observed date range is 2009-12-01 to 2011-12-09.

These are observed minimum and maximum timestamps, not a guarantee that every date in between has records.

### 1.5 Consolidation provenance

The first worksheet was retained in full.

For the second worksheet, exact records already represented in the first worksheet were excluded only after verifying that their occurrence frequencies matched across both worksheets.

This resulted in:

- 22,202 unique exact records shared between worksheets.
- 22,523 shared row occurrences.
- Zero additional occurrences for those shared records in either worksheet.

The `source_sheet` column preserves the worksheet origin of each retained row. For shared records, the retained representation comes from the first worksheet.

No within-worksheet duplicate removal was performed.

---



## 2. Column-Level Data Dictionary

This section documents the original business columns and the additional provenance column.

### 2.1 Column definitions

| Column | Observed pandas type (Excel) | Description | Missing values across original worksheets |
|---|---|---|---:|
| `Invoice` | object | Invoice identifier associated with the recorded line | 0 |
| `StockCode` | object | Product or operational item code | 0 |
| `Description` | object | Recorded description associated with the stock code | 4,382 |
| `Quantity` | int64 | Recorded quantity for the invoice line | 0 |
| `InvoiceDate` | datetime64[us] | Date and time associated with the invoice line | 0 |
| `Price` | float64 | Recorded price associated with the line | 0 |
| `Customer ID` | float64 | Customer identifier, where available | 243,007 |
| `Country` | str | Country associated with the recorded transaction | 0 |
The additional `source_sheet` column has zero missing values in the consolidated dataset.

**Important:** Missing-value counts in this table refer to the two original worksheets before consolidation. They must not be interpreted as missing-value counts in the consolidated dataset because cross-worksheet overlap was removed.

### 2.2 Field-level semantic notes

**Invoice**
- Identifies an invoice associated with the recorded line.
- Invoice identifiers are not guaranteed to represent only ordinary completed sales.
- The source documentation identifies invoice numbers beginning with `C` as cancellations.

**StockCode**
- Identifies a product or operational item.
- The observed data includes both numeric-looking and non-numeric codes.
- Some codes represent operational entries rather than ordinary merchandise.

**Description**
- Contains recorded product or operational descriptions.
- Missing descriptions occur in the source data.
- Some descriptions contain operational annotations.
- A StockCode having a description elsewhere does not establish that every missing description should be automatically filled.

**Quantity**
- Records the quantity associated with the invoice line.
- Positive and negative values are present.
- Negative quantities must not automatically be classified as customer returns.

**InvoiceDate**
- Records the date and time associated with the invoice line.
- The observed range across both worksheets is 2009-12-01 to 2011-12-09.

**Price**
- The workbook column is named `Price`; the UCI documentation describes the corresponding field as `UnitPrice`.
- Represents the product price per unit in sterling (£).
- Zero and negative values are present.
- Negative prices occur in records associated with the `B` StockCode and `Adjust bad debt` description.
- It must not automatically be interpreted as the extended invoice-line amount.

**Customer ID**
- Identifies a customer where the identifier is available.
- Missing values are present.
- Missing Customer IDs occur across transaction-line records.
- Invoice-level inspection found that invoices were either entirely populated with Customer IDs or entirely missing them; no partially missing-ID invoices were observed in either worksheet.
- The dataset does not establish the identity of customers whose IDs are missing.

**Country**
- Records the country associated with the transaction.
- Country-level missing Customer ID rates vary considerably.
- These differences are descriptive observations and do not establish why customer identifiers are missing.

**source_sheet**
- Added during consolidation.
- Possible values are `Year 2009-2010` and `Year 2010-2011`.
- Records the source worksheet of each retained row.
- It is a provenance field, not an original business attribute.

### 2.3 Data type and nullability considerations

The observed Excel and consolidated CSV representations use the following types:

- Text-like identifiers and descriptions are represented as strings.
- `Quantity` is represented as an integer.
- `InvoiceDate` is represented as a datetime.
- `Price` is represented as a floating-point number.
- `Customer ID` is represented as a floating-point number because missing values exist.
- `source_sheet` is represented as a string.

These are observed pandas representations, not final PostgreSQL type decisions.

The final database types and nullability constraints will be defined separately during database schema design.

---


## 3. Consolidated Missing-Value Profile

### 3.1 Missing-value summary

The following counts were calculated directly from the consolidated CSV containing 1,044,848 rows.

| Column | Missing count | Missing percentage |
|---|---:|---:|
| Invoice | 0 | 0.000000% |
| StockCode | 0 | 0.000000% |
| Description | 4,275 | 0.409150% |
| Quantity | 0 | 0.000000% |
| InvoiceDate | 0 | 0.000000% |
| Price | 0 | 0.000000% |
| Customer ID | 235,287 | 22.518778% |
| Country | 0 | 0.000000% |
| source_sheet | 0 | 0.000000% |

### 3.2 Relationship between missing Description and Customer ID

The consolidated dataset produces the following cross-tabulation:

| Description status | Customer ID present | Customer ID missing |
|---|---:|---:|
| Description present | 809,561 | 231,012 |
| Description missing | 0 | 4,275 |

Key observations:

- All 4,275 records with missing Description also have missing Customer ID.
- 231,012 records have a Description but lack Customer ID.
- No records have a missing Description while retaining a Customer ID.

These are descriptive relationships. They do not establish the reason for missing values.

### 3.3 Missing-value handling policy

At this stage:

- Missing Customer IDs will remain NULL in the database.
- Missing Descriptions will remain NULL.
- No records will be deleted solely because Customer ID or Description is missing.
- No customer identities or product descriptions will be inferred or fabricated.
- Missing-value treatment will be determined by the requirements of individual analytical questions.

**Status:** Missing-value inspection completed. No missing-value imputation or deletion performed.

---


## 4. Transaction Semantics and Anomaly Observations

This section records transaction patterns observed during the original worksheet inspection. Unless explicitly stated otherwise, the counts below are from the two original worksheets before cross-worksheet consolidation.

### 4.1 Invoice identifiers and cancellation indicators

The source documentation identifies invoice numbers beginning with `C` as cancellation invoices.

Observed C-prefixed records:

| Worksheet | C-prefixed rows | Unique C-prefixed invoice identifiers |
|---|---:|---:|
| Year 2009-2010 | 10,206 | 4,592 |
| Year 2010-2011 | 9,288 | 3,836 |

Interpretation:

- A C-prefixed invoice is a source-documented cancellation indicator.
- It must not automatically be interpreted as an ordinary completed sale.
- The cancellation indicator should be preserved during ingestion.
- The dataset does not establish that every negative-quantity record is a cancellation.

The unique invoice counts above are worksheet-level observations and must not be added to claim a consolidated unique invoice count without a separate cross-worksheet verification.

### 4.2 Quantity patterns

Observed quantity distributions:

| Quantity category | Year 2009-2010 | Year 2010-2011 |
|---|---:|---:|
| Positive quantity | 513,135 | 531,286 |
| Negative quantity | 12,326 | 10,624 |
| Zero quantity | 0 | 0 |

Negative quantities require careful interpretation.

Of the negative-quantity records:

| Category | Year 2009-2010 | Year 2010-2011 |
|---|---:|---:|
| C-prefixed invoice | 10,205 | 9,288 |
| Non-C-prefixed invoice | 2,121 | 1,336 |

The non-C-prefixed negative-quantity records total 3,457 across the two original worksheets.

Some contain descriptions such as `damages`, `damaged`, `check`, `thrown away`, and `Unsaleable destroyed`. Others have missing descriptions.

Therefore:

- Negative quantity is an observed numerical property.
- Negative quantity alone does not prove that a record represents a customer return.
- C-prefixed invoice status and negative quantity should be treated as separate attributes.
- Operational explanations should not be inferred solely from quantity signs.

### 4.3 Price patterns

The original worksheets contain:

| Price category | Year 2009-2010 | Year 2010-2011 |
|---|---:|---:|
| Positive price | 521,771 | 539,393 |
| Zero price | 3,687 | 2,515 |
| Negative price | 3 | 2 |

All five observed negative-price records had:

- `StockCode`: `B`
- `Description`: `Adjust bad debt`
- `Quantity`: 1
- Missing Customer ID

The observed negative prices were:

| Invoice | Price |
|---|---:|
| A506401 | -53,594.36 |
| A516228 | -44,031.79 |
| A528059 | -38,925.87 |
| A563186 | -11,062.06 |
| A563187 | -11,062.06 |

These records indicate that the Price column is not necessarily a conventional positive merchandise unit price.

Zero-price records must also be preserved until their business meaning is established.

### 4.4 Operational and special StockCodes

The inspection identified several StockCodes associated with operational entries.

| StockCode | Observed description | Year 2009-2010 rows | Year 2010-2011 rows |
|---|---|---:|---:|
| M | Manual | 850 | 571 |
| B | Adjust bad debt | 3 | 3 |
| D | Discount | 100 | 77 |
| POST | Postage | 865 | 1,257 |
| DOT | Dotcom postage | 736 | 710 |
| BANK CHARGES | Bank charges | 65 | 37 |
| AMAZONFEE | Amazon fee | 9 | 34 |
| C2 | Carriage | 138 | 144 |
| CRUK | CRUK commission | 0 | 16 |

These examples demonstrate that StockCode is not exclusively a product identifier. It can also represent operational or financial entries.

The above list is based on selected codes examined during inspection. It is not an exhaustive classification of every StockCode.

### 4.5 Transaction interpretation policy

For ingestion and future analytical processing:

1. Preserve original Invoice, StockCode, Description, Quantity, and Price values.
2. Preserve C-prefixed invoice identifiers.
3. Do not automatically classify every negative quantity as a return.
4. Do not automatically classify every C-prefixed record as a completed sale.
5. Do not treat zero or negative prices as invalid without further evidence.
6. Do not assume every StockCode represents a physical product.
7. Retain operational entries rather than deleting them during initial ingestion.

Any future business classification must be supported by documented source semantics or independently verified evidence.

**Status:** Transaction anomaly inspection completed. No transaction records removed or reclassified.

---


## 5. Duplicate Records and Consolidation Policy

### 5.1 Exact duplicate definition

For this inspection, an exact duplicate is defined as a row whose values match across all eight original business columns:

- Invoice
- StockCode
- Description
- Quantity
- InvoiceDate
- Price
- Customer ID
- Country

The `source_sheet` provenance column is excluded from the comparison because it was added during consolidation.

### 5.2 Within-worksheet duplicate observations

The original worksheets contain exact repeated records.

| Metric | Year 2009-2010 | Year 2010-2011 |
|---|---:|---:|
| Rows belonging to duplicate groups | 13,283 | 10,147 |
| Unique duplicate groups | 6,418 | 4,879 |
| Additional repeated rows | 6,865 | 5,268 |
| Maximum occurrences of one exact record | 6 | 20 |

These are independent worksheet-level measurements.

The combined figures must not be interpreted as the number of unique duplicate records across the consolidated dataset because some exact records occur in both worksheets.

### 5.3 Cross-worksheet overlap

An exact-record frequency comparison was performed between the two worksheets.

| Metric | Result |
|---|---:|
| Unique exact records present in both worksheets | 22,202 |
| Shared row occurrences | 22,523 |
| Additional occurrences in first worksheet | 0 |
| Additional occurrences in second worksheet | 0 |

The occurrence frequencies of all shared exact records matched between the worksheets.

This verification established that the second worksheet contained no additional occurrences of records already represented in the first worksheet.

### 5.4 Consolidation policy

The following consolidation procedure was applied:

1. Retain the first worksheet in full.
2. Identify exact records appearing in both worksheets.
3. Compare their occurrence frequencies.
4. Stop consolidation if any shared record has mismatched occurrence frequencies.
5. Retain from the second worksheet only exact records absent from the first worksheet.
6. Preserve the original worksheet name in `source_sheet`.

Result:

| Metric | Rows |
|---|---:|
| First worksheet retained | 525,461 |
| Second worksheet retained | 519,387 |
| Consolidated dataset | 1,044,848 |

### 5.5 Duplicate handling policy

- Exact repeated records within an individual worksheet are retained.
- Only verified cross-worksheet overlap is removed.
- No assumption is made that repeated invoice lines are accidental.
- No unique invoice-line identifier is available to establish whether identical rows represent separate legitimate observations or data-entry duplication.
- Future analytical queries involving transaction counts, quantities, or revenue must account for the possibility of repeated records.


### 5.6 Provenance

- The consolidated dataset contains the additional source_sheet column.
- It identifies the original worksheet from which each retained row originated.
- For records appearing in both worksheets with matching frequencies, the retained representation originates from Year 2009-2010.

Status: Cross-worksheet overlap verified and consolidated. Within-worksheet repeated records preserved.

---

## 6. Dataset Limitations and Analytical Safeguards

This section documents known limitations identified during Worker 01 inspection. These limitations must be considered during database design, retrieval, SQL generation, and analytical evaluation.

### 6.1 No unique invoice-line identifier

The dataset does not provide a dedicated unique identifier for individual invoice lines.

Consequences:

- A row cannot be uniquely identified using a documented transaction-line ID.
- Identical rows may represent repeated observations.
- Invoice and StockCode together cannot be assumed to uniquely identify a line.
- Row counts must not automatically be described as unique transaction counts.

### 6.2 Missing customer identifiers

A substantial portion of the consolidated dataset has missing Customer ID values.

Observed missing Customer ID count: 235,287 (22.518778%).

Consequences:

- Customer-level analysis must account for records without an identifiable Customer ID.
- Missing IDs must not be replaced with fabricated customer identities.
- Counts of distinct identified customers must not be presented as counts of all actual customers.
- Grouping by Customer ID retains records with NULL Customer IDs in a separate NULL group. Queries that explicitly filter out NULL Customer IDs exclude those records, and this exclusion must be disclosed.

### 6.3 Missing descriptions

There are 4,275 consolidated records with missing Description values.

Inspection found that some StockCodes have descriptions elsewhere, while others do not.

Consequences:

- Missing descriptions must remain NULL unless a separately validated enrichment rule is established.
- Descriptions must not be inferred solely from similar StockCodes.
- Operational annotations must not be mistaken for ordinary product descriptions.

### 6.4 Ambiguous transaction semantics

The dataset contains:

- C-prefixed cancellation invoice identifiers.
- Negative quantities.
- Zero prices.
- Negative prices.
- Operational StockCodes and descriptions.

These attributes do not independently establish a complete business classification.

Consequences:

- Negative quantities must not automatically be classified as customer returns.
- C-prefixed invoices must not be treated as ordinary completed sales.
- Negative and zero prices must not automatically be discarded.
- Operational StockCodes must not automatically be included in merchandise-product counts.
- Revenue definitions must explicitly state how cancellations, adjustments, discounts, postage, and other operational entries are handled.

### 6.5 Repeated records

Exact repeated rows exist within the original worksheets.

No dedicated line identifier is available to establish whether all such repetitions are accidental.

Consequences:

- Within-worksheet repetitions remain preserved.
- Analytical queries must define whether they operate on recorded rows, invoices, products, or another business entity.
- Deduplication must not be introduced without an independently justified rule.

### 6.6 Limited business definitions

The source data does not provide a complete business glossary defining every operational StockCode, cancellation scenario, or financial adjustment.

Consequences:

- Business terms must be documented using verified source evidence.
- Unknown or ambiguous terms must remain explicitly unresolved.
- SQL examples must not encode unsupported business assumptions.
- Analytical answers must distinguish source facts from interpretation.

### 6.7 Analytical safeguards for VeriQuery

Future query generation and evaluation should enforce the following principles:

1. Use only columns and relationships supported by the actual database schema.
2. Do not assume a unique invoice-line key.
3. Do not silently exclude missing Customer IDs.
4. Do not automatically interpret negative quantities as returns.
5. Distinguish cancellation indicators from ordinary invoice records.
6. Define revenue and sales metrics explicitly before calculating them.
7. Treat operational StockCodes separately from merchandise when the question requires that distinction.
8. Preserve uncertainty when the dataset cannot support a definitive answer.
9. Identify assumptions that materially affect analytical results.
10. Return an appropriate limitation or clarification when a question cannot be answered reliably.

**Status:** Known dataset limitations documented. No additional cleaning or business reclassification performed.

---

## 7. Transformation and Reproducibility Record

### 7.1 Source dataset

| Property | Value |
|---|---|
| Dataset name | UCI Online Retail II |
| Source | UCI Machine Learning Repository |
| Original format | Excel workbook (`.xlsx`) |
| Original filename | `online_retail_II.xlsx` |
| Raw data directory | `data/raw/` |

The original workbook is retained unchanged.

**Dataset citation:**

Chen, D. (2012). Online Retail II [Dataset].
UCI Machine Learning Repository.
https://doi.org/10.24432/C5CG6D

**Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0).

### 7.2 Processing environment

| Component | Version / Configuration |
|---|---|
| Programming language | Python 3.11 |
| Data processing library | pandas 3.1.1 |
| Excel reader | openpyxl 3.1.5 |
| Environment | Conda environment `veriquery` |

These versions represent the environment used during the recorded processing work.

### 7.3 Inspection scripts

The following scripts were created and executed during dataset inspection.

| Script | Responsibility |
|---|---|
| `01_workbook_overview.py` | Workbook structure, worksheet dimensions, columns, data types, missing values, and date ranges |
| `02_missing_value_analysis.py` | Missing-value relationships and initial missing-value investigation |
| `03_missing_value_deep_analysis.py` | Country-level missing Customer IDs, description investigation, and invoice-level missing-ID analysis |
| `04_duplicate_overlap_analysis.py` | Within-sheet duplicates, cross-sheet overlap, and occurrence-frequency comparison |
| `05_transaction_anomaly_analysis.py` | Cancellation indicators, quantity patterns, price anomalies, and selected operational StockCodes |
| `06_dataset_consolidation.py` | Verified cross-sheet overlap removal, provenance preservation, consolidation, and initial validation |
| `07_consolidated_csv_validation.py` | Reloading the saved CSV and validating its dimensions, columns, and provenance |
| `08_consolidated_missing_value_check.py` | Missing-value analysis on the consolidated dataset |

### 7.4 Generated inspection reports

Inspection outputs are stored in `reports/data_quality/`.

| Report | Contents |
|---|---|
| `workbook_overview.json` | Original workbook structure and column-level overview |
| `missing_value_analysis.json` | Initial missing-value findings |
| `missing_value_deep_analysis.json` | Detailed missing-value investigation |
| `duplicate_overlap_analysis.json` | Duplicate and cross-worksheet overlap findings |
| `transaction_anomaly_analysis.json` | Transaction anomaly observations |

### 7.5 Consolidation transformation

Input:

`data/raw/online_retail_II.xlsx`

Output:

`data/processed/online_retail_II_consolidated.csv`

Transformation procedure:

1. Load both original worksheets.
2. Add a `source_sheet` provenance column to each worksheet.
3. Count exact row occurrences using all eight original business columns.
4. Compare occurrence frequencies for records present in both worksheets.
5. Stop processing if shared-record frequencies do not match.
6. Retain the first worksheet in full.
7. Retain only records absent from the first worksheet from the second worksheet.
8. Concatenate the retained records.
9. Validate total rows, source provenance, and original column preservation.
10. Save the consolidated dataset as UTF-8 CSV.

### 7.6 Consolidated output verification

The saved CSV was independently reloaded and checked.

Verified results:

- Total rows: 1,044,848.
- Total columns: 9.
- First worksheet provenance: 525,461 rows.
- Second worksheet provenance: 519,387 rows.
- Missing provenance values: 0.
- Original eight business columns preserved.
- `InvoiceDate` successfully parsed as a datetime column.

The consolidated missing-value analysis was also executed separately.

### 7.7 Reproducibility requirements

To reproduce the processing workflow:

1. Preserve the original workbook at `data/raw/online_retail_II.xlsx`.
2. Use the recorded Python and library environment.
3. Execute the inspection scripts in their documented order.
4. Execute the consolidation script only after confirming the source workbook and overlap assumptions.
5. Execute the saved CSV validation and missing-value analysis scripts.
6. Compare the generated outputs against the documented findings.

Any future change to the source workbook, consolidation logic, or data-cleaning policy must be documented and validated.

### 7.8 Processing status

| Activity | Status |
|---|---|
| Original workbook inspection | Completed |
| Missing-value investigation | Completed |
| Duplicate and overlap investigation | Completed |
| Transaction anomaly investigation | Completed |
| Cross-sheet consolidation | Completed |
| CSV structural validation | Completed |
| Consolidated missing-value analysis | Completed |
| Formal dataset contract | Draft completed; review pending |
| Data cleaning and enrichment | Not performed |
| PostgreSQL schema implementation | Not started in this workflow |

---
