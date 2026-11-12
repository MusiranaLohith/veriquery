# VeriQuery — Design Decisions

**Project:** VeriQuery — Trustworthy Natural-Language Analytics for Relational Databases
**Workstream:** Worker 02 — LLM Integration and Full-Schema Baseline
**Status:** Implementation in progress
**Last updated:** 12 November 2026

---

## 1. Purpose

This document records the architectural and implementation decisions governing Worker 02 of VeriQuery.

Worker 02 establishes a reproducible full-schema/no-retrieval baseline. It integrates LLM providers, generates structured SQL responses, and records development benchmark outcomes.

The baseline will later serve as the comparison point for retrieval-based approaches.

## 2. Problem Context

Natural-language-to-SQL systems can generate incorrect SQL because they may:

- Reference nonexistent tables or columns.
- Misinterpret business terminology.
- Produce incorrect aggregations.
- Make unsupported assumptions about the underlying data.
- Generate queries that do not reflect the actual database structure.

VeriQuery aims to reduce these problems by grounding SQL generation in verified database schema information and documented business rules.

Worker 02 establishes the initial baseline against which subsequent retrieval approaches can be evaluated.

## 3. Dataset and Database Decisions

### 3.1 Dataset

The project uses the UCI Online Retail II dataset.

The prepared dataset contains 1,044,848 records.

### 3.2 Database

PostgreSQL is used as the relational database.

The current implementation uses one primary table:

`retail_transactions`

The table contains ten columns:

| Column | Type |
|---|---|
| record_id | BIGINT |
| invoice | TEXT |
| stock_code | TEXT |
| description | TEXT |
| quantity | INTEGER |
| invoice_date | TIMESTAMP |
| price | NUMERIC(12, 3) |
| customer_id | BIGINT |
| country | TEXT |
| source_sheet | TEXT |

The database does not currently provide a multi-table relational schema with foreign-key relationships. Therefore, this phase does not claim to demonstrate general multi-table JOIN reasoning.

### 3.3 Data Semantics

The following verified dataset characteristics must be respected:

- A database row represents a recorded invoice-line observation.
- Multiple rows can share an invoice.
- Exact duplicate records are preserved.
- Invoice identifiers beginning with `C` indicate cancellation records.
- Negative quantities are not automatically equivalent to customer returns.
- Price represents a per-unit amount in GBP, not a precomputed line total.
- Customer identifiers may be NULL.
- Descriptions can contain product descriptions, operational annotations, or NULL values.
- Stock codes are case-sensitive and may represent operational entries rather than merchandise.

These rules are included in the SQL-generation prompt to reduce unsupported interpretations.

## 4. LLM Provider Decisions

### 4.1 Provider integrations

Worker 02 contains separate integrations for:

- Google Gemini using the official `google-genai` SDK.
- Groq using the official `groq` SDK.

The integrations are maintained independently. Their experiment records must not be mixed or treated as interchangeable results.

### 4.2 Gemini experiment

Gemini was the initial provider integration.

The first recorded live attempt used DEV001 and failed with an HTTP 503 service-unavailable response.

The failed attempt is preserved in:

`experiments/results/full_schema_baseline.jsonl`

This failure is part of the experiment history and must not be deleted or represented as successful generation.

### 4.3 Groq experiment

Groq was introduced as a separate provider experiment after the initial Gemini service failure.

The selected model for the current integration is:

`qwen/qwen3.8-27b`

The first controlled live smoke test used DEV001 and successfully returned a structured SQL response.

The result is preserved separately in:

`experiments/results/groq_smoke_test.jsonl`

The smoke test demonstrates successful provider communication and structured response generation for one development question. It does not establish full benchmark performance or prove that Groq is superior to Gemini.

### 4.4 Provider and cost constraints

- Use only explicitly configured providers.
- Keep provider credentials outside version control.
- Do not enable paid billing or add payment methods.
- Respect the available free-tier model and account limits.
- Do not silently switch providers during an experiment.
- Record the provider and model identifier for every attempt.
- Keep provider-specific results separate.

The definitive provider for subsequent baseline evaluation must be selected explicitly and documented before the full development benchmark is run.

## 5. Full-Schema Baseline Decision

### Decision

Every baseline prompt receives the complete verified database schema and the documented business rules.

### Rationale

This establishes a baseline without retrieval.

It allows subsequent experiments to determine whether retrieval improves SQL generation compared with providing the complete schema directly.

### Explicit exclusions

The full-schema baseline must not use:

- BM25 retrieval.
- Dense retrieval.
- Embeddings.
- pgvector.
- Hybrid retrieval.
- Retrieved SQL examples.
- Few-shot SQL examples.
- Retrieval-based schema selection.

The absence of retrieval is intentional, not an incomplete implementation.

## 6. Structured Output Decision

### Decision

Use Pydantic to define and validate the expected LLM response.

The response contract contains:

- `is_answerable`
- `sql`
- `interpretation`
- `assumptions`
- `needs_clarification`

### Rationale

Structured responses make it easier to:

- Distinguish answerable and unanswerable questions.
- Capture generated SQL separately from explanatory text.
- Record assumptions.
- Identify questions requiring clarification.
- Validate model output consistently.

Unanswerable questions must not contain SQL. Answerable questions that do not require clarification must contain non-empty SQL.

## 7. SQL Generation and Execution Separation

### Decision

Worker 02 generates SQL but does not execute it.

### Rationale

