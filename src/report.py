

from __future__ import annotations

import json
import os
from collections import defaultdict

from schema import CATEGORIES

RESULTS = os.path.join(os.path.dirname(__file__), "..", "data", "results.jsonl")


def load(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> None:
    rows = load(RESULTS)

    # confusion[true][pred] = count
    confusion: dict[str, dict[str, int]] = {c: defaultdict(int) for c in CATEGORIES}
    for r in rows:
        confusion[r["label_category"]][r["prediction"]["category"]] += 1

    # per-class precision / recall / F1
    print("Per-class metrics")
    print(f"{'category':>24} {'prec':>6} {'recall':>7} {'f1':>6} {'support':>8}")
    macro_f1 = 0.0
    for c in CATEGORIES:
        tp = confusion[c][c]
        fp = sum(confusion[o][c] for o in CATEGORIES if o != c)
        fn = sum(confusion[c][o] for o in CATEGORIES if o != c)
        support = tp + fn
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        macro_f1 += f1
        if support:
            print(f"{c:>24} {prec:6.2f} {rec:7.2f} {f1:6.2f} {support:8d}")
    print(f"\nMacro F1: {macro_f1/len(CATEGORIES):.3f}")

    # compact confusion matrix (rows=true, cols=pred), short labels
    short = {c: c[:8] for c in CATEGORIES}
    print("\nConfusion matrix (rows = true, cols = predicted)")
    header = " " * 24 + "".join(f"{short[c]:>9}" for c in CATEGORIES)
    print(header)
    for c in CATEGORIES:
        cells = "".join(f"{confusion[c][p]:>9}" for p in CATEGORIES)
        print(f"{c:>24}{cells}")


if __name__ == "__main__":
    main()
