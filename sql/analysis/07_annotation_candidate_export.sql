SELECT
    stock_code,
    description,
    COUNT(*) AS occurrences,

    CASE
        WHEN LOWER(TRIM(description)) ~
            '^(damaged|damage|damages|broken|faulty|cracked|crushed|mouldy|missing|destroyed|unsaleable|adjustment|amazon adjustment)$'
            OR LOWER(TRIM(description)) LIKE 'adjustment by %'
            OR LOWER(TRIM(description)) LIKE 'incorrectly credited%'
        THEN 'condition_or_adjustment_candidate'

        WHEN LOWER(TRIM(description)) ~
            '^(postage|dotcom postage|amazon fee|bank charges|discount|carriage|cruk commission|manual)$'
        THEN 'operational_entry_candidate'

        WHEN LOWER(TRIM(description)) ~
            '(dotcom|amazon)'
        THEN 'channel_reference_candidate'

        ELSE 'other'
    END AS preliminary_annotation

FROM retail_transactions
WHERE description IS NOT NULL
  AND LOWER(description) ~
      '(damaged|damage|broken|faulty|cracked|crushed|mouldy|missing|destroyed|unsaleable|wrong code|incorrect|adjustment|credited|dotcom|amazon|postage|bank charges|discount|carriage|commission|manual)'

GROUP BY stock_code, description

ORDER BY stock_code, description;