
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

QUESTION_FILE = ROOT / "data/benchmark/locked_test/test_questions.jsonl"
ANSWER_FILE = ROOT / "data/benchmark/locked_test/test_answer_key.jsonl"


def load_jsonl(path):
    with path.open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


questions = load_jsonl(QUESTION_FILE)
answers = load_jsonl(ANSWER_FILE)

answer_map = {
    item["question_id"]: item
    for item in answers
}

print("=" * 65)
print("LOCKED-TEST BENCHMARK — SQL COMPLEXITY AUDIT")
print("=" * 65)

for question in questions:
    qid = question["question_id"]
    answer = answer_map.get(qid)

    if answer is None:
        print(f"{qid}: MISSING ANSWER KEY")
        continue

    sql = answer.get("reference_sql", "").upper()
    result = answer.get("expected_result")

    if isinstance(result, list):
        cardinality = len(result)
    elif isinstance(result, dict):
        cardinality = 1
    else:
        cardinality = 0

    features = {
        "JOIN": "JOIN" in sql,
        "CTE": "WITH " in sql,
        "GROUP BY": "GROUP BY" in sql,
        "HAVING": "HAVING" in sql,
        "WINDOW": "OVER (" in sql,
        "SUBQUERY": "SELECT" in sql[sql.find("FROM") + 4:],
        "FILTER": "FILTER (WHERE" in sql,
        "ORDER BY": "ORDER BY" in sql,
        "LIMIT": "LIMIT" in sql,
    }

    complexity_signals = sum(features.values())

    print(
        f"{qid} | "
        f"{question['difficulty']:<6} | "
        f"{question['category']:<38} | "
        f"rows={cardinality:<3} | "
        f"signals={complexity_signals}"
    )

print("\nAudit extraction complete.")
print(f"Questions: {len(questions)}")
print(f"Answer keys: {len(answers)}")
