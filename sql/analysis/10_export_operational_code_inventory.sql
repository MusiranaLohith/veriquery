SELECT
    stock_code,
    COUNT(*) AS transaction_records,
    COUNT(DISTINCT description)
        FILTER (WHERE description IS NOT NULL)
        AS distinct_descriptions,
    STRING_AGG(
        DISTINCT description,
        ' | '
        ORDER BY description
    ) FILTER (WHERE description IS NOT NULL)
        AS recorded_descriptions,
    COUNT(*) FILTER (WHERE quantity < 0)
        AS negative_quantity_records,
    COUNT(*) FILTER (WHERE quantity > 0)
        AS positive_quantity_records,
    MIN(invoice_date) AS first_observed,
    MAX(invoice_date) AS last_observed
FROM retail_transactions
WHERE stock_code IN (
    'AMAZONFEE',
    'B',
    'BANK CHARGES',
    'C2',
    'CRUK',
    'D',
    'DOT',
    'M',
    'POST',
    'ADJUST',
    'ADJUST2',
    'm'
)
GROUP BY stock_code
ORDER BY transaction_records DESC, stock_code;