
import json
from collections import Counter, defaultdict
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

difficulty_counts = defaultdict(Counter)
category_counts = defaultdict(Counter)
overall = Counter()

for question in questions:
    qid = question["question_id"]
    result = answer_map[qid]["expected_result"]

    if isinstance(result, list):
        rows = len(result)
    elif isinstance(result, dict):
        rows = 1
    else:
        rows = 0

    if rows == 1:
        group = "one_row"
    elif rows > 1:
        group = "multiple_rows"
    else:
        group = "zero_or_unknown"

    overall[group] += 1
    difficulty_counts[question["difficulty"]][group] += 1
    category_counts[question["category"]][group] += 1

print("=" * 60)
print("OVERALL RESULT CARDINALITY")
print("=" * 60)

for group, count in overall.items():
    print(f"{group}: {count}")

print("\n" + "=" * 60)
print("CARDINALITY BY DIFFICULTY")
print("=" * 60)

for difficulty, counts in sorted(difficulty_counts.items()):
    print(f"\n{difficulty}")
    for group, count in counts.items():
        print(f"  {group}: {count}")

print("\n" + "=" * 60)
print("CARDINALITY BY CATEGORY")
print("=" * 60)

for category, counts in sorted(category_counts.items()):
    print(f"\n{category}")
    for group, count in counts.items():
        print(f"  {group}: {count}")

print("\nAudit complete.")
