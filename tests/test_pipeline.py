import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from classifier import classify_offline, _extract, _normalise  # noqa: E402
from schema import CATEGORIES, URGENCY_LEVELS, TRIAGE_TOOL  # noqa: E402


def test_offline_output_is_schema_valid():
    d = classify_offline("My parcel arrived broken", "customer_email", "en")
    assert d["category"] in CATEGORIES
    assert d["urgency"] in URGENCY_LEVELS
    assert isinstance(d["needs_customer_reply"], bool)
    assert set(d) >= set(TRIAGE_TOOL["input_schema"]["required"])


def test_damaged_is_high_urgency():
    d = classify_offline("The box was crushed and the item is broken", "customer_email", "en")
    assert d["category"] == "damaged_parcel"
    assert d["urgency"] == "high"


def test_german_customs_message():
    d = classify_offline("Mein Paket steckt im Zoll fest", "customer_email", "de")
    assert d["category"] == "customs_hold"


def test_tracking_extraction():
    assert _extract("Tracking DHL772100544 please", r"\b([A-Z]{2,4}\d{6,})\b") == "DHL772100544"


def test_normalise_rejects_garbage():
    out = _normalise({"category": "not_a_real_cat", "urgency": "extreme"})
    assert out["category"] in CATEGORIES
    assert out["urgency"] in URGENCY_LEVELS


def test_carrier_note_needs_no_reply():
    d = classify_offline("Delivery attempt failed, card left", "carrier_note", "en")
    assert d["needs_customer_reply"] is False
