# The no-code twin: building this in Make.com

The Python project proves you can build the logic. The Make.com scenario proves
you can ship it as a **no-code automation a non-developer could maintain** — which
is literally what the Seven Senders AI Taskforce does. Build both; they tell the
same story at two levels.

The whole thing runs on Make's **free plan** (1,000 credits/month, 2 active
scenarios). You do not even need your own API key to start: Make's built-in AI
Toolkit works on every plan. Swap in the native Anthropic Claude module later
when you want to use your own key.

## The scenario, module by module

1. **Webhook (trigger)** — "Custom webhook". This receives one message as JSON:
   `{ "channel": "...", "language": "...", "text": "..." }`. In production this
   would be your mailbox or ticketing tool; for the demo you POST test messages
   to the webhook URL with any HTTP client.

2. **AI module — classify + extract** (Make AI Toolkit, or the Anthropic Claude
   module). Paste a system prompt matching `src/schema.py`, ask it to return the
   same fields (category, urgency, tracking_id, order_id, needs_customer_reply,
   suggested_reply), and tell it to return **JSON only**.

3. **JSON → Parse JSON.** Turns the model's string into real fields you can map.

4. **Router** — this is your "agentic" decision step, and the part that impresses:
   - Route A — `urgency = high` → post to a Slack/Teams channel for a human now.
   - Route B — `needs_customer_reply = true` → create a draft reply email
     (drafted, **not** auto-sent — keep a human in the loop).
   - Route C — everything else → just log it.

5. **Google Sheets — "Add a row".** Append every decision (id, category, urgency,
   correct?, timestamp). This sheet becomes your metrics dashboard — the same
   numbers `evaluate.py` prints, now live.

## Why this shape wins the interview

- **Human-in-the-loop:** replies are drafted, high-urgency items are escalated to
  a person. You never let the model auto-send. Say this out loud — it shows
  judgement, and it echoes the trustworthy-AI framing already on your CV.
- **Observable:** every step's input and output is visible in Make's canvas, and
  every decision lands in a sheet. You can prove it works and show where it fails.
- **Measured:** the sheet gives you volume, category mix, and (against a labelled
  sample) accuracy — the exact "time saved, error rates, volume handled" the JD
  asks for.

## Build order (a weekend)

Sat AM: get the Python baseline running (done). Sat PM: read the Make.com "LLM
integration" how-to, build modules 1–3, test with 3 messages. Sun: add the router
+ Sheets logging, run all 36 sample messages through, screenshot the sheet and the
canvas for your write-up.
