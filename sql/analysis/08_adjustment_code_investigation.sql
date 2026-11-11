SELECT
    stock_code,
    description,
    COUNT(*) AS transaction_records,
    COUNT(*) FILTER (WHERE quantity < 0) AS negative_quantity_records,
    COUNT(*) FILTER (WHERE quantity > 0) AS positive_quantity_records,
    MIN(invoice_date) AS first_observed,
    MAX(invoice_date) AS last_observed
FROM retail_transactions
WHERE description IS NOT NULL
  AND LOWER(description) ~
      '(adjust|credit|debt|refund|reverse|wrongly|incorrectly|bad debt)'
GROUP BY stock_code, description
ORDER BY transaction_records DESC, stock_code;