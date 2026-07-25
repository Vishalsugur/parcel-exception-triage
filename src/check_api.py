

from __future__ import annotations

import os
import sys


def main() -> int:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        print("x  ANTHROPIC_API_KEY is not set.")
        print("   The pipeline will run the OFFLINE baseline until you set it.")
        print("   macOS/Linux : export ANTHROPIC_API_KEY=sk-ant-...")
        print('   Windows PS  : $env:ANTHROPIC_API_KEY="sk-ant-..."')
        return 1

    print(f"ok  Key found (starts with {key[:7]}..., length {len(key)}).")

    try:
        import anthropic
    except ModuleNotFoundError:
        print("x  The 'anthropic' package isn't installed.")
        print("   Run: pip install -r requirements.txt")
        return 1

    try:
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=16,
            messages=[{"role": "user", "content": "Reply with exactly: OK"}],
        )
        text = "".join(b.text for b in resp.content if b.type == "text").strip()
        print(f"ok  Live call succeeded. Model replied: {text!r}")
        print(f"    Tokens used: in={resp.usage.input_tokens}, out={resp.usage.output_tokens}")
        print("\nYou're connected. Run:  python src/triage.py")
        return 0
    except anthropic.AuthenticationError:
        print("x  Key was rejected (AuthenticationError). Double-check you copied it correctly.")
    except anthropic.RateLimitError:
        print("x  Rate limited / out of credit. Check your usage at console.anthropic.com.")
    except Exception as e:  # noqa: BLE001
        print(f"x  Call failed: {type(e).__name__}: {e}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
