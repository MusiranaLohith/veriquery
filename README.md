# VeriQuery

**Trustworthy Natural-Language Analytics for Relational Databases**

VeriQuery is a research-oriented project exploring how retrieval-grounded context can improve the accuracy of translating natural-language questions into SQL.

The project focuses on reducing common Text-to-SQL problems, including incorrect schema references, misunderstood business terminology, incorrect database-value matching and inaccurate SQL generation.

## Project Status

**Current milestone:** Phase 1 — Project Foundation, Data Engineering and Benchmark Construction.

The initial dataset investigation, PostgreSQL preparation, business glossary, product inventory and 100-question benchmark have been completed and validated.

Later phases involving retrieval, LLM-based SQL generation, safe execution and production deployment are planned and are not yet implemented.

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

## Planned Development

The remaining project roadmap includes:

1. Schema understanding and retrieval.
2. BM25 and dense retrieval.
3. Hybrid retrieval.
4. LLM-based SQL generation.
5. SQL validation and safe read-only execution.
6. Baseline and retrieval-strategy evaluation.
7. Production engineering and deployment.

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