from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
USERNAME = os.getenv("GITHUB_USERNAME", "shubh-srivastava")
OUTPUT = ROOT / "data" / "contributions.json"


def parse_count(label: str) -> int:
    first = label.split(" contribution", 1)[0].strip()
    if first in {"", "No", "0"}:
        return 0
    return int(first.replace(",", ""))


def fetch_days() -> list[dict[str, object]]:
    url = f"https://github.com/users/{USERNAME}/contributions"
    response = requests.get(
        url,
        headers={
            "User-Agent": "github-profile-readme-art/1.0",
            "Accept": "text/html,application/xhtml+xml",
        },
        timeout=20,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    days = []
    for node in soup.select(".ContributionCalendar-day[data-date]"):
        day = node.get("data-date")
        if not day:
            continue
        count_value = node.get("data-count")
        tooltip = soup.find("tool-tip", attrs={"for": node.get("id")})
        label = (
            node.get("aria-label")
            or node.get("data-tooltip-text")
            or (tooltip.get_text(strip=True) if tooltip else "")
        )
        count = int(count_value) if count_value not in {None, ""} else parse_count(label)
        level_value = node.get("data-level")
        level = int(level_value) if level_value not in {None, ""} else min(5, count)
        days.append({"date": day, "count": count, "level": level})

    unique = {item["date"]: item for item in days}
    if not unique:
        raise RuntimeError("No contribution cells found in GitHub response")
    return [unique[key] for key in sorted(unique)]


def empty_days() -> list[dict[str, object]]:
    today = date.today()
    start = today - timedelta(days=370)
    return [
        {"date": (start + timedelta(days=offset)).isoformat(), "count": 0, "level": 0}
        for offset in range(371)
    ]


def streaks(counts_by_date: dict[date, int]) -> tuple[int, int]:
    if not counts_by_date:
        return 0, 0

    all_days = sorted(counts_by_date)
    longest = 0
    current_run = 0
    for day in all_days:
        if counts_by_date[day] > 0:
            current_run += 1
            longest = max(longest, current_run)
        else:
            current_run = 0

    current = 0
    cursor = date.today()
    while counts_by_date.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)
    return current, longest


def summarize(days: list[dict[str, object]], source: str) -> dict[str, object]:
    parsed = {
        datetime.strptime(str(item["date"]), "%Y-%m-%d").date(): int(item["count"])
        for item in days
    }
    current, longest = streaks(parsed)
    total = sum(parsed.values())
    best_day = max(parsed.items(), key=lambda item: item[1]) if parsed else (date.today(), 0)
    monthly: dict[str, int] = defaultdict(int)
    for day, count in parsed.items():
        monthly[day.strftime("%Y-%m")] += count

    return {
        "username": USERNAME,
        "source": source,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best_day[0].isoformat(), "count": best_day[1]},
        "monthly": dict(sorted(monthly.items())),
        "days": days,
    }


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    source = "github"
    try:
        days = fetch_days()
    except Exception as exc:
        if OUTPUT.exists():
            existing = json.loads(OUTPUT.read_text(encoding="utf-8"))
            days = existing.get("days", empty_days())
            source = f"cached: {exc}"
        else:
            days = empty_days()
            source = f"empty fallback: {exc}"

    OUTPUT.write_text(json.dumps(summarize(days, source), indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
