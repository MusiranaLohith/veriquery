
-- =====================================================
-- VeriQuery: Numeric-only StockCode Review
-- Workstream 8 - Product Inventory
-- =====================================================

SELECT
    stock_code,

    COUNT(*) AS transaction_records,

    COUNT(DISTINCT description)
        AS distinct_non_null_descriptions,

    STRING_AGG(
        DISTINCT description,
        ' | '
        ORDER BY description
    ) AS recorded_descriptions,

    COUNT(*) FILTER (
        WHERE description IS NULL
    ) AS missing_description_rows,

    COUNT(*) FILTER (
        WHERE quantity < 0
    ) AS negative_quantity_records,

    COUNT(*) FILTER (
        WHERE quantity > 0
    ) AS positive_quantity_records

FROM retail_transactions

WHERE stock_code ~ '^[0-9]+$'

GROUP BY stock_code

ORDER BY transaction_records DESC, stock_code;
