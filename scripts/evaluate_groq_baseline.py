
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import sqlglot
from sqlglot import exp


ROOT = Path(__file__).resolve().parents[1]

EXPERIMENT_PATH = (
    ROOT / "experiments/results/groq_json_object_baseline.jsonl"
)
BENCHMARK_PATH = ROOT / "data/benchmark/dev/dev_questions.jsonl"
OUTPUT_DIR = ROOT / "experiments/evaluations"

EXPECTED_PROMPT_VERSION = "full-schema-baseline-json-object-v2"

REQUIRED_FIELDS = {
    "is_answerable",
    "sql",
    "interpretation",
    "assumptions",
    "needs_clarification",
}

FORBIDDEN_SQL_KEYS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "command",
    "merge",
    "truncate",
}

# Findings from the initial manual review of the 40 generations.
# These are human-reviewed findings, not automated SQL judgments.
KNOWN_SEMANTIC_FINDINGS = {
    "DEV011": {
        "severity": "critical",
        "category": "postgresql_function",
        "finding": "Uses MONTH() and invalid month-name conversion.",
    },
    "DEV016": {
        "severity": "moderate",
        "category": "assumption_mismatch",
        "finding": "SQL filters Q1 2011, but assumption describes the first half.",
    },
    "DEV019": {
        "severity": "minor",
        "category": "assumption_quality",
        "finding": "Irrelevant UNIX epoch calendar assumption.",
    },
    "DEV027": {
        "severity": "moderate",
        "category": "null_customer_group",
        "finding": "May report the NULL customer_id group as a customer.",
    },
    "DEV029": {
        "severity": "critical",
        "category": "aggregation_population",
        "finding": "Filters NULL descriptions before COUNT(*), changing the record count.",
    },
    "DEV034": {
        "severity": "moderate",
        "category": "conditional_group",
        "finding": "Does not exclude C-prefixed invoices with zero qualifying records.",
    },
    "DEV037": {
        "severity": "critical",
        "category": "aggregation_population",
        "finding": "Filters NULL customer IDs before calculating all-record metrics.",
    },
    "DEV039": {
        "severity": "moderate",
        "category": "calendar_month_granularity",
        "finding": "Groups by month number across years; calendar months must remain separate.",
    },
}


def load_jsonl(path):
    if not path.exists():
        raise FileNotFoundError(path)

    records = []

    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue

        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON in {path}, line {line_number}: {exc}"
            ) from exc

    return records


def validate_response(output):
    errors = []

    if not isinstance(output, dict):
        return False, ["Output is not a JSON object."]

    if set(output) != REQUIRED_FIELDS:
        errors.append("Output fields do not match the required five-field contract.")

    if not isinstance(output.get("is_answerable"), bool):
        errors.append("is_answerable must be a boolean.")

    if not isinstance(output.get("needs_clarification"), bool):
        errors.append("needs_clarification must be a boolean.")

    if not isinstance(output.get("interpretation"), str):
        errors.append("interpretation must be a string.")

    assumptions = output.get("assumptions")
    if not isinstance(assumptions, list) or not all(
        isinstance(item, str) for item in assumptions
    ):
        errors.append("assumptions must be an array of strings.")

    sql = output.get("sql")

    if sql is not None and not isinstance(sql, str):
        errors.append("sql must be a string or null.")

    if output.get("is_answerable") is False and sql is not None:
        errors.append("Unanswerable response must have SQL null.")

    if output.get("needs_clarification") is True and sql is not None:
        errors.append("Clarification response must have SQL null.")

    if (
        output.get("is_answerable") is True
        and output.get("needs_clarification") is False
        and (not isinstance(sql, str) or not sql.strip())
    ):
        errors.append("Answerable response must contain non-empty SQL.")

    return not errors, errors


