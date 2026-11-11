# VeriQuery — Benchmark Design

## 1. Purpose

The VeriQuery benchmark evaluates whether retrieval-grounded context improves the accuracy and reliability of LLM-generated SQL for natural-language questions about relational business data.

The benchmark will compare four configurations:

1. Full-schema prompting without retrieval (baseline).
2. BM25 keyword retrieval.
3. Dense semantic retrieval.
4. Hybrid retrieval combining BM25 and dense retrieval.

All configurations must be evaluated using the same locked test questions and comparable LLM settings.

## 2. Benchmark Size and Split

The benchmark contains 100 questions.

| Split | Questions | Purpose |
|---|---:|---|
| Development | 40 | Retrieval development, debugging and configuration |
| Locked test | 60 | Independent final evaluation |
| **Total** | **100** | |

The development set may be used during implementation.

The locked test set must remain isolated from development, retrieval configuration, prompt tuning and other optimization decisions.

## 3. Question Category Distribution

| Category | Development | Locked test | Total |
|---|---:|---:|---:|
| Schema understanding | 4 | 4 | 8 |
| Filtering and sorting | 5 | 7 | 12 |
| Aggregation and grouping | 6 | 8 | 14 |
| Date and time analysis | 4 | 5 | 9 |
| NULL handling | 4 | 5 | 9 |
| Customer and country analysis | 4 | 6 | 10 |
| Product and operational-code analysis | 4 | 6 | 10 |
| Transaction and cancellation analysis | 4 | 8 | 12 |
| Multi-condition analytical reasoning | 4 | 7 | 11 |
| Unanswerable questions | 1 | 4 | 5 |
| **Total** | **40** | **60** | **100** |

Each question belongs to one primary category.

## 4. Difficulty Distribution

Both benchmark splits have been classified using the same SQL-complexity rubric. The distributions below reflect the final assigned difficulty labels rather than a predetermined allocation target.

### Development benchmark

| Difficulty | Questions | Percentage |
|---|---:|---:|
| Easy | 15 | 37.5% |
| Medium | 19 | 47.5% |
| Hard | 6 | 15.0% |
| **Total** | **40** | **100%** |

### Locked-test benchmark

| Difficulty | Questions | Percentage |
|---|---:|---:|
| Easy | 10 | 16.7% |
| Medium | 45 | 75.0% |
| Hard | 5 | 8.3% |
| **Total** | **60** | **100%** |

### Combined benchmark

| Difficulty | Questions | Percentage |
|---|---:|---:|
| Easy | 25 | 25.0% |
| Medium | 64 | 64.0% |
| Hard | 11 | 11.0% |
| **Total** | **100** | **100%** |

The locked-test classifications were reviewed against the reference SQL. Questions were not labelled Hard merely because they contain particular SQL keywords or constructs. The final distribution is an outcome of the question complexity review, not an allocation target.

Unanswerable questions also receive a difficulty label based on the reasoning needed to recognize that the requested information cannot be reliably obtained.

### Easy

Tests basic schema understanding, direct filtering, simple NULL checks, straightforward date conditions, basic counting and single-metric aggregations. The query generally requires one uncomplicated analytical operation.

### Medium

Tests meaningful grouped analysis, distinct counts, date transformations, multiple metrics, conditional aggregation, ranking, NULL semantics, or post-aggregation filtering. The query may combine several SQL constructs but follows a relatively direct analytical path.

### Hard

Tests genuinely demanding analytical reasoning involving multiple interacting conditions, derived metrics, complex conditional aggregation, multi-stage analysis, window functions or ranking within partitions. The question requires careful interpretation of several constraints or analytical steps.

SQL syntax alone does not determine difficulty. The number of SQL keywords or the presence of a particular construct must not automatically make a question Hard. Classification must reflect the reasoning required by the natural-language request and its reference SQL.

## 5. Question Design Requirements

Each question must have:

- A unique question ID.
- A natural-language question.
- A primary category.
- A difficulty label.
- An answerability label.
- A verified reference SQL query, where answerable.
- An expected result or result-validation specification.
- Assumptions and interpretation notes where necessary.

Questions must be understandable as realistic business or analytical requests.

Avoid repetitive questions that differ only by a country, date or product identifier without testing a meaningful new capability.

## 6. Answerability

Each question is classified as either:

- **Answerable:** The available database schema and recorded data contain sufficient information to answer the request.
- **Unanswerable:** The request requires information or semantics that cannot be reliably established from the available database.

Unanswerable questions must include an explanation of the missing information or unsupported assumption.

The system should recognize these limitations rather than inventing columns, business definitions or results.

## 7. SQL and Result Validation

Reference SQL must:

- Use only existing database tables and columns.
- Use read-only operations.
- Reflect the documented dataset semantics.
- Handle NULL values deliberately.
- Avoid unsupported business assumptions.
- Be tested against the actual PostgreSQL database.

Evaluation must distinguish:

1. SQL execution success.
2. SQL semantic correctness.
3. Result correctness.
4. Appropriate handling of unanswerable questions.

SQL string similarity alone is not an adequate correctness measure. Different SQL queries may produce equivalent results.

### Result Comparison Rules

Reference SQL results and stored expected results must be compared using the following rules:

