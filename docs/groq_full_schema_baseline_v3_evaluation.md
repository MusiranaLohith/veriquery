# Groq Full-Schema Baseline v3 — Semantic Evaluation

**Evaluation date:** 13 November 2026  
**Experiment:** `full-schema-json-object-v3`  
**Prompt version:** `full-schema-baseline-json-object-v3`  
**Provider/model:** Groq — `qwen/qwen3.8-27b`  
**Benchmark:** Development set DEV001–DEV040 (40 questions)  
**Result file:** `experiments/results/groq_full_schema_baseline_v3.jsonl`

## Scope and limitations

This is a manual, static semantic review of the final successful structured response for each development question against `data/benchmark/dev/dev_questions.jsonl`, `data/benchmark/dev/dev_answer_key.jsonl`, and the verified single-table data contract. Generated SQL was **not executed**. The review therefore does not establish PostgreSQL execution correctness or result-set equivalence. A syntax observation is based on the SQL text; it is not a substitute for execution testing.

The locked 60-question test set was not inspected or used. No generated SQL was executed by Worker 02.

## Generation evidence

The append-only v3 result file contains 56 attempt records:
- Initial run: 40 attempted, 25 successful, 15 failed.
- Retry of the 15 failed questions: 14 successful, 1 invalid response (DEV036).
- Targeted retry of DEV036: 1 successful.
- Final unique successful questions: **40/40**.
- Final failed/pending unique questions: **0**.

The initial 25 successful outputs were generated with `max_completion_tokens=1024` and a 12-second request interval. The 15 retry attempts used `max_completion_tokens=2048` and a 45-second interval. DEV036's final successful retry also used the latter configuration. Thus, the final v3 dataset is complete but was generated under two configurations; it must not be described as a fully uniform controlled run.

## Results

| Classification | Count |
|---|---:|
| Fully correct | 32 |
| Partially correct | 1 |
| Incorrect | 7 |
| **Total** | **40** |

Fully correct response rate: **32/40 = 80.0%**.

Of 39 expected-answerable questions, 31 are fully correct, 1 is partial and 7 are incorrect. Fully correct rate among expected-answerable questions: **31/39 = 79.5%**.

Answerability classification matches the benchmark for **39/40** questions. DEV013 is incorrectly marked unanswerable; DEV040 is correctly marked unanswerable. The model returned SQL for 38 questions.

These are manual semantic classifications, not execution-based accuracy.

## Question-level assessment