def inspect_sql(sql):
    result = {
        "parse_status": "not_applicable",
        "read_only_status": "not_applicable",
        "postgres_function_warning": False,
        "sql_error": None,
    }

    if not isinstance(sql, str) or not sql.strip():
        return result

    try:
        statements = sqlglot.parse(sql, read="postgres")

        if len(statements) != 1 or statements[0] is None:
            raise ValueError(
                f"Expected one SQL statement; found {len(statements)}."
            )

        tree = statements[0]
        result["parse_status"] = "passed"

        if tree.key not in {"select", "union", "intersect", "except"}:
            result["read_only_status"] = "failed"
            result["sql_error"] = (
                f"Unexpected SQL root expression: {tree.key}"
            )
            return result

        forbidden = sorted({
            node.key
            for node in tree.walk()
            if node.key in FORBIDDEN_SQL_KEYS
        })

        result["read_only_status"] = (
            "failed" if forbidden else "passed"
        )

        if forbidden:
            result["sql_error"] = (
                "Forbidden SQL operations found: " + ", ".join(forbidden)
            )

        # SQLGlot may parse unknown/dialect-specific functions without
        # necessarily rejecting them. Flag MONTH()/YEAR() separately.
        for node in tree.walk():
            if isinstance(node, exp.Anonymous):
                if node.name.upper() in {"MONTH", "YEAR"}:
                    result["postgres_function_warning"] = True

    except Exception as exc:
        result["parse_status"] = "failed"
        result["read_only_status"] = "not_verified"
        result["sql_error"] = str(exc)

    return result


