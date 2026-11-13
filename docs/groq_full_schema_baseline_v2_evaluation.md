# Groq Full-Schema Baseline v2 --- Semantic Evaluation

**Evaluation date:** 2026-11-13\
**Experiment:** `full-schema-json-object-v2`\
**Prompt version:** `full-schema-baseline-json-object-v2`\
**Provider/model:** Groq --- `qwen/qwen3.8-27b`\
**Benchmark:** Development set, DEV001--DEV040 (40 questions)

## Scope and limitations

This is a static semantic review against the development questions,
benchmark answer key, and verified schema/business context. No generated
SQL was executed against PostgreSQL. This report does not claim
execution accuracy or result-set equivalence. SQLGlot parsing is a
mechanical check, not proof of PostgreSQL validity or semantic
correctness. The locked 60-question test set was not accessed.

## Results

  Classification        Count
  ------------------- -------
  Fully correct            33
  Partially correct         1
  Incorrect                 6
  Total                    40

Fully correct response rate: **33/40 = 82.5%**.

Among 39 expected-answerable questions: 32 fully correct, 1 partial, 6
incorrect; fully correct rate **32/39 = 82.1%**.

Among 38 responses that generated SQL: 32 fully correct, 1 partial, 5
incorrect. These are manual semantic classifications, not
execution-based accuracy.

## Question-level assessment

  -----------------------------------------------------------------------
  Question                Assessment              Finding
  ----------------------- ----------------------- -----------------------
  DEV001                  Correct                 Counts all rows.

  DEV002                  Correct                 Counts distinct
                                                  invoices.

  DEV003                  Correct                 Counts distinct
                                                  StockCodes.

  DEV004                  Correct                 Counts distinct
                                                  countries and known
                                                  customers.

  DEV005                  Correct                 Correct
                                                  positive-quantity
                                                  filter.

  DEV006                  Correct                 Correct
                                                  negative-quantity
                                                  filter.

  DEV007                  Correct                 Correct strict price
                                                  threshold.

  DEV008                  Correct                 Correct inclusive price
                                                  threshold.

  DEV009                  Correct                 Correct country
                                                  aggregation and
                                                  ranking.

  DEV010                  Correct                 Correct November 2011
                                                  date range.

  DEV011                  Incorrect               Uses `MONTH()`, not a
                                                  PostgreSQL function,
                                                  and groups month
                                                  numbers across years.

  DEV012                  Correct                 Correct sum of all
                                                  recorded quantities.

  DEV013                  Correct                 Correct arithmetic
                                                  average, rounded to two
                                                  decimals.

  DEV014                  Correct                 `COUNT(record_id)`
                                                  equals `COUNT(*)`
                                                  because the primary key
                                                  cannot be NULL.

  DEV015                  Correct                 Correct country-level
                                                  quantity aggregation.

  DEV016                  Correct SQL;            SQL selects Q1 2011,
                          explanation             but an assumption says
                          inconsistency           first half of 2011.

  DEV017                  Correct                 Correct weekday
                                                  aggregation.

  DEV018                  Correct                 Ranks months separately
                                                  within each year.

  DEV019                  Correct SQL; minor      Correct yearly
                          explanation issue       grouping; UNIX epoch
                                                  assumption is
                                                  irrelevant.

  DEV020                  Correct                 Correct
                                                  missing-customer count.

  DEV021                  Correct                 Correct
                                                  missing-description
                                                  count.

  DEV022                  Correct                 Correct combined NULL
                                                  condition.

  DEV023                  Correct                 Correct top-10
                                                  missing-customer
                                                  country aggregation.

  DEV024                  Correct                 Correct known-customer
                                                  invoice and record
                                                  counts.

  DEV025                  Correct                 Correct known-customer
                                                  filtering before both
                                                  counts.

  DEV026                  Correct                 Correct average records
                                                  per known customer and
                                                  minimum threshold.

  DEV027                  Incorrect               Includes NULL customer
                                                  IDs as a customer
                                                  group.

  DEV028                  Correct                 Correct StockCode
                                                  aggregation.

  DEV029                  Incorrect               Filters out NULL
                                                  descriptions before
                                                  `COUNT(*)`, reducing
                                                  transaction-record
                                                  counts.

  DEV030                  Incorrect answerability Marks an answerable
                                                  question unanswerable
                                                  because v2 lacks the 12
                                                  operational-entry
                                                  StockCodes.

  DEV031                  Correct                 Correct
                                                  missing-description
                                                  grouping.

  DEV032                  Correct                 Correct C-prefixed
                                                  versus other invoice
                                                  comparison.

  DEV033                  Correct                 Correct
                                                  negative-quantity
                                                  comparison.

  DEV034                  Incorrect               Does not exclude
                                                  C-prefixed invoices
                                                  with zero
                                                  non-negative-quantity
                                                  records.

  DEV035                  Correct                 Correct price-sign
                                                  classification and
                                                  grouping.

  DEV036                  Partial                 Distinct invoice count
                                                  includes negative-only
                                                  records, while the
                                                  benchmark reference
                                                  filters positive
                                                  quantities before
                                                  aggregation.

  DEV037                  Correct SQL;            SQL matches
                          explanation             known-customer
                          inconsistency           filtering, but the
                                                  assumption says metrics
                                                  include all records.

  DEV038                  Correct                 Correct numeric
                                                  StockCode, price and
                                                  quantity filters and
                                                  aggregations.

  DEV039                  Incorrect               Groups by month number,
                                                  merging the same month
                                                  across years.

  DEV040                  Correct                 Correctly refuses to
                                                  calculate net profit
                                                  without verified
                                                  cost/profit
                                                  information.
  -----------------------------------------------------------------------