1. **Column names:** Column names and their corresponding values must match exactly.
2. **Row count:** The actual and expected results must contain the same number of rows.
3. **Row ordering:** Multi-row reference queries must use an explicit `ORDER BY` clause when a particular ordering is part of the expected result. Row order must then match exactly.
4. **Numeric values:** Numeric results must match within a relative and absolute tolerance of `1e-9` to accommodate floating-point representation differences.
5. **NULL values:** NULL must match NULL. It must not be treated as zero, an empty string or a missing row.
6. **Strings:** String values must match exactly, including case and whitespace.
7. **Dates and timestamps:** Date and timestamp values must be represented consistently using ISO 8601 formatting.
8. **Result structure:** Single-row results and multi-row results must retain their documented expected-result structures.

The benchmark verification process uses independently executed, read-only PostgreSQL reference queries to validate stored expected results. Comparison differences must be investigated rather than silently normalized or ignored.

## 8. Dataset-Specific Safeguards

The benchmark must respect the formal dataset contract and business glossary.

In particular:

- Cancellation invoices are identified by the documented `C` invoice prefix; they are not interchangeable with all negative-quantity records.
- `price` represents recorded per-unit price, not an invoice-line total.
- Missing Customer IDs and descriptions must be handled explicitly.
- StockCode values are case-sensitive.
- Not every StockCode represents merchandise.
- Operational-entry candidates must not automatically be treated as ordinary products.
- Description annotations must not be interpreted as verified product categories.
- Repeated observations are preserved according to the consolidation policy.
- The database contains one primary transaction table; unsupported relationships and JOIN questions must not be invented.

## 9. Locked Test Set Isolation

The 60-question test set is reserved for final evaluation.

### Isolation rules

1. Construct and validate the development set first.
2. Store locked test questions separately from development questions.
3. Store test reference SQL and expected results separately from test question text.
4. Do not use locked test questions or answers to tune prompts, retrieval parameters or other system configurations.
5. Freeze the development process before conducting final test evaluation.
6. Record the benchmark version and evaluation configuration.
7. Do not modify test questions after inspecting evaluation outcomes without documenting a new benchmark version and rationale.
8. Do not include locked-test questions, reference SQL or expected results in development SQL-example resources.

### Verified isolation checks

The following checks were performed during Phase 1:

| Check | Result |
|---|---|
| Development questions | 40 |
| Locked-test questions | 60 |
| Development/test question-ID overlap | 0 |
| Locked-test IDs found in development data and SQL resources | 0 |
| Exact normalized SQL duplicates among answerable questions | 0 |
| Exact normalized SQL duplicates involving unanswerable questions | 4 |

The four SQL duplicates involve TEST056–TEST059 and DEV040. These questions use the same schema-inspection query to establish that requested information is unavailable in the dataset. This is intentional reuse for answerability validation, not reuse of answerable test queries as development examples.

The development/test wording-overlap audit compared all 2,400 question pairs. It found zero exact wording matches. Twenty-eight similarity flags remained for manual review; these were retained because the questions test distinct conditions or analytical operations despite sharing terminology.

The project currently contains no separate development SQL-example collection. Its SQL resources contain dataset investigation and schema scripts rather than benchmark-example queries.

These checks establish structural separation and the absence of answerable reference-SQL duplication. They do not, by themselves, establish that no person has ever inspected locked-test content during later model development. The no-test-tuning rule must continue to be enforced during subsequent phases.

## 10. Evaluation Objective

The primary comparison is:

**Hybrid retrieval versus full-schema prompting without retrieval.**

The pre-registered target is for hybrid retrieval to improve SQL correctness by at least 5 percentage points on the locked test set.

BM25-only and dense-only configurations provide additional comparisons.

This target is an objective, not a guaranteed outcome. Any failure to achieve it must be reported honestly.

Report the number of correct questions alongside accuracy. Discuss the uncertainty associated with a 60-question test set and avoid claims of universal NL-to-SQL reliability.

## 11. Benchmark Completion and Acceptance Criteria

The benchmark is considered ready for downstream evaluation when the following conditions are satisfied:

| Area | Acceptance criterion |
|---|---|
| Benchmark composition | Exactly 100 questions, comprising 40 development and 60 locked-test questions. |
| Question integrity | Unique identifiers, valid metadata, and consistent question-to-answer-key mapping. |
| Coverage | Documented category distribution and meaningful analytical diversity across both splits. |
| Difficulty | Consistent application of the documented complexity rubric, with actual distributions reported. |
| Answerability | Every question classified as answerable or unanswerable, with supporting validation evidence. |
| SQL correctness | All answerable reference queries execute successfully against the benchmark database. |
| Expected results | Stored expected results match independently executed reference queries. |
| Split integrity | Development and locked-test resources remain structurally separated, with overlap and leakage checks documented. |
| Documentation | Dataset limitations, business assumptions, benchmark methodology, validation procedures and known limitations are documented. |

Completion evidence is maintained through the benchmark validation scripts, audit outputs, answer keys and accompanying reports.

The benchmark establishes a controlled evaluation resource for subsequent NL-to-SQL experiments. It does not establish the correctness, security or reliability of any downstream NL-to-SQL system.