def main():
    experiment_records = load_jsonl(EXPERIMENT_PATH)
    benchmark_records = load_jsonl(BENCHMARK_PATH)

    benchmark = {
        item["question_id"]: item
        for item in benchmark_records
    }

    experiment_ids = [
        record.get("question_id")
        for record in experiment_records
    ]

    duplicate_ids = [
        question_id
        for question_id, count in Counter(experiment_ids).items()
        if count > 1
    ]

    missing_ids = sorted(set(benchmark) - set(experiment_ids))
    unexpected_ids = sorted(set(experiment_ids) - set(benchmark))

    results = []

    for record in experiment_records:
        question_id = record.get("question_id")
        question = benchmark.get(question_id)
        output = record.get("output")

        contract_ok, contract_errors = validate_response(output)

        sql = output.get("sql") if isinstance(output, dict) else None
        sql_result = inspect_sql(sql)

        expected_answerability = (
            question.get("answerability") if question else None
        )

        actual_answerability = None
        if isinstance(output, dict):
            actual_answerability = (
                "answerable"
                if output.get("is_answerable") is True
                else "unanswerable"
                if output.get("is_answerable") is False
                else "invalid"
            )

        answerability_match = (
            actual_answerability == expected_answerability
            if expected_answerability is not None
            else None
        )

        semantic_finding = KNOWN_SEMANTIC_FINDINGS.get(question_id)

        results.append({
            "question_id": question_id,
            "question": question.get("question") if question else None,
            "api_status": record.get("api_status"),
            "prompt_version": record.get("prompt_version"),
            "contract_status": "passed" if contract_ok else "failed",
            "contract_errors": contract_errors,
            "expected_answerability": expected_answerability,
            "actual_answerability": actual_answerability,
            "answerability_match": answerability_match,
            "sql_parse_status": sql_result["parse_status"],
            "read_only_status": sql_result["read_only_status"],
            "postgres_function_warning": sql_result[
                "postgres_function_warning"
            ],
            "sql_error": sql_result["sql_error"],
            "semantic_review_status": (
                "known_issue" if semantic_finding else "not_flagged"
            ),
            "semantic_finding": semantic_finding,
        })

    counts = {
        "experiment_records": len(experiment_records),
        "benchmark_questions": len(benchmark_records),
        "api_successes": sum(
            r.get("api_status") == "success"
            for r in experiment_records
        ),
        "contract_passed": sum(
            item["contract_status"] == "passed" for item in results
        ),
        "contract_failed": sum(
            item["contract_status"] == "failed" for item in results
        ),
        "sql_parse_passed": sum(
            item["sql_parse_status"] == "passed" for item in results
        ),
        "sql_parse_failed": sum(
            item["sql_parse_status"] == "failed" for item in results
        ),
        "read_only_passed": sum(
            item["read_only_status"] == "passed" for item in results
        ),
        "read_only_failed": sum(
            item["read_only_status"] == "failed" for item in results
        ),
        "answerability_matches": sum(
            item["answerability_match"] is True for item in results
        ),
        "answerability_mismatches": sum(
            item["answerability_match"] is False for item in results
        ),
        "known_semantic_findings": sum(
            item["semantic_review_status"] == "known_issue"
            for item in results
        ),
        "duplicate_question_ids": duplicate_ids,
        "missing_question_ids": missing_ids,
        "unexpected_question_ids": unexpected_ids,
        "prompt_versions": sorted({
            record.get("prompt_version")
            for record in experiment_records
        }),
        "expected_prompt_version": EXPECTED_PROMPT_VERSION,
        "sqlglot_version": sqlglot.__version__,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = OUTPUT_DIR / "groq_json_object_v2_evaluation.json"
    csv_path = OUTPUT_DIR / "groq_json_object_v2_evaluation.csv"
    md_path = OUTPUT_DIR / "groq_json_object_v2_evaluation.md"

    for path in (json_path, csv_path, md_path):
        if path.exists():
            raise FileExistsError(
                f"{path} already exists. Preserve it and choose a new "
                "output filename before rerunning."
            )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "experiment_file": str(EXPERIMENT_PATH.relative_to(ROOT)),
        "benchmark_file": str(BENCHMARK_PATH.relative_to(ROOT)),
        "evaluation_type": "offline; no SQL execution",
        "summary": counts,
        "results": results,
    }

    json_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    csv_fields = [
        "question_id",
        "api_status",
        "contract_status",
        "expected_answerability",
        "actual_answerability",
        "answerability_match",
        "sql_parse_status",
        "read_only_status",
        "postgres_function_warning",
        "semantic_review_status",
        "semantic_finding",
        "sql_error",
    ]

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=csv_fields)
        writer.writeheader()

        for item in results:
            row = dict(item)
            row["semantic_finding"] = (
                json.dumps(item["semantic_finding"])
                if item["semantic_finding"]
                else ""
            )
            writer.writerow({
                field: row.get(field)
                for field in csv_fields
            })

    lines = [
        "# Groq JSON-object v2 — Offline Evaluation",
        "",
        "> Historical v2 outputs evaluated offline. No SQL was executed.",
        "",
        "## Summary",
        "",
    ]

    for key, value in counts.items():
        lines.append(f"- **{key}:** {value}")

    lines.extend([
        "",
        "## Per-question findings",
        "",
        "| ID | Contract | PostgreSQL parse | Read-only | Answerability | Semantic review |",
        "|---|---|---|---|---|---|",
    ])

    for item in results:
        lines.append(
            f"| {item['question_id']} "
            f"| {item['contract_status']} "
            f"| {item['sql_parse_status']} "
            f"| {item['read_only_status']} "
            f"| {item['answerability_match']} "
            f"| {item['semantic_review_status']} |"
        )

    lines.extend([
        "",
        "## Known semantic findings",
        "",
    ])

    for item in results:
        finding = item["semantic_finding"]
        if finding:
            lines.append(
                f"- **{item['question_id']} ({finding['severity']}):** "
                f"{finding['finding']}"
            )

    lines.extend([
        "",
        "## Interpretation limitations",
        "",
        "- SQL parsing is not proof of semantic correctness.",
        "- Read-only AST checks are static checks, not database execution.",
        "- `not_flagged` means no issue was registered in the initial "
        "manual review; it does not mean the query is proven correct.",
        "- The benchmark's answerability labels are used as the comparison "
        "reference, not as proof of SQL correctness.",
        "- Historical v2 outputs are not relabelled as v3 generations.",
        "",
    ])

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print("\nOFFLINE EVALUATION COMPLETE")
    print("=" * 45)

    for key, value in counts.items():
        print(f"{key}: {value}")

    print("\nReports created:")
    print(json_path.relative_to(ROOT))
    print(csv_path.relative_to(ROOT))
    print(md_path.relative_to(ROOT))

    print("\nNo generated SQL was executed.")


if __name__ == "__main__":
    main()
