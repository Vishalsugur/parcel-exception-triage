

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from schema import TRIAGE_TOOL  # noqa: E402
from classifier import MODEL, SYSTEM_PROMPT, _normalise  # noqa: E402


def build_requests(rows: list[dict]) -> list[dict]:
    reqs = []
    for r in rows:
        reqs.append(
            {
                "custom_id": r["id"],
                "params": {
                    "model": MODEL,
                    "max_tokens": 512,
                    "system": SYSTEM_PROMPT,
                    "tools": [TRIAGE_TOOL],
                    "tool_choice": {"type": "tool", "name": "record_triage"},
                    "messages": [
                        {
                            "role": "user",
                            "content": (
                                f"Channel: {r['channel']}\n"
                                f"Language: {r['language']}\n"
                                f"Message:\n{r['text']}"
                            ),
                        }
                    ],
                },
            }
        )
    return reqs


def main() -> None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("Set ANTHROPIC_API_KEY first — the batch API needs a real key.")
    import anthropic

    path = sys.argv[1] if len(sys.argv) > 1 else "data/exceptions_large.jsonl"
    with open(path, encoding="utf-8") as f:
        rows = [json.loads(l) for l in f if l.strip()]

    client = anthropic.Anthropic()
    print(f"Submitting {len(rows)} requests as one batch...")
    batch = client.messages.batches.create(requests=build_requests(rows))

    while True:
        batch = client.messages.batches.retrieve(batch.id)
        if batch.processing_status == "ended":
            break
        print(f"  status={batch.processing_status} ... waiting")
        time.sleep(10)

    decisions: dict[str, dict] = {}
    for result in client.messages.batches.results(batch.id):
        if result.result.type == "succeeded":
            for block in result.result.message.content:
                if block.type == "tool_use":
                    decisions[result.custom_id] = _normalise(block.input)

    out = "data/results.jsonl"
    with open(out, "w", encoding="utf-8") as f:
        for r in rows:
            dec = decisions.get(r["id"])
            if not dec:
                continue
            f.write(json.dumps(
                {**r, "prediction": dec,
                 "category_correct": dec["category"] == r["label_category"]},
                ensure_ascii=False) + "\n")
    print(f"Done. Wrote {len(decisions)} results to {out}. Now: python src/evaluate.py")


if __name__ == "__main__":
    main()