| Question | Assessment | Finding |
|---|---|---|
| DEV001 | Correct | Counts all transaction rows. |
| DEV002 | Correct | Counts distinct invoices. |
| DEV003 | Correct | Counts distinct StockCodes. |
| DEV004 | Correct | Counts distinct countries and non-NULL customer IDs. |
| DEV005 | Correct | Counts rows with quantity > 0. |
| DEV006 | Correct | Counts rows with quantity < 0. |
| DEV007 | Correct | Uses strict price > 100 threshold. |
| DEV008 | Correct | Uses inclusive price >= 500 threshold; COUNT(record_id) is equivalent to COUNT(*) because record_id is the non-NULL primary key. |
| DEV009 | Correct | Groups by country and ranks record counts. |
| DEV010 | Incorrect | Missing whitespace in `WHEREinvoice_date`; invalid SQL syntax. |
| DEV011 | Correct | Uses DATE_TRUNC month, preserving calendar year-month identity. |
| DEV012 | Correct | Sums recorded quantity across all rows. |
| DEV013 | Incorrect | Returns unanswerable/clarification with NULL SQL although AVG(price) is supported. |
| DEV014 | Correct | Correct country count threshold and aggregation. |
| DEV015 | Correct | Correct country-level SUM(quantity) ranking. |
| DEV016 | Correct | Correct half-open timestamp range for Q1 2011. |
| DEV017 | Partial | Returns EXTRACT(DOW) numeric code, not weekday name and ISO weekday number requested by reference; partial output. |
| DEV018 | Correct | Partitions month ranking by calendar year and month. |
| DEV019 | Correct | Groups by calendar year. |
| DEV020 | Correct | Counts NULL customer IDs. |
| DEV021 | Correct | Counts NULL descriptions. |
| DEV022 | Correct | Counts rows where both fields are NULL. |
| DEV023 | Correct | Correct top-10 country aggregation for NULL customer IDs. |
| DEV024 | Incorrect | References invoice_count and record_count without defining aggregates; invalid grouped query. |
| DEV025 | Correct | Correct known-customer country aggregation. |
| DEV026 | Correct | Correct top-10 average records per known customer; answer-key SQL has LIMIT 1 despite question asking for 10, so evaluation follows question wording. |
| DEV027 | Correct | Excludes NULL customer IDs and returns requested customer metrics. |
| DEV028 | Correct | Correct StockCode record-count and quantity aggregation. |
| DEV029 | Incorrect | Filters NULL descriptions before COUNT(*), so transaction-record counts are understated. |
| DEV030 | Incorrect | Identifies the 12 codes and counts negative records, but omits transaction-record count required by reference output; also only returns codes with negative rows. |
| DEV031 | Correct | Correctly counts missing-description rows by StockCode. |
| DEV032 | Correct | Correct C-prefixed versus other invoice grouping and requested metrics. |
| DEV033 | Correct | Correct negative-quantity grouping by invoice type. |
| DEV034 | Incorrect | Adds unsupported exclusion of operational StockCodes and omits total quantity; question/reference ask about C-prefixed invoices generally. |
| DEV035 | Correct | Correct price-sign counts by invoice type. |
| DEV036 | Correct | Filters to customer-known positive-quantity rows before invoice count and quantity aggregation; aligns with reference. |
| DEV037 | Correct | Correct known-customer filter and requested metrics; SQL matches reference. |
| DEV038 | Incorrect | Eligibility uses qualifying rows, but reported aggregates are calculated across all rows for each StockCode; reference calculates requested metrics over rows meeting numeric-code, price and quantity filters. |
| DEV039 | Correct | Groups by DATE_TRUNC month, so each calendar month is distinct across years; includes requested measures and thresholds. |
| DEV040 | Correct | Correctly refuses net-profit calculation because verified cost/profit inputs are absent. |

## Principal findings

### Improvements over v2
- DEV011 uses calendar-month `DATE_TRUNC` rather than invalid `MONTH()` and month-number grouping.
- DEV027 excludes NULL customer IDs from customer ranking.
- DEV030 recognizes the verified operational-entry StockCode context and no longer refuses the question. Its generated result remains incomplete.
- DEV036 filters positive-quantity records before counting invoices and summing quantity.
- DEV039 groups by calendar month rather than month number alone.

### Regressions or remaining errors
- DEV010 contains `WHEREinvoice_date` without a separating space, making the SQL text invalid.
- DEV013 incorrectly refuses a supported `AVG(price)` calculation.
- DEV024 references `invoice_count` and `record_count` without defining those aggregates.
- DEV029 filters out NULL descriptions before `COUNT(*)`, changing transaction-record counts.
- DEV030 omits the requested transaction-record count and does not represent operational codes with zero negative-quantity records.
- DEV034 excludes operational StockCodes without support from the question and omits total quantity.
- DEV038 uses qualifying records for eligibility but calculates displayed metrics over all records for each qualifying StockCode, unlike the answer-key population.
- DEV017 returns a numeric `EXTRACT(DOW)` value rather than the weekday name and ISO weekday number specified by the reference output.

### Answer-key caveat
DEV026's natural-language question asks for the top 10 countries, and v3 uses `LIMIT 10`. The supplied reference SQL ends with `LIMIT 1`, which conflicts with the question wording. The review follows the question wording and treats the v3 limit as correct. This answer-key inconsistency should be corrected in the development answer key in a separately controlled benchmark-maintenance action; it does not justify changing the locked test set.

## Mechanical and execution limitations

This report does not claim SQLGlot parsing, PostgreSQL execution, read-only enforcement, or result-set equivalence for all v3 outputs. API success and Pydantic response validity are not semantic correctness. No database execution was performed as part of this review.

## Decision

**Do not lock v3 as the full-schema baseline.** It has 32 fully correct responses compared with 33 in v2, and it introduces material regressions in DEV010, DEV013, DEV024 and DEV038, while retaining other semantic issues. Preserve v3 as an immutable experiment. Keep v2 as the current comparison baseline, with its known limitations and the DEV037 report correction documented in the comparison report.
