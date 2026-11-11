# VeriQuery — Business Glossary

## 1. Dataset and Transaction Concepts

### 1.1 Transaction Record
A single row in `retail_transactions`, representing one recorded invoice-line observation. It is not necessarily a unique product sale because repeated rows are preserved.

### 1.2 Invoice
The recorded invoice identifier stored in `invoice`. Multiple transaction records may share the same invoice identifier.

### 1.3 Invoice Line
A row-level observation associated with an invoice, containing a StockCode, quantity, price, date, and other recorded attributes. This is a practical description of the dataset's row structure, not a claim that every row is a unique commercial line.

### 1.4 Cancellation Invoice
An invoice whose identifier begins with the letter `C`. The original dataset documentation identifies this prefix as indicating cancellations. This should not be confused with every negative-quantity record.

### 1.5 Source Sheet
The original workbook worksheet from which a transaction record originated. Stored in `source_sheet` as either `Year 2009-2010` or `Year 2010-2011`.

## 2. Database Attributes

### 2.1 StockCode
The recorded item or operational-entry identifier stored in `stock_code`. It is case-sensitive. Not every StockCode necessarily identifies a merchandise product.

### 2.2 Description
The recorded text associated with a StockCode, stored in `description`. It may contain a product description, an operational annotation, a correction, or a missing value.

### 2.3 Quantity
The recorded quantity associated with a transaction record. Positive and negative values are both present. A negative value should not automatically be interpreted as a customer return.

### 2.4 Price
The recorded per-unit price stored in `price`, expressed in the dataset's original currency, pounds sterling (GBP). It is not a precomputed invoice-line total.

### 2.5 Invoice Date
The timestamp associated with a transaction record, stored in `invoice_date`. It represents the recorded invoice date and time.

### 2.6 Customer ID
The customer identifier stored in `customer_id`. It can be NULL. A missing Customer ID does not necessarily mean that the transaction is invalid.

### 2.7 Country
The recorded country associated with a transaction record, stored in `country`.

## 3. Analytical and Operational Concepts

### 3.1 Operational Entry
A transaction entry that appears to represent an operational charge, fee, adjustment, or other non-merchandise activity rather than an ordinary merchandise item. The identified operational StockCodes are documented as candidates, not independently verified accounting categories.

### 3.2 Condition Annotation
A description that records a product or inventory condition, such as `damaged`, `broken`, `missing`, or `mouldy`. These annotations should not automatically be interpreted as separate products.

### 3.3 Missing Description
A transaction record whose `description` value is NULL. Missing descriptions are preserved rather than automatically inferred from other StockCodes or records.

### 3.4 Repeated Transaction Record
A transaction observation with the same recorded field values as another observation. Repeated observations are preserved in the consolidated dataset according to the documented duplicate policy.

---

## Usage Notes

- Use the exact database column names when mapping glossary terms to SQL.
- Preserve the distinction between invoice-level and transaction-record-level analysis.
- Do not equate cancellation invoices with all negative-quantity records.
- Do not equate negative quantity with customer returns.
- Do not treat Price as a line total.
- Do not assume all StockCodes represent merchandise.
- Treat missing identifiers and descriptions as data conditions, not automatic evidence of invalid transactions.
- Use operational classifications conservatively and retain the original recorded values.