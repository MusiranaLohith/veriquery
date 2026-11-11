
-- =====================================================
-- VeriQuery: Description Annotation Investigation
-- Workstream 8 - Product Inventory
-- =====================================================

-- 1. Count codes with descriptions containing
--    operational or condition-related keywords.

WITH description_flags AS (
    SELECT
        stock_code,
        description,

        CASE
            WHEN description ~*
                '(damaged|damage|broken|faulty|cracked|crushed|mouldy|missing|destroyed|unsaleable|wrong code|incorrect|adjustment|credited)'
            THEN TRUE
            ELSE FALSE
        END AS condition_or_adjustment_annotation,

        CASE
            WHEN description ~*
                '(dotcom|amazon)'
            THEN TRUE
            ELSE FALSE
        END AS channel_annotation

    FROM retail_transactions
    WHERE description IS NOT NULL
)

SELECT
    COUNT(DISTINCT stock_code) AS total_codes_with_descriptions,

    COUNT(DISTINCT stock_code) FILTER (
        WHERE condition_or_adjustment_annotation
    ) AS codes_with_condition_or_adjustment_annotations,

    COUNT(DISTINCT stock_code) FILTER (
        WHERE channel_annotation
    ) AS codes_with_channel_annotations

FROM description_flags;


-- 2. Show matching descriptions for manual review.

SELECT
    stock_code,
    description,
    COUNT(*) AS occurrences

FROM retail_transactions

WHERE description ~*
    '(damaged|damage|broken|faulty|cracked|crushed|mouldy|missing|destroyed|unsaleable|wrong code|incorrect|adjustment|credited|dotcom|amazon)'

GROUP BY stock_code, description

ORDER BY occurrences DESC, stock_code

LIMIT 100;
