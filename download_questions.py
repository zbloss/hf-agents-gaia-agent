from utils import get_questions
import json
import os

QUESTIONS_FILEPATH: str = os.getenv("QUESTIONS_FILEPATH", default="metadata.jsonl")


if __name__ == "__main__":
    questions: list[dict] = get_questions()

    # 2. Save to JSON file
    with open(QUESTIONS_FILEPATH, "w") as f:
        json.dump(questions, f, indent=4)

    print(f"Saved {len(questions)} questions to {QUESTIONS_FILEPATH}")
