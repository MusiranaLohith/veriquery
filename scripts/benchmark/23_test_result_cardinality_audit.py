
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

QUESTION_FILE = (
    ROOT / "data/benchmark/locked_test/test_questions.jsonl"
)
ANSWER_FILE = (
    ROOT / "data/benchmark/locked_test/test_answer_key.jsonl"
)


def load_jsonl(path):
    with path.open(encoding="utf-8") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


questions = load_jsonl(QUESTION_FILE)
answers = load_jsonl(ANSWER_FILE)

answer_map = {
    item["question_id"]: item
    for item in answers
}

difficulty_counts = defaultdict(Counter)
category_counts = defaultdict(Counter)
overall = Counter()
unanswerable_counts = Counter()

for question in questions:
    qid = question["question_id"]
    answerability = question["answerability"]

    if answerability == "unanswerable":
        unanswerable_counts[question["category"]] += 1
        continue

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


print("=" * 65)
print("LOCKED-TEST — ANSWERABLE RESULT CARDINALITY")
print("=" * 65)

for group in ["one_row", "multiple_rows", "zero_or_unknown"]:
    print(f"{group}: {overall[group]}")

print("Total answerable questions:", sum(overall.values()))

print("\n" + "=" * 65)
print("CARDINALITY BY DIFFICULTY")
print("=" * 65)

for difficulty in ["easy", "medium", "hard"]:
    print(f"\n{difficulty}")
    for group in ["one_row", "multiple_rows", "zero_or_unknown"]:
        print(f"  {group}: {difficulty_counts[difficulty][group]}")


print("\n" + "=" * 65)
print("CARDINALITY BY CATEGORY")
print("=" * 65)

for category, counts in sorted(category_counts.items()):
    print(f"\n{category}")
    for group in ["one_row", "multiple_rows", "zero_or_unknown"]:
        print(f"  {group}: {counts[group]}")


print("\n" + "=" * 65)
print("UNANSWERABLE QUESTIONS — REPORTED SEPARATELY")
print("=" * 65)

for category, count in sorted(unanswerable_counts.items()):
    print(f"{category}: {count}")

print("Total unanswerable questions:", sum(unanswerable_counts.values()))

print("\nAudit complete.")