## Main error patterns

1.  **Date reasoning:** DEV011 and DEV039 show problems with
    calendar-month grouping.
2.  **NULL handling:** DEV027 and DEV029 show incorrect handling of
    missing values.
3.  **Filtering:** DEV034 fails to exclude groups that do not meet the
    requested condition.
4.  **Business context:** DEV030 shows that missing business context can
    cause an incorrect refusal.
5.  **Aggregation scope:** DEV036 differs from the benchmark's
    positive-quantity aggregation scope.

Explanation-quality issues: DEV016 has a period mismatch; DEV019 has an
irrelevant UNIX epoch assumption; DEV037's explanation contradicts its
SQL filtering.

## Mechanical checks (separate from semantic quality)

The offline evaluator recorded 40 experiment records and 40 benchmark
questions; 40 successful API generations; 40/40 structured
response-contract passes; 38 SQL parse passes and 0 parse failures among
generated SQL; 38 read-only checks passed; 39 answerability matches and
1 mismatch (DEV030); and 8 known semantic findings.

Parser acceptance does not guarantee PostgreSQL validity. DEV011 is an
example.

## Baseline conclusion

The v2 full-schema baseline handles many straightforward analytical
questions correctly, but has weaknesses in calendar-month reasoning,
NULL handling, conditional group filtering, and business-context
interpretation. Preserve v2 as a historical baseline; do not overwrite
it with v3 results.

## Next evaluation

Evaluate prompt v3 on the same 40 development questions using a separate
append-only experiment result file. Compare v3 against this v2
assessment, especially whether the additional verified operational-entry
StockCode context resolves DEV030 and whether regressions appear. Do not
access or tune against the locked 60-question test set. Do not execute
generated SQL.

## Historical clarification (13 November 2026)

DEV037's SQL applies `WHERE customer_id IS NOT NULL` before grouping and matches the supplied DEV037 reference SQL. Its assumption text contradicts the SQL, but this is an explanation inconsistency rather than a semantic SQL error. The earlier narrative's description of this as a semantic error should not be carried forward. The reported aggregate classification remains unchanged because DEV037 was counted as correct SQL in the 33/1/6 totals.

DEV026's natural-language question asks for 10 countries, while its supplied reference SQL ends with `LIMIT 1`. The question wording and reference SQL are inconsistent. The v3 comparison follows the natural-language request for 10; the benchmark answer key should be reconciled in a separately controlled development-set maintenance action.
