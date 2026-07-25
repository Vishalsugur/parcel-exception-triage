

from __future__ import annotations

import json
import os
import sys
import time

# allow "python src/triage.py" from the project root
sys.path.insert(0, os.path.dirname(__file__))

from classifier import classify  # noqa: E402

_HERE = os.path.dirname(__file__)
# Override the input with e.g.  DATA=data/exceptions_large.jsonl python src/triage.py
DATA = os.getenv("DATA") or os.path.join(_HERE, "..", "data", "exceptions.jsonl")
OUT = os.getenv("OUT") or os.path.join(_HERE, "..", "data", "results.jsonl")


def load(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> None:
    rows = load(DATA)
    mode = "LLM (Claude)" if os.getenv("ANTHROPIC_API_KEY") else "offline baseline"
    print(f"Classifying {len(rows)} messages using the {mode}...\n")

    results = []
    t0 = time.time()
    for row in rows:
        decision = classify(row["text"], row["channel"], row["language"])
        correct = decision["category"] == row["label_category"]
        results.append({**row, "prediction": decision, "category_correct": correct})
        mark = "ok " if correct else "MISS"
        print(f"  [{mark}] {row['id']}  {row['label_category']:>24}  ->  {decision['category']}")

    elapsed = time.time() - t0
    with open(OUT, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\nDone in {elapsed:.1f}s. Wrote {len(results)} rows to {os.path.relpath(OUT)}")
    print("Now run:  python src/evaluate.py")


if __name__ == "__main__":
    main()
