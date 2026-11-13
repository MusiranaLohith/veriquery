# Groq Full-Schema Baseline — v2 vs v3 Comparison

**Date:** 13 November 2026  
**Benchmark:** DEV001–DEV040 (40 development questions)  
**v2 experiment:** `full-schema-json-object-v2`  
**v3 experiment:** `full-schema-json-object-v3`  
**Provider/model:** Groq — `qwen/qwen3.8-27b`

## Decision

**v2 remains the current comparison baseline. v3 is not approved to replace or lock the baseline.** Preserve both append-only result files. v3's generation is complete (40/40 unique successful outputs), but its manual semantic score is lower and it introduces material regressions.

## Aggregate comparison

| Measure | v2 | v3 |
|---|---:|---:|
| Unique successful generations | 40/40 | 40/40 |
| Fully correct | 33/40 (82.5%) | 32/40 (80.0%) |
| Partial | 1/40 | 1/40 |
| Incorrect | 6/40 | 7/40 |
| Answerability matches | 39/40 | 39/40 |
| Fully correct among 39 expected-answerable questions | 32/39 (82.1%) | 31/39 (79.5%) |

Manual semantic classifications; no generated SQL was executed. The rates should not be interpreted as PostgreSQL execution accuracy.

## Per-question comparison

| Question | v2 | v3 | Comparison |
|---|---|---|---|
| DEV001 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV002 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV003 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV004 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV005 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV006 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV007 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV008 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV009 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV010 | Correct | Incorrect | Regression: v2 date-range SQL was syntactically valid; v3 has a missing space after WHERE. |
| DEV011 | Incorrect | Correct | v3 fixes invalid MONTH() and merges no different years; uses calendar-month DATE_TRUNC. |
| DEV012 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV013 | Correct | Incorrect | Regression: v2 correctly uses ROUND(AVG(price), 2); v3 incorrectly refuses an answerable average-price request. |
| DEV014 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV015 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV016 | Correct* | Correct | Both SQL queries correctly select Q1 2011; v2 has an inconsistent explanation, v3 explanation is aligned. |
| DEV017 | Correct | Partial | Regression in output detail: v2 returns weekday name; v3 returns only EXTRACT(DOW) numeric code, not requested weekday label/ISO number. |
| DEV018 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV019 | Correct* | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV020 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV021 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV022 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV023 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV024 | Correct | Incorrect | Regression: v2 defines COUNT(DISTINCT invoice) and COUNT(*); v3 references undefined invoice_count and record_count columns. |
| DEV025 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV026 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV027 | Incorrect | Correct | v3 fixes NULL-customer grouping by excluding unknown customer IDs. |
| DEV028 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV029 | Incorrect | Incorrect | Unchanged error: both versions filter NULL descriptions before COUNT(*), understating transaction records. |
| DEV030 | Incorrect | Incorrect | v3 fixes v2 refusal using the 12-code business rule, but omits total transaction-record count and only returns codes with negative rows. |
| DEV031 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV032 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV033 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV034 | Incorrect | Incorrect | Unresolved/changed error: v2 does not enforce HAVING positive-record count > 0; v3 adds this condition but introduces unsupported operational-code exclusions and omits SUM(quantity). |
| DEV035 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |
| DEV036 | Partial | Correct | v3 fixes v2 invoice-count population by filtering quantity > 0 before aggregation. |
| DEV037 | Correct* | Correct | Both SQL queries match the answer-key known-customer filter; v2 assumption contradicts its SQL. Correct the earlier v2 report wording. |
| DEV038 | Correct | Incorrect | Regression: v2 aggregates the requested qualifying rows; v3 eligibility uses qualifying rows but reported metrics aggregate across all records for qualifying StockCodes. |
| DEV039 | Incorrect | Correct | v3 fixes month-number-only grouping by grouping on DATE_TRUNC calendar month. |
| DEV040 | Correct | Correct | No material semantic difference identified in this manual comparison; both responses align with the development reference intent. |

## Improvements in v3

- **DEV011:** Corrects invalid `MONTH()` usage and groups by full calendar month.
- **DEV027:** Excludes NULL customer IDs from customer ranking.
- **DEV030:** Uses the newly supplied 12-code operational-entry context and correctly recognizes the question as answerable. The output still omits one requested metric.
- **DEV036:** Filters to positive-quantity rows before invoice counting and quantity summation, correcting v2's population mismatch.
- **DEV039:** Groups by full calendar month, avoiding month-number collisions across years.

## Regressions and unresolved issues

- **DEV010:** v3 has invalid `WHEREinvoice_date` syntax; v2's date-range SQL was valid.
- **DEV013:** v3 refuses a supported average-price query that v2 answered correctly.
- **DEV017:** v3 returns a numeric weekday code rather than the requested weekday name/ISO number.
- **DEV024:** v3 references undefined aggregate aliases; v2 correctly defined the invoice and record counts.
- **DEV029:** Both versions filter NULL descriptions before `COUNT(*)`, changing the transaction-record population.
- **DEV030:** v3 fixes answerability but omits total transaction-record count and does not include codes with zero negative-quantity records.
- **DEV034:** v2 fails to enforce the positive-record group condition. v3 adds that condition but also applies unsupported operational-code exclusions and omits total quantity. Neither fully matches the reference.
- **DEV038:** v3 changes the aggregation population: eligibility is based on qualifying rows, but displayed metrics are aggregated across all records for each qualifying StockCode.

## Correction to the historical v2 evaluation

The earlier v2 report labels DEV037 as “Correct SQL; explanation inconsistency” and lists it among explanation-quality issues. Its SQL applies `WHERE customer_id IS NOT NULL` before grouping, which matches the supplied DEV037 reference SQL. The answer key supports the SQL's known-customer filtering. The assumption text contradicts the SQL, but this should be treated as an explanation inconsistency, not a semantic SQL error. The historical aggregate score of 33 fully correct, 1 partial and 6 incorrect remains unchanged because DEV037 was counted as correct SQL in that score.

DEV026 also has an answer-key inconsistency: the natural-language question asks for 10 countries, while the reference SQL ends in `LIMIT 1`. v3 uses `LIMIT 10`, consistent with the question wording. This comparison does not alter the benchmark files.

## Experiment configuration caveat

The v3 result file contains 56 append-only attempts for 40 unique questions:
- Initial run: 40 attempts, 25 successes, 15 failures; generation settings `max_completion_tokens=1024`, 12-second interval.
- Retry: 15 attempts, 14 successes, 1 invalid response; settings `max_completion_tokens=2048`, 45-second interval.
- Final targeted retry: DEV036 succeeded with `max_completion_tokens=2048`, 45-second interval.

The final successful output for every question is present, but v3 was not generated under one uniform configuration. Do not present it as a controlled same-settings comparison with v2.

## Baseline and next-step decision

1. Retain v2 as the current full-schema/no-retrieval comparison baseline.
2. Preserve v3 as a completed but rejected candidate experiment.
3. Do not inspect or tune against the locked test set.
4. Do not execute generated SQL in Worker 02.
5. If a later prompt revision is authorized, address only evidenced development-set errors and version it as a new experiment. Do not overwrite v2 or v3.

The hybrid retrieval target (at least +5 percentage points over the full-schema baseline on the locked test) remains a future evaluation target, not a result established in Phase 2.
