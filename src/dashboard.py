

from __future__ import annotations

import datetime as dt
import json
import os
from collections import Counter

from schema import CATEGORIES

RESULTS = os.path.join(os.path.dirname(__file__), "..", "data", "results.jsonl")
OUT = os.path.join(os.path.dirname(__file__), "..", "dashboard.html")

SECONDS_MANUAL = 180
SECONDS_AUTO = 20

CSS = """
:root{
  --bg:#0f1720; --panel:#17212e; --line:rgba(255,255,255,.08);
  --ink:#e6edf3; --mute:#8595a6; --amber:#ffb02e;
  --low:#3fb950; --med:#f5a623; --high:#f85149;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
  padding:32px;line-height:1.4}
.mono{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace}
.wrap{max-width:960px;margin:0 auto}
.label{background:var(--panel);border:1px solid var(--line);border-radius:10px;
  padding:20px 22px;display:flex;justify-content:space-between;align-items:flex-end;
  gap:20px;flex-wrap:wrap}
.label h1{margin:0;font-size:20px;letter-spacing:.02em}
.label .sub{color:var(--mute);font-size:12px;margin-top:6px}
.barcode{height:44px;flex:1;min-width:160px;border-radius:4px;
  background:repeating-linear-gradient(90deg,var(--ink) 0 2px,transparent 2px 4px,
  var(--ink) 4px 5px,transparent 5px 9px,var(--ink) 9px 12px,transparent 12px 14px);
  opacity:.85}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:12px;margin:18px 0}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px}
.kpi .n{font-size:30px;font-weight:650}
.kpi .k{color:var(--mute);font-size:11px;text-transform:uppercase;letter-spacing:.08em;margin-top:4px}
.kpi.accent .n{color:var(--amber)}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;
  padding:18px 20px;margin-top:14px}
.panel h2{margin:0 0 14px;font-size:12px;text-transform:uppercase;
  letter-spacing:.1em;color:var(--mute)}
.row{display:grid;grid-template-columns:190px 1fr 44px;align-items:center;
  gap:12px;margin:7px 0}
.row .name{font-size:13px;color:var(--ink)}
.track{background:rgba(255,255,255,.05);height:14px;border-radius:7px;overflow:hidden}
.fill{height:100%;background:var(--amber);border-radius:7px}
.row .v{text-align:right;font-size:13px;color:var(--mute)}
.urg{display:flex;gap:10px;flex-wrap:wrap}
.pill{border:1px solid var(--line);border-radius:8px;padding:12px 16px;flex:1;min-width:120px}
.pill .n{font-size:24px;font-weight:650}
.pill .k{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--mute);margin-top:2px}
.pill.low .n{color:var(--low)} .pill.med .n{color:var(--med)} .pill.high .n{color:var(--high)}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{text-align:left;padding:8px 6px;border-bottom:1px solid var(--line)}
th{color:var(--mute);font-weight:500;font-size:11px;text-transform:uppercase;letter-spacing:.06em}
td.arrow{color:var(--high)}
.foot{color:var(--mute);font-size:11px;margin-top:18px;text-align:center}
"""


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def bar(name, count, total):
    pct = (count / total * 100) if total else 0
    return (f'<div class="row"><div class="name">{name}</div>'
            f'<div class="track"><div class="fill" style="width:{pct:.0f}%"></div></div>'
            f'<div class="v mono">{count}</div></div>')


def main():
    rows = load(RESULTS)
    n = len(rows)
    correct = sum(r["category_correct"] for r in rows)
    acc = correct / n if n else 0
    saved = n * (SECONDS_MANUAL - SECONDS_AUTO) / 60
    cat_counts = Counter(r["prediction"]["category"] for r in rows)
    urg = Counter(r["prediction"]["urgency"] for r in rows)
    misses = [r for r in rows if not r["category_correct"]]
    backend = "Claude LLM" if os.getenv("ANTHROPIC_API_KEY") else "offline baseline"
    today = dt.date.today().isoformat()

    cat_bars = "".join(bar(c, cat_counts.get(c, 0), n) for c in CATEGORIES)
    urg_pills = "".join(
        f'<div class="pill {lvl}"><div class="n mono">{urg.get(lvl,0)}</div>'
        f'<div class="k">{lvl} urgency</div></div>'
        for lvl in ("low", "medium", "high")
    )
    miss_rows = "".join(
        f'<tr><td class="mono">{m["id"]}</td><td>{m["label_category"]}</td>'
        f'<td class="arrow">&rarr;</td><td>{m["prediction"]["category"]}</td></tr>'
        for m in misses
    ) or '<tr><td colspan="4">No misclassifications on this run.</td></tr>'

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Parcel Exception Triage — Dispatch Console</title><style>{CSS}</style></head>
<body><div class="wrap">
  <div class="label">
    <div><h1>PARCEL EXCEPTION TRIAGE</h1>
      <div class="sub mono">RUN {today} &nbsp;•&nbsp; BACKEND {backend} &nbsp;•&nbsp; {n} MESSAGES</div></div>
    <div class="barcode"></div>
  </div>

  <div class="kpis">
    <div class="kpi"><div class="n mono">{n}</div><div class="k">Handled</div></div>
    <div class="kpi accent"><div class="n mono">{acc:.0%}</div><div class="k">Category accuracy</div></div>
    <div class="kpi"><div class="n mono">{saved:.0f}</div><div class="k">Minutes saved</div></div>
    <div class="kpi"><div class="n mono">{urg.get('high',0)}</div><div class="k">Escalated</div></div>
  </div>

  <div class="panel"><h2>Volume by category</h2>{cat_bars}</div>
  <div class="panel"><h2>Urgency split</h2><div class="urg">{urg_pills}</div></div>
  <div class="panel"><h2>Error backlog — review these</h2>
    <table><thead><tr><th>ID</th><th>Labelled</th><th></th><th>Predicted</th></tr></thead>
    <tbody>{miss_rows}</tbody></table></div>

  <div class="foot mono">Generated by dashboard.py — synthetic evaluation data</div>
</div></body></html>"""

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {os.path.relpath(OUT)} — open it in a browser and screenshot it.")


if __name__ == "__main__":
    main()
