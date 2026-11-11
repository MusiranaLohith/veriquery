# Spider and BIRD Benchmark Feasibility Review

## 1. Purpose

Assess whether the Spider and BIRD Text-to-SQL benchmarks are suitable
for direct use in VeriQuery's Phase 1 benchmark.

This is a feasibility review only. Neither external benchmark is being
integrated into VeriQuery.

## 2. Spider

**Reference:** Yu et al., EMNLP 2018.

Spider contains 10,181 questions and 5,693 unique SQL queries across
200 databases and 138 domains. Its primary purpose is to evaluate
complex SQL generation and generalization across unseen database
schemas.

Official sources:
- Paper: https://aclanthology.org/D18-1425/
- Dataset and task information: https://yale-lily.github.io/spider
- Evaluation code: https://github.com/taoyds/spider

### Relevance to VeriQuery

Spider is useful as a reference for:
- SQL complexity and question diversity.
- Evaluation against previously unseen schemas.
- Relational reasoning across multiple tables.
- Designing rigorous Text-to-SQL evaluation procedures.

### Limitations for direct use

VeriQuery currently uses one retail dataset and one PostgreSQL table.
The table has no foreign keys or verified relationships to other tables.
Consequently, multi-table JOIN and cross-schema reasoning cannot be
meaningfully evaluated using the current project schema.

Spider's cross-domain, multi-database setting also differs from
VeriQuery's fixed retail-domain benchmark.

**Assessment:** Useful as a methodological reference, but not suitable
for direct integration into the current Phase 1 benchmark.

## 3. BIRD

**Reference:** Li et al., NeurIPS 2023.

BIRD contains 12,751 question-SQL pairs across 95 databases, covering
37 professional domains, with a reported total database size of
33.4 GB.

Its key focus areas include:
- Grounding questions in actual database values.
- Handling dirty or noisy database contents.
- Using external knowledge to interpret database values.
- Producing efficient SQL for substantial databases.

Official sources:
- Paper: https://proceedings.neurips.cc/paper_files/paper/2023/hash/83fc8fab1710363050bbd1d4b8cc0021-Abstract-Datasets_and_Benchmarks.html
- Benchmark website: https://bird-bench.github.io/
- Official code and data: https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/bird

### Relevance to VeriQuery

BIRD is conceptually relevant to:
- Product-value matching.
- Grounding natural-language terms in database values.
- Handling imperfect or inconsistent database contents.
- Considering query execution efficiency.

These areas provide useful design references for future VeriQuery
development.

### Limitations for direct use

BIRD's multi-database, multi-domain scale is substantially broader
than VeriQuery's single retail dataset and one-table schema.

Direct integration would introduce additional datasets, schemas,
domain-specific knowledge and evaluation requirements beyond the
approved Phase 1 scope.

**Assessment:** Particularly useful as a reference for database-value
grounding, but not suitable for direct integration into the current
benchmark.

## 4. Comparison with VeriQuery

| Dimension | Spider | BIRD | Current VeriQuery |
|---|---|---|---|
| Dataset scope | 200 databases | 95 databases | 1 dataset |
| Domain scope | 138 domains | 37 domains | 1 retail domain |
| Main emphasis | Complex SQL and schema generalization | Database values and real-world grounding | Retrieval-assisted retail NL-to-SQL evaluation |
| Relational coverage | Multiple tables | Multiple databases and schemas | One table, no foreign keys |
| Direct JOIN evaluation | Supported by its schemas | Supported by its schemas | Not supported by current schema |

## 5. Feasibility Decision

Neither Spider nor BIRD will be integrated into VeriQuery's primary
100-question benchmark.

They will remain external methodological references:

- Spider informs thinking about SQL complexity, schema generalization
  and evaluation methodology.
- BIRD informs thinking about database-value grounding, noisy values
  and query efficiency.

No external benchmark questions, answer keys or database records will
be added to the development or locked-test splits.

## 6. Scope and Limitations

This assessment is based on published benchmark descriptions and
VeriQuery's current dataset and schema.

Neither benchmark has been experimentally integrated or evaluated
within VeriQuery.

The current VeriQuery benchmark remains limited to one retail dataset,
one business domain and one database table. It cannot establish
generalization across multiple domains or multi-table relational
schemas.