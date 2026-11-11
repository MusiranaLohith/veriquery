
-- =====================================================
-- VeriQuery: Detailed StockCode Inventory
-- Workstream 8 - Product Inventory
-- =====================================================

SELECT
    stock_code,

    COUNT(*) AS transaction_records,

    COUNT(DISTINCT description)
        AS distinct_non_null_descriptions,

    COUNT(*) FILTER (
        WHERE description IS NULL
    ) AS missing_description_rows,

    MIN(description) AS alphabetically_first_description,

    MIN(invoice_date) AS first_observed_date,

    MAX(invoice_date) AS last_observed_date,

    MIN(price) AS minimum_price,

    MAX(price) AS maximum_price,

    COUNT(*) FILTER (
        WHERE quantity > 0
    ) AS positive_quantity_records,

    COUNT(*) FILTER (
        WHERE quantity < 0
    ) AS negative_quantity_records

FROM retail_transactions

GROUP BY stock_code

ORDER BY transaction_records DESC, stock_code;
