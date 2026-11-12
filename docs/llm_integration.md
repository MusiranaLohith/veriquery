# VeriQuery — LLM Integration

## 1. Purpose

Worker 02 integrates external Large Language Model (LLM) providers into VeriQuery.

Its responsibility is to convert a natural-language analytics question into a structured SQL-generation response. The model is given the complete database schema and verified business rules.

This implementation establishes the full-schema, no-retrieval baseline.

It does not execute generated SQL. SQL validation, safety enforcement, and controlled execution belong to subsequent project components.

## 2. Supported providers

The integration currently supports two providers:

| Provider | Model | Client |
|---|---|---|
| Gemini | `gemini-3.8-flash` | `GeminiSQLClient` |
| Groq | `qwen/qwen3.8-27b` | `GroqSQLClient` |

Provider results are recorded separately. A result from one provider must not be presented as a result from the other.

The provider is selected explicitly when running the benchmark. The system does not silently switch providers when one is unavailable.

## 3. Credential configuration

Provider credentials are stored in the project-root `.env` file:

- `GEMINI_API_KEY`
- `GROQ_API_KEY`

The `.env` file must not be committed to Git.

The shared configuration module is:

`src/veriquery/llm/config.py`

It provides:

- `get_api_key("gemini")`
- `get_api_key("groq")`

Gemini-specific request settings are represented by the `Settings` dataclass.

Missing credentials produce a configuration error. Credentials must never be printed or included in experiment records.

## 4. Structured response contract

Both providers are expected to return a response conforming to the Pydantic model:

`src/veriquery/llm/models.py`

The response contains:

| Field | Purpose |
|---|---|
| `is_answerable` | Whether the supplied data and business rules support an answer |
| `sql` | Generated SQL, or null when SQL should not be supplied |
| `interpretation` | The model's interpretation of the question |
| `assumptions` | Assumptions made while interpreting the question |
| `needs_clarification` | Whether clarification is required |

The model enforces these conditions:

- An unanswerable question must have `sql = null`.
- A question requiring clarification must have `sql = null`.
- An answerable question that does not require clarification must contain non-empty SQL.

Provider output is parsed and validated against this contract. Invalid structured output is recorded as a failed generation attempt.

## 5. Prompt construction

Prompt construction is implemented in:

`src/veriquery/llm/prompts.py`

The current prompt version is:

`full-schema-baseline-v1`

Each prompt includes:

- The complete schema of `retail_transactions`.
- Verified business rules.
- Instructions for PostgreSQL SQL generation.
- Instructions for identifying unanswerable questions.
- Instructions for handling ambiguity and clarification.
- Restrictions against data modification and schema modification.

The current dataset contains one table. The prompt must not imply that the dataset supports general multi-table JOIN reasoning.

The prompt does not include retrieved documents, embeddings, BM25 results, dense-retrieval results, or few-shot SQL examples.

## 6. Provider client behavior

### Gemini

Implementation:

`src/veriquery/llm/client.py`

The Gemini client:

- Uses structured JSON output.
- Validates the response using the Pydantic response model.
- Uses a 120-second request timeout.
- Configures two retries for selected transient failures.
- Captures latency and available token usage.
- Classifies failures and returns a common `GenerationResult`.

### Groq

Implementation:

`src/veriquery/llm/groq_client.py`

The Groq client:

- Uses strict JSON Schema structured output.
- Validates the returned JSON using the Pydantic response model.
- Uses a 45-second request timeout.
- Disables automatic SDK retries.
- Captures latency and available token usage.
- Classifies failures and returns the same `GenerationResult` structure.

The Groq client's lack of automatic retries is intentional. Failed attempts remain visible in the experiment records rather than being silently retried by the SDK.

## 7. Common generation result

Both clients return the shared `GenerationResult` structure.

It captures:

- Structured output, when valid.
- Model identifier.
- Latency in seconds.
- Prompt token count, when available.
- Candidate/completion token count, when available.
- Total token count, when available.
- API status.
- Error information, when generation fails.

Token counts are provider-reported values. They should not be assumed to be directly comparable across different providers or tokenization systems.

## 8. Benchmark integration

The provider-independent benchmark executor is implemented in:

`src/veriquery/benchmark/executor.py`

The CLI entry point is:

`src/veriquery/benchmark/run_baseline.py`

Select the provider explicitly:

```bash
python -m veriquery.benchmark.run_baseline --provider gemini --dry-run
python -m veriquery.benchmark.run_baseline --provider groq --dry-run
A dry-run loads and selects development questions without initializing a provider client or sending API requests.

The benchmark runner supports:
- Provider selection.
- Dry-run inspection.
- Skipping previously attempted questions by default.
- Retrying failed questions with `--retry-failed`.
- Separate result files for each provider.

A real benchmark run makes external API requests and requires explicit authorization.

## 9. Experiment result files

| File | Purpose |
|---|---|
| `experiments/results/full_schema_baseline.jsonl` | Gemini full-schema baseline attempts |
| `experiments/results/groq_full_schema_baseline.jsonl` | Groq full-schema baseline attempts |
| `experiments/results/groq_smoke_test.jsonl` | Separate Groq integration smoke test |

The Groq smoke test is not part of the 40-question Groq baseline.

Each benchmark record includes the experiment identifier, provider, question identifier, prompt version, model identifier, timestamp, latency, available token usage, API status, error information, and structured output when available.

Records are appended as JSON Lines. Existing records are preserved.

## 10. Reliability and error handling

The integration distinguishes successful structured generation from failed generation.

Failures can include missing credentials, request timeouts, rate limits, provider service errors, other API errors, and invalid or empty structured responses.

A failed attempt is recorded rather than silently discarded.

The benchmark runner uses existing records to avoid repeating completed work by default.

## 11. SQL execution boundary

Worker 02 generates SQL but does not execute it.

Generated SQL is untrusted model output. It must not be run directly against the database.

SQL validation, read-only enforcement, execution controls, and execution-result handling belong to the later SQL safety and execution workstream.

## 12. Testing

Provider behavior is tested using mocks. These tests validate response parsing, schema construction, error handling, token capture, and benchmark integration without requiring live API calls.

Passing mocked tests does not establish live provider availability or benchmark accuracy.

Live API experiments must be recorded separately from mocked tests.
