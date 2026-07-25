

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from classifier import classify, MODEL  # noqa: E402

app = FastAPI(
    title="Parcel Exception Triage API",
    description="Classify and route inbound parcel-delivery exception messages.",
    version="1.0.0",
)


class Message(BaseModel):
    text: str
    channel: str = "customer_email"   # or "carrier_note"
    language: str = "en"              # or "de"


@app.get("/health")
def health() -> dict:
    """Liveness + which backend is active, so ops can see it at a glance."""
    return {
        "status": "ok",
        "backend": "llm" if os.getenv("ANTHROPIC_API_KEY") else "offline_baseline",
        "model": MODEL,
    }


@app.post("/triage")
def triage(msg: Message) -> dict:
    """Classify one message and return the structured decision + a routing hint."""
    decision = classify(msg.text, msg.channel, msg.language)

    # The routing hint is the 'agentic' decision Make.com (or any caller) acts on.
    if decision["urgency"] == "high":
        route = "escalate_to_human"
    elif decision["needs_customer_reply"]:
        route = "draft_customer_reply"
    else:
        route = "log_only"

    return {"decision": decision, "route": route}
