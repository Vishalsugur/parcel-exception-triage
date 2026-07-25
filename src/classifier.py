

from __future__ import annotations

import os
import re
from typing import Optional

from schema import TRIAGE_TOOL, CATEGORIES

# Fast + cheap model, ideal for high-volume classification. Bump to
# "claude-sonnet-5" if you ever need more nuance on tricky messages.
MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = (
    "You are the triage assistant for a cross-border parcel-delivery company. "
    "You read one inbound message — either a customer email or an internal "
    "carrier status note — and record a triage decision by calling the "
    "record_triage tool. Always reply to customers in their own language "
    "(English or German). Be accurate and conservative: only mark urgency "
    "'high' when a parcel is damaged, lost, missing after delivery, or a "
    "customer is clearly upset."
)


def classify_with_llm(text: str, channel: str, language: str) -> dict:
    """Call Claude and return the structured triage dict.

    Requires: pip install anthropic, and ANTHROPIC_API_KEY in the environment.
    """
    import anthropic  # imported lazily so offline runs need no dependency

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the env

    user_content = (
        f"Channel: {channel}\n"
        f"Language: {language}\n"
        f"Message:\n{text}"
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        system=SYSTEM_PROMPT,
        tools=[TRIAGE_TOOL],
        # tool_choice forces the model to call record_triage every time,
        # so we always get a schema-valid object back — no JSON parsing of prose.
        tool_choice={"type": "tool", "name": "record_triage"},
        messages=[{"role": "user", "content": user_content}],
    )

    # The structured answer lives in the tool_use block's `input`.
    for block in response.content:
        if block.type == "tool_use" and block.name == "record_triage":
            return _normalise(block.input)

    raise RuntimeError("Model did not return the expected tool call.")


# --- Offline keyword baseline -------------------------------------------------

# Very small, readable rule set. Order matters: earlier rules win.
_RULES: list[tuple[str, str]] = [
    ("damaged_parcel", r"beschädigt|aufgerissen|damaged|crushed|smashed|broken|dented|soaked|leaked"),
    ("delivered_not_received", r"delivered.*(never|nothing|no parcel|didn'?t)|als zugestellt.*nichts|locker.*(code|open)|marked as delivered"),
    ("customs_hold", r"customs|zoll|clearance|import fee|duties|commercial invoice"),
    ("lost_parcel", r"lost|verloren|missing|no scan|hasn'?t (updated|moved).*(week|days)|kein neuer status"),
    ("return_to_sender", r"return(ing)? to (sender|origin)|zurückschicken|zurück.*warehouse|refused|storniere"),
    ("address_issue", r"address|adresse|postcode|postleitzahl|house number|umleiten|moved|wrong (city|address)|incomplete"),
    ("failed_delivery_attempt", r"attempt|zustell|niemand war|not at home|business closed|missed|card left|retry"),
    ("delayed", r"delay|verspät|hasn'?t (arrived|changed)|no.*update|still.*(transit|processing)|wann kommt|endlich"),
]

_HIGH = re.compile(r"damaged|crushed|smashed|broken|beschädigt|lost|verloren|missing|never received|nichts erhalten|urgent|dringend|third|3 attempts|really need", re.I)
_LOW = re.compile(r"just letting you know|all good|no problem|fine though|card left|retry|reschedule", re.I)


def classify_offline(text: str, channel: str, language: str) -> dict:
    lowered = text.lower()
    category = "delayed"  # safe default
    for cat, pattern in _RULES:
        if re.search(pattern, lowered, re.I):
            category = cat
            break

    if _HIGH.search(text):
        urgency = "high"
    elif _LOW.search(text):
        urgency = "low"
    else:
        urgency = "medium"

    return _normalise(
        {
            "category": category,
            "urgency": urgency,
            "tracking_id": _extract(text, r"\b([A-Z]{2,4}\d{6,})\b|\b(1Z[0-9A-Z]+)\b"),
            "order_id": _extract(text, r"(?:order|bestellung|bestellnummer)\D{0,6}(\d{5,6})"),
            "needs_customer_reply": channel == "customer_email",
            "suggested_reply": "",  # the baseline does not draft replies
        }
    )


# --- Helpers ------------------------------------------------------------------

def _extract(text: str, pattern: str) -> Optional[str]:
    m = re.search(pattern, text, re.I)
    if not m:
        return None
    return next((g for g in m.groups() if g), None)


def _normalise(raw: dict) -> dict:
    """Guard against anything off-schema so downstream code never crashes."""
    cat = raw.get("category")
    if cat not in CATEGORIES:
        cat = "delayed"
    urg = raw.get("urgency")
    if urg not in ("low", "medium", "high"):
        urg = "medium"
    return {
        "category": cat,
        "urgency": urg,
        "tracking_id": raw.get("tracking_id"),
        "order_id": raw.get("order_id"),
        "needs_customer_reply": bool(raw.get("needs_customer_reply", False)),
        "suggested_reply": raw.get("suggested_reply", "") or "",
    }


def classify(text: str, channel: str, language: str) -> dict:
    """Dispatch to the LLM when a key is present, else the offline baseline."""
    if os.getenv("ANTHROPIC_API_KEY"):
        return classify_with_llm(text, channel, language)
    return classify_offline(text, channel, language)
