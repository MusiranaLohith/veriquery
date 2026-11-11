
import json
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

QUESTION_FILE = ROOT / "data/benchmark/dev/dev_questions.jsonl"
ANSWER_FILE = ROOT / "data/benchmark/dev/dev_answer_key.jsonl"


def load_jsonl(path):
    with path.open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


questions = load_jsonl(QUESTION_FILE)
answers = load_jsonl(ANSWER_FILE)

answer_map = {
    item["question_id"]: item
    for item in answers
}

# These are audit indicators, not automatic difficulty decisions.
patterns = {
    "where": "WHERE",
    "group_by": "GROUP BY",
    "having": "HAVING",
    "order_by": "ORDER BY",
    "limit": "LIMIT",
    "window_function": "OVER (",
    "cte": "WITH ",
    "case_expression": "CASE",
    "conditional_aggregation": "FILTER (WHERE",
    "distinct_aggregation": "COUNT(DISTINCT",
    "date_transformation": "DATE_TRUNC",
    "regex": "~ '",
    "subquery": "SELECT",
}

distribution = defaultdict(Counter)

print("=" * 85)
print("DEVELOPMENT BENCHMARK — DIFFICULTY VALIDITY AUDIT")
print("=" * 85)

for question in questions:
    qid = question["question_id"]
    answer = answer_map[qid]
    sql = answer.get("reference_sql", "").upper()

    detected = [
        label
        for label, pattern in patterns.items()
        if pattern in sql
    ]

    difficulty = question["difficulty"]
    distribution[difficulty]["questions"] += 1

    print(f"\n{qid} | Assigned difficulty: {difficulty}")
    print(f"Category: {question['category']}")
    print(f"Answerability: {question['answerability']}")
    print(f"Question: {question['question']}")
    print("Detected SQL features:", ", ".join(detected) or "Basic SQL")

print("\n" + "=" * 85)
print("ASSIGNED DIFFICULTY DISTRIBUTION")
print("=" * 85)

for difficulty in ["easy", "medium", "hard"]:
    print(f"{difficulty}: {distribution[difficulty]['questions']}")

print("\nAudit extraction complete.")
print(f"Questions inspected: {len(questions)}")
