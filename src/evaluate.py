

from __future__ import annotations

import json
import os
from collections import defaultdict

RESULTS = os.path.join(os.path.dirname(__file__), "..", "data", "results.jsonl")

# --- Assumptions you would agree with the ops team (document them!) -----------
SECONDS_MANUAL_PER_MSG = 180     # ~3 min to read, categorise and route by hand
SECONDS_AUTOMATED_PER_MSG = 20   # human just reviews the drafted decision


def load(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> None:
    rows = load(RESULTS)
    n = len(rows)
    correct = sum(r["category_correct"] for r in rows)
    accuracy = correct / n if n else 0.0

    # Per-category accuracy — shows *where* it fails, not just an average.
    per_cat_total: dict[str, int] = defaultdict(int)
    per_cat_correct: dict[str, int] = defaultdict(int)
    for r in rows:
        label = r["label_category"]
        per_cat_total[label] += 1
        per_cat_correct[label] += int(r["category_correct"])

    # Business metrics
    time_manual = n * SECONDS_MANUAL_PER_MSG
    time_auto = n * SECONDS_AUTOMATED_PER_MSG
    time_saved_min = (time_manual - time_auto) / 60
    high_urgency = sum(r["prediction"]["urgency"] == "high" for r in rows)

    print("=" * 56)
    print("PARCEL EXCEPTION TRIAGE — RESULTS")
    print("=" * 56)
    print(f"Messages handled (volume) : {n}")
    print(f"Category accuracy         : {accuracy:6.1%}  ({correct}/{n})")
    print(f"Flagged high-urgency      : {high_urgency}")
    print(f"Est. manual time          : {time_manual/60:6.1f} min")
    print(f"Est. automated time       : {time_auto/60:6.1f} min")
    print(f"Est. time saved           : {time_saved_min:6.1f} min "
          f"(~{time_saved_min/max(n,1):.1f} min/msg)")
    print("-" * 56)
    print("Accuracy by category (find the weak spots):")
    for cat in sorted(per_cat_total):
        tot = per_cat_total[cat]
        acc = per_cat_correct[cat] / tot
        print(f"  {cat:>24}: {acc:5.0%}  ({per_cat_correct[cat]}/{tot})")

    misses = [r for r in rows if not r["category_correct"]]
    if misses:
        print("-" * 56)
        print("Misclassified (your error-analysis backlog):")
        for r in misses:
            print(f"  {r['id']}: labelled {r['label_category']} "
                  f"-> predicted {r['prediction']['category']}")
    print("=" * 56)


if __name__ == "__main__":
    main()
