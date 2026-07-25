


from __future__ import annotations

import json
import random
import sys

CARRIERS = ["DHL", "GLS", "DPD", "HER", "UPS", "PN"]
COUNTRIES = ["Germany", "France", "Italy", "Netherlands", "Spain", "Austria"]

# (category, language, urgency, template). {trk}=tracking, {ord}=order id.
TEMPLATES: list[tuple[str, str, str, str]] = [
    ("delayed", "en", "medium", "Hi, my parcel {trk} was due days ago but the status hasn't changed. Order {ord}. Where is it?"),
    ("delayed", "en", "low", "Just checking on {trk} — still shows in transit, no update for several days."),
    ("delayed", "de", "medium", "Wann kommt mein Paket {trk} endlich? Sollte laut Shop schon da sein. Bestellung {ord}."),
    ("delayed", "en", "medium", "Carrier note: shipment {trk} delayed in transit hub, expected 24-48h late."),

    ("failed_delivery_attempt", "en", "low", "Delivery attempt failed, recipient not home. Card left, retry next day. Tracking {trk}."),
    ("failed_delivery_attempt", "en", "low", "First delivery attempt missed while I was at work. How do I reschedule {trk}?"),
    ("failed_delivery_attempt", "de", "medium", "Zusteller sagt niemand war da, aber ich war zu Hause. Keine Benachrichtigung. {trk}."),
    ("failed_delivery_attempt", "en", "low", "Attempted delivery, business closed. Second attempt scheduled tomorrow. {trk}."),

    ("damaged_parcel", "en", "high", "My parcel {trk} arrived with the box torn open and the contents broken. What now?"),
    ("damaged_parcel", "de", "high", "Mein Paket {trk} kam an, aber der Karton war aufgerissen und der Inhalt beschädigt."),
    ("damaged_parcel", "en", "high", "Box arrived soaked and crushed, the item inside no longer works. Tracking {trk}."),
    ("damaged_parcel", "en", "low", "Got {trk} today, outer box a bit dented but items inside are fine. Just flagging it."),

    ("customs_hold", "en", "medium", "Shipment {trk} held at customs, extra documentation required for clearance."),
    ("customs_hold", "de", "medium", "Mein Paket {trk} steckt im Zoll fest. Muss ich etwas bezahlen oder Dokumente schicken?"),
    ("customs_hold", "en", "medium", "Package sat in customs for two weeks and now there's an import fee. Options? {trk}."),
    ("customs_hold", "en", "low", "Customs clearance completed, duties paid, out for delivery. Tracking {trk}."),

    ("address_issue", "en", "medium", "I gave the wrong delivery address for order {ord}. Can you redirect {trk}?"),
    ("address_issue", "de", "medium", "Ich habe eine falsche Lieferadresse angegeben. Können Sie {trk} umleiten? Bestellung {ord}."),
    ("address_issue", "en", "high", "Wrong postcode was auto-filled, package {trk} is going to the wrong city. Please help fast."),
    ("address_issue", "en", "medium", "Carrier note: address incomplete, house number missing on {trk}, returned to depot."),

    ("lost_parcel", "en", "high", "It's been three weeks and {trk} still hasn't moved past 'in transit'. I think it's lost."),
    ("lost_parcel", "de", "high", "Die Sendungsverfolgung {trk} zeigt seit 10 Tagen keinen neuen Status. Verloren?"),
    ("lost_parcel", "en", "high", "Item {trk} lost in network, no scan for 15 days. Investigation opened."),
    ("lost_parcel", "en", "high", "Tracking {trk} hasn't updated since it left the sorting centre 12 days ago. Missing."),

    ("delivered_not_received", "en", "high", "Tracking {trk} says delivered yesterday but I never got anything and was home all day."),
    ("delivered_not_received", "de", "high", "Paket {trk} wurde als zugestellt markiert, aber ich habe nichts erhalten. Bitte dringend prüfen."),
    ("delivered_not_received", "en", "high", "Marked delivered but nothing here and no note. Checked the whole building. {trk}."),
    ("delivered_not_received", "en", "high", "The locker code you sent for {trk} doesn't open any box. I can't get my package."),

    ("return_to_sender", "en", "medium", "Parcel {trk} undeliverable after 3 attempts, now returning to sender. I really need this."),
    ("return_to_sender", "de", "low", "Kann ich {trk} zurückschicken lassen? Ich möchte Bestellung {ord} stornieren."),
    ("return_to_sender", "en", "low", "Recipient refused delivery of {trk}, being returned to origin warehouse."),
    ("return_to_sender", "en", "high", "This is the third failed attempt and now {trk} is going back to the sender."),
]


def _trk() -> str:
    return f"{random.choice(CARRIERS)}{random.randint(100000, 9999999)}"


def _ord() -> str:
    return str(random.randint(100000, 109999))


def generate(n: int) -> list[dict]:
    rows = []
    for i in range(n):
        cat, lang, urg, tpl = random.choice(TEMPLATES)
        text = tpl.replace("{trk}", _trk()).replace("{ord}", _ord())
        channel = "carrier_note" if text.lower().startswith("carrier note") else "customer_email"
        rows.append(
            {
                "id": f"GEN-{i+1:05d}",
                "channel": channel,
                "language": lang,
                "text": text,
                "label_category": cat,
                "label_urgency": urg,
            }
        )
    return rows


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    out = sys.argv[2] if len(sys.argv) > 2 else "data/exceptions_large.jsonl"
    random.seed(42)  # reproducible
    rows = generate(n)
    with open(out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote {len(rows)} messages to {out}")
    print("Run it through the pipeline with:")
    print(f"  DATA={out} python src/triage.py")


if __name__ == "__main__":
    main()
