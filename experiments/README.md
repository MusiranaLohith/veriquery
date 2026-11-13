# VeriQuery Experiment Index

This file is the index for recorded experiments. Result JSONL files are append-only; do not overwrite historical attempts.

## Worker 02 — Full-schema/no-retrieval baseline

| Experiment | Provider/model | Prompt version | Results | Evaluation | Decision |
|---|---|---|---|---|---|
| Groq v2 | Groq `qwen/qwen3.8-27b` | `full-schema-baseline-json-object-v2` | `results/groq_json_object_baseline.jsonl` | `../docs/groq_full_schema_baseline_v2_evaluation.md` | Current comparison baseline |
| Groq v3 | Groq `qwen/qwen3.8-27b` | `full-schema-baseline-json-object-v3` | `results/groq_full_schema_baseline_v3.jsonl` | `../docs/groq_full_schema_baseline_v3_evaluation.md` and `../docs/groq_full_schema_baseline_comparison.md` | Completed candidate; not approved to replace v2 |
| Groq smoke test | Groq | Smoke-test prompt | `results/groq_smoke_test.jsonl` | Integration smoke test only | Not a benchmark |
| Gemini initial attempt | Gemini | Initial full-schema attempt | `results/full_schema_baseline.jsonl` | Recorded provider failure | Not a completed benchmark |
| Groq initial full-schema records | Groq | Earlier prompt | `results/groq_full_schema_baseline.jsonl` | Historical | Do not merge with v2/v3 |

## v2/v3 summary

| Measure | v2 | v3 |
|---|---:|---:|
| Unique successful generations | 40/40 | 40/40 |
| Fully correct | 33 | 32 |
| Partial | 1 | 1 |
| Incorrect | 6 | 7 |
| Answerability matches | 39/40 | 39/40 |

The classifications are manual semantic review, not execution accuracy. Worker 02 did not execute generated SQL. The locked test set was not used.

The v3 JSONL contains 56 append-only attempts for 40 unique questions. Its initial run used `max_completion_tokens=1024` and a 12-second interval; retries used `2048` and 45 seconds. See the v3 report for the full evidence and limitations.

## Preservation rules

- Keep v2 and v3 result files unchanged.
- Do not delete failed attempts; retries append new records.
- Do not combine provider records.
- Do not use locked-test questions or answers for prompt development.
- Do not describe API success, JSON validity or parser acceptance as SQL semantic or execution correctness.
