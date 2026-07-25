

CATEGORIES = [
    "delayed",                 # in transit longer than promised, no bigger problem yet
    "failed_delivery_attempt", # courier tried but could not hand over
    "damaged_parcel",          # box or contents arrived damaged
    "customs_hold",            # stuck in customs / clearance / duties
    "address_issue",           # wrong / incomplete / changed delivery address
    "lost_parcel",             # no scan for a long time, likely lost in network
    "delivered_not_received",  # marked delivered but customer has nothing
    "return_to_sender",        # being sent back to the warehouse
]

URGENCY_LEVELS = ["low", "medium", "high"]


TRIAGE_TOOL = {
    "name": "record_triage",
    "description": (
        "Record the triage decision for one inbound parcel-exception message "
        "(a customer email or a carrier status note)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": CATEGORIES,
                "description": "The single best-fitting exception category.",
            },
            "urgency": {
                "type": "string",
                "enum": URGENCY_LEVELS,
                "description": (
                    "How urgently a human should act. 'high' for damage, "
                    "lost/missing parcels, or an angry customer at risk of churn; "
                    "'low' for routine, self-resolving updates."
                ),
            },
            "tracking_id": {
                "type": ["string", "null"],
                "description": "The tracking / shipment number if present, else null.",
            },
            "order_id": {
                "type": ["string", "null"],
                "description": "The order / reference number if present, else null.",
            },
            "needs_customer_reply": {
                "type": "boolean",
                "description": "True if the customer is waiting on an answer from us.",
            },
            "suggested_reply": {
                "type": "string",
                "description": (
                    "A short, empathetic draft reply to the customer in THEIR "
                    "language (English or German). One or two sentences. Leave "
                    "empty for internal carrier notes that need no reply."
                ),
            },
        },
        "required": [
            "category",
            "urgency",
            "needs_customer_reply",
            "suggested_reply",
        ],
    },
}
