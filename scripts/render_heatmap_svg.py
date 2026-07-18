from __future__ import annotations

import html
import json
from datetime import date, datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "contributions.json"
OUTPUT = ROOT / "contrib-heatmap.svg"
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]


def level_for(count: int, stored_level: int) -> int:
    if 0 <= stored_level <= 5:
        return stored_level
    if count <= 0:
        return 0
    if count == 1:
        return 1
    if count <= 3:
        return 2
    if count <= 6:
        return 3
    if count <= 10:
        return 4
    return 5


def main() -> None:
    payload = json.loads(INPUT.read_text(encoding="utf-8"))
    days = {
        datetime.strptime(item["date"], "%Y-%m-%d").date(): item
        for item in payload.get("days", [])
    }
    today = date.today()
    start = today - timedelta(days=370)
    start -= timedelta(days=(start.weekday() + 1) % 7)
    cell = 12
    gap = 4
    left = 34
    top = 64
    cols = 53
    rows = 7
    width = 860
    height = 214

    rects = []
    month_labels = []
    seen_months: set[str] = set()
    for week in range(cols):
        week_start = start + timedelta(days=week * 7)
        month_key = week_start.strftime("%Y-%m")
        if week_start.day <= 7 and month_key not in seen_months:
            seen_months.add(month_key)
            month_labels.append(
                f'<text x="{left + week * (cell + gap)}" y="44" fill="#8b949e" font-size="11">{week_start.strftime("%b")}</text>'
            )
        for weekday in range(rows):
            current = week_start + timedelta(days=weekday)
            item = days.get(current, {"count": 0, "level": 0})
            count = int(item.get("count", 0))
            level = level_for(count, int(item.get("level", 0)))
            color = PALETTE[level]
            delay = (week + weekday) * 0.012
            opacity = "0.45" if current > today else "1"
            label = f"{count} contributions on {current.isoformat()}"
            rects.append(
                f'<rect x="{left + week * (cell + gap)}" y="{top + weekday * (cell + gap)}" width="{cell}" height="{cell}" rx="3" fill="{color}" opacity="{opacity}">'
                f"<title>{html.escape(label)}</title>"
                f'<animate attributeName="opacity" values="0;{opacity}" dur="0.35s" begin="{delay:.3f}s" fill="freeze" />'
                f'<animateTransform attributeName="transform" type="translate" from="0 -8" to="0 0" dur="0.35s" begin="{delay:.3f}s" fill="freeze" />'
                "</rect>"
            )

    total = int(payload.get("total", 0))
    current_streak = int(payload.get("current_streak", 0))
    longest_streak = int(payload.get("longest_streak", 0))
    best = payload.get("best_day", {"date": "-", "count": 0})
    source = str(payload.get("source", "github"))
    source_note = "auto-refreshed daily" if source == "github" else "cached data"

    legend_x = width - 184
    legend = [f'<text x="{legend_x - 34}" y="181" fill="#8b949e" font-size="11">Less</text>']
    for idx, color in enumerate(PALETTE):
        legend.append(
            f'<rect x="{legend_x + idx * 16}" y="171" width="11" height="11" rx="2" fill="{color}" />'
        )
    legend.append(f'<text x="{legend_x + 101}" y="181" fill="#8b949e" font-size="11">More</text>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="GitHub contribution heatmap for shubh-srivastava">
  <title>GitHub contribution heatmap for shubh-srivastava</title>
  <style>
    text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  </style>
  <rect width="100%" height="100%" rx="12" fill="#0d1117" />
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="11" fill="none" stroke="#30363d" />
  <text x="28" y="30" fill="#7ee787" font-size="14">shubh@github:~$ ./contributions.sh</text>
  {''.join(month_labels)}
  <g>
    {''.join(rects)}
  </g>
  <text x="28" y="181" fill="#c9d1d9" font-size="12">{total:,} contributions in the last year</text>
  <text x="28" y="199" fill="#8b949e" font-size="11">current streak: {current_streak}d | longest streak: {longest_streak}d | best day: {best.get("count", 0)} on {best.get("date", "-")} | {source_note}</text>
  {''.join(legend)}
</svg>
"""
    OUTPUT.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