SQL generation and SQL execution are separate responsibilities.

Generated SQL must eventually pass through a dedicated validation and execution layer before it can interact with the database.

Worker 02 therefore does not implement:

- SQL parsing and validation.
- SQLGlot-based safety checks.
- Database execution of generated queries.
- SQL correction or automatic repair.
- Database write operations.

These responsibilities belong to subsequent project workstreams.

## 8. Benchmark Decisions

### 8.1 Development Benchmark

The development benchmark contains 40 questions.

It is used for implementation checks and baseline development.

The current question set includes answerable and unanswerable questions. DEV040 is unanswerable because the dataset does not contain verified cost or profit information needed to calculate net profit by product.

### 8.2 Locked Test Benchmark

The locked test benchmark contains 60 questions.

It must remain untouched during Worker 02 development.

It must not be inspected, used for prompt tuning, used for debugging, or used to make implementation decisions.

### 8.3 Baseline Comparison

The full-schema/no-retrieval baseline will provide the comparison point for later retrieval experiments.

The pre-registered evaluation target is for hybrid retrieval to outperform the full-schema baseline by at least five percentage points on the locked test set.

If this target is not achieved, the result must be reported honestly rather than presenting retrieval as an improvement.

## 9. Experiment Recording Decision

### Decision

Record benchmark outcomes in append-only JSONL format.

The existing provider experiment files are:

- Gemini: `experiments/results/full_schema_baseline.jsonl`
- Groq: `experiments/results/groq_smoke_test.jsonl`

These files represent separate experiments and must remain independent.

Each attempt should preserve:

- Question ID.
- Prompt version.
- Structured model output, when available.
- Model ID.
- Timestamp.
- Token usage, when available.
- Latency.
- API status.
- Error information, when applicable.

### Rationale

Append-only recording preserves experiment history and supports reproducibility.

Failed attempts must also be recorded. A failed API request must not silently disappear from the experiment history.

Existing experiment records must not be deleted or overwritten during normal benchmark execution.

## 10. Resume and Retry Decision

The benchmark runner supports two execution modes:

**Default mode**

Previously attempted questions are skipped, regardless of whether the previous attempt succeeded or failed.

**Retry-failed mode**

Previously successful questions are skipped, while previously attempted questions without a successful result can be retried.

The `--retry-failed` command-line option enables the second behavior.

This prevents unnecessary repeated requests while allowing failed attempts to be retried deliberately.

## 11. Configuration and Secret Management

Provider credentials are loaded from the project-root `.env` file:

- `GEMINI_API_KEY`
- `GROQ_API_KEY`

The `.env` file is excluded from version control through `.gitignore`.

Configuration is accessed through centralized provider configuration rather than scattering environment-variable access throughout the application.

Credentials must never be printed, committed, or included in experiment records.

## 12. Reliability Decisions

Provider-specific reliability behavior is maintained separately.

**Gemini integration:**

- Request timeout configuration.
- Bounded retries for transient failures.
- Error classification.
- Structured-response validation.
- Token-usage capture when returned by the API.
- Latency measurement.
- Failure recording.

**Groq integration:**

- Request timeout configuration.
- Automatic SDK retries disabled.
- Error classification.
- Strict structured JSON response configuration.
- Pydantic response validation.
- Token-usage capture when returned by the API.
- Latency measurement.
- Failure recording.

Transient service errors and rate limits must not be treated as successful SQL-generation outcomes.

A successful mocked test does not establish that a live provider is available or that real benchmark generation has succeeded.

A successful single-question smoke test does not establish full benchmark performance.

## 13. Testing Strategy

Worker 02 uses automated tests with mocked external API interactions.

The tests cover:

- Pydantic response validation.
- Prompt construction and schema inclusion.
- Absence of retrieval and few-shot examples.
- Gemini client success and failure handling.
- Groq client success and failure handling.
- Strict structured-response configuration.
- Timeout and error classification.
- Benchmark loading and validation.
- Duplicate question rejection.
- Resume and retry selection.
- Append-only experiment recording.
- Benchmark execution.
- CLI dry-run and orchestration behavior.

Live API calls are not required for ordinary unit-test execution.

## 14. Explicitly Out of Scope

The following are not part of Worker 02:

- BM25, dense, or hybrid retrieval.
- Embedding generation.
- pgvector integration.
- Multi-agent systems.
- LangGraph.
- Model fine-tuning or training.
- Multi-database support.
- Multiple datasets.
- Complex query planning.
- Database write operations.
- Enterprise authentication.
- Dashboards and frontend development.
- Voice interfaces.
- Conversational memory.
- Production deployment.

These exclusions preserve a controlled experimental scope.

## 15. Definition of Completion

Worker 02 is considered complete only when:

1. Provider integrations and configuration are implemented and documented.
2. Structured SQL-generation responses are validated.
3. Full-schema prompts contain the verified schema and business rules.
4. Development benchmark loading and execution are reproducible.
5. Successful and failed attempts are recorded separately by experiment.
6. Resume and retry behavior works correctly.
7. Automated tests cover the implementation.
8. Required documentation is complete.
9. The selected provider and model are explicitly documented for the baseline evaluation.
10. Development benchmark outcomes and live-provider limitations are reported honestly.

A passing unit-test suite or a successful single-question smoke test alone does not establish successful full benchmark execution.

---

**Document ownership:** VeriQuery — Worker 02
**Next related documents:** `llm_integration.md` and `baseline_methodology.md`
