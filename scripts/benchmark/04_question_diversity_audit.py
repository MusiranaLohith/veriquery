
import json
from collections import defaultdict
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

print("=" * 75)
print("DEVELOPMENT QUESTION DIVERSITY AUDIT")
print("=" * 75)

for question in questions:
    qid = question["question_id"]
    answer = answer_map[qid]

    print(f"\n{qid} | {question['difficulty']} | {question['category']}")
    print("Question:", question["question"])
    print("SQL:", answer["reference_sql"])

print("\n" + "=" * 75)
print("AUDIT COMPLETE")
print(f"Questions inspected: {len(questions)}")
