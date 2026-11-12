# VeriQuery — Full-Schema Baseline Methodology

## 1. Purpose

This document defines the methodology for the full-schema, no-retrieval baseline in Worker 02.

The baseline measures SQL-generation behavior when an LLM receives the complete database schema and verified business rules directly in its prompt.

It provides the reference point for later retrieval experiments.

## 2. Dataset and database

The project uses the UCI Online Retail II dataset.

The PostgreSQL database is named `veriquery`.

The relevant table is `retail_transactions`, containing 1,044,848 rows.

The table has these columns:

| Column | Type | Description |
|---|---|---|
| `record_id` | BIGINT | Generated primary key |
| `invoice` | TEXT | Invoice identifier |
| `stock_code` | TEXT | Product stock code |
| `description` | TEXT | Product description |
| `quantity` | INTEGER | Recorded quantity |
| `invoice_date` | TIMESTAMP | Invoice date and time |
| `price` | NUMERIC(12, 3) | Recorded unit price |
| `customer_id` | BIGINT | Nullable customer identifier |
| `country` | TEXT | Country |
| `source_sheet` | TEXT | Source dataset sheet |

The table has one primary key and no foreign keys. The current dataset is single-table; this baseline does not establish general multi-table JOIN capability.

## 3. Development benchmark

The development benchmark is:

`data/benchmark/dev/dev_questions.jsonl`

It contains exactly 40 questions, identified as DEV001 through DEV040.

It is used for prompt development, provider integration testing, structured response testing, development experiments, and investigation of generation failures.

DEV040 asks for net profit by product. The available dataset does not contain a verified cost or profit field. The correct behavior under the current data contract is to identify this question as unanswerable rather than invent a profit calculation.

## 4. Locked test benchmark

The locked test benchmark contains 60 questions and is reserved for final evaluation.

It must not be inspected, used to debug prompts, used to select models, used to tune generation settings, or used to make Worker 02 development decisions.

Development decisions must use the development benchmark and permitted engineering tests.

## 5. Baseline definition

The baseline supplies the LLM with:
1. The natural-language question.
2. The complete `retail_transactions` schema.
3. Verified business rules.
4. Instructions for structured SQL generation.

The baseline excludes:
- BM25 retrieval.
- Dense retrieval.
- Embeddings.
- pgvector.
- Hybrid retrieval.
- Retrieved SQL examples.
- Few-shot SQL examples.
- External schema retrieval.

This is deliberately a full-schema, no-retrieval baseline.

## 6. Prompt and generation contract

The current prompt version is `full-schema-baseline-v1`.

The model returns a structured response containing:
- `is_answerable`
- `sql`
- `interpretation`
- `assumptions`
- `needs_clarification`

Unanswerable questions and questions requiring clarification must not contain generated SQL.

The prompt requests PostgreSQL SQL and restricts generation to read-only SELECT queries, including WITH queries where appropriate.

Worker 02 does not execute generated SQL.

## 7. Provider separation

Gemini and Groq are separate experiments.

Their result files are:
- Gemini: `experiments/results/full_schema_baseline.jsonl`
- Groq: `experiments/results/groq_full_schema_baseline.jsonl`

The Groq integration smoke test is stored separately in `experiments/results/groq_smoke_test.jsonl`.

The smoke test is not a full 40-question baseline and must not be counted as one.

A provider failure must not cause the runner to silently switch providers.

## 8. Experiment records

Each generation attempt is recorded in JSONL with:
- Experiment identifier.
- Provider.
- Question identifier.
- Prompt version.
- Model identifier.
- Timestamp.
- Latency.
- Available prompt, completion, and total token counts.
- API status.
- Error details.
- Structured output, when valid.

Records are appended. Earlier attempts are preserved.

The runner skips previously attempted questions by default. With `--retry-failed`, previously successful questions remain skipped while failed questions can be attempted again.

## 9. Running the baseline

Inspect the selected work without making API calls:

```bash
python -m veriquery.benchmark.run_baseline --provider gemini --dry-run
python -m veriquery.benchmark.run_baseline --provider groq --dry-run

A real benchmark run sends external API requests and requires explicit authorization.

Do not run either provider as part of routine local testing.

## 10. Evaluation boundaries

Worker 02 handles generation and experiment recording. It does not execute generated SQL against PostgreSQL.

Generation success alone does not prove semantic correctness or query executability.

Evaluation must distinguish:
- API/generation success.
- Structured-response validity.
- Answerability classification.
- SQL correctness.
- SQL execution correctness, where assessed by the later authorized evaluation workflow.

No SQL generated by Worker 02 should be executed as part of this baseline-generation workflow.

## 11. Comparison with retrieval experiments

The full-schema baseline is the reference condition for later retrieval experiments.

Later experiments may compare BM25, dense retrieval, and hybrid retrieval.

The pre-registered target is for hybrid retrieval to exceed the full-schema/no-retrieval baseline by at least 5 percentage points on the locked test set.

If hybrid retrieval does not meet that target, the result must be reported honestly. The target must not be changed after observing locked-test results.

## 12. Current evidence and limitations

The current evidence must be kept distinct:

- The Gemini DEV001 attempt returned a provider 503 failure, recorded in `full_schema_baseline.jsonl`.
- The Groq DEV001 smoke test succeeded and returned a structured response, recorded in `groq_smoke_test.jsonl`.
- The Groq smoke test is not evidence of full 40-question benchmark performance.
- A complete 40-question baseline has not been established merely by passing unit tests or dry-runs.

Mocked tests do not establish provider availability, SQL correctness, benchmark accuracy, or retrieval improvement.

Any completion report must state the actual number of attempted, successful, failed, and remaining development questions for each provider.
