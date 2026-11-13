# Groq JSON-object v2 — Offline Evaluation

> Historical v2 outputs evaluated offline. No SQL was executed.

## Summary

- **experiment_records:** 40
- **benchmark_questions:** 40
- **api_successes:** 40
- **contract_passed:** 40
- **contract_failed:** 0
- **sql_parse_passed:** 38
- **sql_parse_failed:** 0
- **read_only_passed:** 38
- **read_only_failed:** 0
- **answerability_matches:** 39
- **answerability_mismatches:** 1
- **known_semantic_findings:** 8
- **duplicate_question_ids:** []
- **missing_question_ids:** []
- **unexpected_question_ids:** []
- **prompt_versions:** ['full-schema-baseline-json-object-v2']
- **expected_prompt_version:** full-schema-baseline-json-object-v2
- **sqlglot_version:** 30.31.0

## Per-question findings

| ID | Contract | PostgreSQL parse | Read-only | Answerability | Semantic review |
|---|---|---|---|---|---|
| DEV001 | passed | passed | passed | True | not_flagged |
| DEV002 | passed | passed | passed | True | not_flagged |
| DEV003 | passed | passed | passed | True | not_flagged |
| DEV004 | passed | passed | passed | True | not_flagged |
| DEV005 | passed | passed | passed | True | not_flagged |
| DEV006 | passed | passed | passed | True | not_flagged |
| DEV007 | passed | passed | passed | True | not_flagged |
| DEV008 | passed | passed | passed | True | not_flagged |
| DEV009 | passed | passed | passed | True | not_flagged |
| DEV010 | passed | passed | passed | True | not_flagged |
| DEV011 | passed | passed | passed | True | known_issue |
| DEV012 | passed | passed | passed | True | not_flagged |
| DEV013 | passed | passed | passed | True | not_flagged |
| DEV014 | passed | passed | passed | True | not_flagged |
| DEV015 | passed | passed | passed | True | not_flagged |
| DEV016 | passed | passed | passed | True | known_issue |
| DEV017 | passed | passed | passed | True | not_flagged |
| DEV018 | passed | passed | passed | True | not_flagged |
| DEV019 | passed | passed | passed | True | known_issue |
| DEV020 | passed | passed | passed | True | not_flagged |
| DEV021 | passed | passed | passed | True | not_flagged |
| DEV022 | passed | passed | passed | True | not_flagged |
| DEV023 | passed | passed | passed | True | not_flagged |
| DEV024 | passed | passed | passed | True | not_flagged |
| DEV025 | passed | passed | passed | True | not_flagged |
| DEV026 | passed | passed | passed | True | not_flagged |
| DEV027 | passed | passed | passed | True | known_issue |
| DEV028 | passed | passed | passed | True | not_flagged |
| DEV029 | passed | passed | passed | True | known_issue |
| DEV030 | passed | not_applicable | not_applicable | False | not_flagged |
| DEV031 | passed | passed | passed | True | not_flagged |
| DEV032 | passed | passed | passed | True | not_flagged |
| DEV033 | passed | passed | passed | True | not_flagged |
| DEV034 | passed | passed | passed | True | known_issue |
| DEV035 | passed | passed | passed | True | not_flagged |
| DEV036 | passed | passed | passed | True | not_flagged |
| DEV037 | passed | passed | passed | True | known_issue |
| DEV038 | passed | passed | passed | True | not_flagged |
| DEV039 | passed | passed | passed | True | known_issue |
| DEV040 | passed | not_applicable | not_applicable | True | not_flagged |

## Known semantic findings

- **DEV011 (critical):** Uses MONTH() and invalid month-name conversion.
- **DEV016 (moderate):** SQL filters Q1 2011, but assumption describes the first half.
- **DEV019 (minor):** Irrelevant UNIX epoch calendar assumption.
- **DEV027 (moderate):** May report the NULL customer_id group as a customer.
- **DEV029 (critical):** Filters NULL descriptions before COUNT(*), changing the record count.
- **DEV034 (moderate):** Does not exclude C-prefixed invoices with zero qualifying records.
- **DEV037 (critical):** Filters NULL customer IDs before calculating all-record metrics.
- **DEV039 (moderate):** Groups by month number across years; calendar months must remain separate.

## Interpretation limitations

- SQL parsing is not proof of semantic correctness.
- Read-only AST checks are static checks, not database execution.
- `not_flagged` means no issue was registered in the initial manual review; it does not mean the query is proven correct.
- The benchmark's answerability labels are used as the comparison reference, not as proof of SQL correctness.
- Historical v2 outputs are not relabelled as v3 generations.
