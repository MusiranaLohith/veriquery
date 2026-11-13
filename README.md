# VeriQuery

**Trustworthy Natural-Language Analytics for Relational Databases**

VeriQuery is a research-oriented project exploring how retrieval-grounded context can improve the accuracy of translating natural-language questions into SQL.

The project focuses on reducing common Text-to-SQL problems, including incorrect schema references, misunderstood business terminology, incorrect database-value matching and inaccurate SQL generation.

## Project Status

**Current milestone:** Phase 2 — LLM Integration and Full-Schema Baseline — completed on 13 November 2026.

Phase 1 established the dataset, PostgreSQL table, business context and 40-question development / 60-question locked-test benchmark. Phase 2 implemented the Groq LLM integration, structured SQL response contract, versioned full-schema/no-retrieval prompts, append-only experiment recording and development benchmark evaluation. The v2 experiment remains the current comparison baseline; v3 was evaluated but not approved to replace it.

## Technology Stack

- Python 3.11
- PostgreSQL
- SQL
- Pandas
- NumPy
- psycopg
- JSONL-based benchmark datasets

## Phase 1 — Completed Work

### 1. Dataset Investigation and Engineering

- Selected the UCI Online Retail II dataset.
- Investigated missing values, duplicate records, overlapping records and transaction anomalies.
- Consolidated the source workbook into a unified retail transaction dataset.
- Defined a formal dataset contract.
- Loaded the consolidated dataset into PostgreSQL.

### 2. Product Inventory and Business Understanding

- Investigated numeric and non-numeric StockCode values.
- Identified operational-entry candidates.
- Prepared product inventory reports and annotation candidates.
- Created a business glossary to document relevant retail terminology and dataset semantics.

### 3. Benchmark Construction

Constructed a 100-question Text-to-SQL benchmark:

| Split | Questions | Purpose |
|---|---:|---|
| Development | 40 | Development and experimentation |
| Locked test | 60 | Final evaluation |
| **Total** | **100** | |

The benchmark includes schema understanding, filtering, aggregation, date analysis, NULL handling, customer and country analysis, product-value analysis, cancellation patterns and multi-condition analytical reasoning.

Four questions are explicitly classified as unanswerable because the required information is absent from the database.

### 4. Validation and Evaluation Design

- Validated question and answer-key structure.
- Checked development/test separation.
- Audited question diversity and difficulty.
- Executed all 56 answerable locked-test reference queries against PostgreSQL.
- Verified expected results against actual database outputs.
- Documented result-comparison rules and benchmark limitations.

**Latest validation evidence:**
- Benchmark structure: PASSED.
- Development questions: 40.
- Locked-test questions: 60.
- Development/test ID overlap: 0.
- Answerable locked-test SQL queries: 56/56 passed.
- Unanswerable locked-test questions: 4 correctly identified.

The locked-test questions and answer keys are intentionally excluded from this public repository to preserve evaluation integrity.

## Dataset

**Source:** UCI Online Retail II

https://archive.ics.uci.edu/dataset/502/online+retail+ii

The project currently uses one retail dataset, one business domain and one PostgreSQL transaction table: `retail_transactions`.

The dataset contains approximately 1.04 million transaction records.

### Current limitations

- Single retail dataset and business domain.
- One primary database table.
- No verified foreign-key relationships or multi-table JOIN evaluation.
- No demonstrated generalization across multiple databases or domains.

These limitations are explicitly documented rather than hidden.

## Repository Structure

```text
veriquery/
├── data/
│   └── benchmark/
│       └── dev/
├── reports/
│   ├── benchmark/
│   ├── data_quality/
│   └── product_inventory/
├── scripts/
│   ├── benchmark/
│   ├── database/
│   └── inspection/
├── sql/
│   ├── analysis/
│   └── schema/
├── .gitignore
└── README.md
```

Raw and processed dataset files are excluded from Git because of their size. The locked-test materials are also excluded.

## Phase 2 — LLM Integration and Full-Schema Baseline

Completed 13 November 2026.

- Integrated Groq (`qwen/qwen3.8-27b`) as an explicitly selected provider.
- Implemented structured Pydantic response validation and JSON-object generation.
- Built versioned full-schema/no-retrieval prompts with verified schema and business rules.
- Added append-only JSONL experiment records, resume/retry behavior and rate-limit-aware request spacing.
- Generated and manually reviewed v2 and v3 against the 40-question development benchmark.
- Preserved all historical attempts; v3 has 40/40 final successful unique outputs.

### Baseline decision

The v2 full-schema/no-retrieval experiment remains the current comparison baseline (33/40 fully correct in manual semantic review). v3 achieved 32/40 and was not approved to replace v2. These are static manual semantic assessments, not SQL execution accuracy. See:

- `docs/groq_full_schema_baseline_v2_evaluation.md`
- `docs/groq_full_schema_baseline_v3_evaluation.md`
- `docs/groq_full_schema_baseline_comparison.md`

### Phase 2 limitations

Generated SQL was not executed as part of Worker 02. This phase does not establish PostgreSQL execution accuracy, safe execution, general multi-table JOIN capability, or retrieval improvement. The locked test set was not used.

## Planned Development

The next workstream is retrieval-grounded context construction and evaluation, followed by controlled SQL validation and safe read-only execution:

1. BM25 and dense retrieval.
2. Hybrid retrieval and evidence selection.
3. Retrieval-grounded SQL generation compared with the full-schema baseline.
4. SQL validation, read-only enforcement and controlled execution (separate execution workstream).
5. Evaluation and production engineering.

The primary evaluation objective remains to investigate whether hybrid retrieval improves SQL correctness by at least five percentage points over the full-schema/no-retrieval baseline on the locked test set. This is a target, not an achieved result.

The primary evaluation objective is to investigate whether hybrid retrieval improves SQL correctness by at least five percentage points over a full-schema/no-retrieval baseline on the locked test set. This is a pre-registered target, not an achieved result.

## External Benchmark References

Spider and BIRD are used as research references for SQL complexity, schema generalization and database-value grounding. Neither is integrated into the current benchmark.

See `reports/benchmark/spider_bird_feasibility.md`.

## Project Philosophy

VeriQuery prioritizes:

- Evidence-based dataset understanding.
- Explicit business semantics.
- Reproducible benchmark construction.
- Strict development/test separation.
- Measurable evaluation.
- Honest reporting of limitations.

The objective is not merely to generate SQL, but to investigate how natural-language analytics can become more trustworthy and verifiable.

## Worker 02 experiment artifacts

- v2 results: `experiments/results/groq_json_object_baseline.jsonl`
- v3 results: `experiments/results/groq_full_schema_baseline_v3.jsonl`
- v2 machine-readable evaluation: `experiments/evaluations/groq_json_object_v2_evaluation.json` and `.csv`
- v2 semantic report: `docs/groq_full_schema_baseline_v2_evaluation.md`
- v3 semantic report: `docs/groq_full_schema_baseline_v3_evaluation.md`
- v2/v3 comparison: `docs/groq_full_schema_baseline_comparison.md`

The v3 JSONL is append-only and contains 56 attempts, including failed attempts and successful retries, for 40 unique development questions. Its final state is 40/40 unique questions successfully generated. Generation settings changed during recovery; see the v3 report.
