
-- =====================================================
-- VeriQuery: StockCode Population Overview
-- Workstream 8 - Product Inventory
-- =====================================================

-- 1. Total transaction observations
SELECT
    COUNT(*) AS total_records
FROM retail_transactions;


-- 2. Distinct StockCodes
SELECT
    COUNT(DISTINCT stock_code) AS distinct_stock_codes
FROM retail_transactions;


-- 3. StockCode format distribution
-- This is a structural observation, NOT a product classification.

SELECT
    CASE
        WHEN stock_code ~ '^[0-9]+$'
            THEN 'Numeric-only'
        ELSE 'Contains non-numeric characters'
    END AS code_format,
    COUNT(DISTINCT stock_code) AS distinct_codes,
    COUNT(*) AS transaction_records
FROM retail_transactions
GROUP BY code_format
ORDER BY code_format;


-- 4. StockCodes with multiple descriptions

SELECT
    COUNT(*) AS codes_with_multiple_descriptions
FROM (
    SELECT
        stock_code
    FROM retail_transactions
    WHERE description IS NOT NULL
    GROUP BY stock_code
    HAVING COUNT(DISTINCT description) > 1
) AS description_variants;


-- 5. StockCodes with no recorded description

SELECT
    COUNT(DISTINCT stock_code) AS codes_without_description
FROM retail_transactions
WHERE description IS NULL;
