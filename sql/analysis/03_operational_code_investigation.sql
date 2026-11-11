-- =====================================================
-- VeriQuery: Known Operational Code Investigation
-- Workstream 8 - Product Inventory
-- =====================================================

SELECT
    stock_code,
    COUNT(*) AS transaction_records,
    COUNT(DISTINCT description) AS distinct_descriptions,
    STRING_AGG(
        DISTINCT description,
        ' | '
        ORDER BY description
    ) AS recorded_descriptions,
    SUM(quantity) AS net_quantity,
    COUNT(*) FILTER (WHERE quantity < 0) AS negative_quantity_records,
    COUNT(*) FILTER (WHERE quantity > 0) AS positive_quantity_records,
    MIN(price) AS minimum_price,
    MAX(price) AS maximum_price
FROM retail_transactions
WHERE stock_code IN (
    'M',
    'B',
    'D',
    'POST',
    'DOT',
    'BANK CHARGES',
    'AMAZONFEE',
    'C2',
    'CRUK'
)
GROUP BY stock_code
ORDER BY stock_code;