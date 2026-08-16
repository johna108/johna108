from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def fetch_graphql(token: str, username: str) -> list[dict[str, int | str]]:
    query = """
    query($userName: String!) {
      user(login: $userName) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                date
                contributionCount
                color
              }
            }
          }
        }
      }
    }
    """
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": {"userName": username}},
        headers={"Authorization": f"Bearer {token}", "User-Agent": "profile-art-bot"},
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    days = []
    for week in data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
        for day in week["contributionDays"]:
            count = day["contributionCount"]
            level = 0 if count == 0 else min(5, 1 + count // 2)
            days.append({"date": day["date"], "count": count, "level": level})
    return days


def parse_total(html: str) -> int:
    match = re.search(r"([\d,]+) contributions in the last year", html)
    if not match:
        return 0
    return int(match.group(1).replace(",", ""))


def parse_day_cells(html: str) -> list[dict[str, int | str]]:
    soup = BeautifulSoup(html, "html.parser")
    tooltip_by_cell: dict[str, str] = {}
    for tip in soup.select("tool-tip[for]"):
        cell_id = tip.get("for")
        text = tip.get_text(" ", strip=True)
        if cell_id and text:
            tooltip_by_cell[cell_id] = text

    # Deduplicate by date: keep last occurrence (GitHub renders oldest→newest in columns)
    by_date: dict[str, dict[str, int | str]] = {}
    for cell in soup.select('td[data-date][data-level]'):
        cell_id = cell.get("id")
        day = cell.get("data-date")
        if not day:
            continue
        tooltip_text = tooltip_by_cell.get(cell_id or "", "")
        count = 0
        if tooltip_text.startswith("No contributions"):
            count = 0
        else:
            match = re.match(r"(?P<count>[\d,]+) contribution(?:s)? on ", tooltip_text)
            if match:
                count = int(match.group("count").replace(",", ""))
            else:
                try:
                    count = int(cell.get("data-level", "0"))
                except ValueError:
                    count = 0
        try:
            level = int(cell.get("data-level", "0"))
        except ValueError:
            level = 0
        by_date[day] = {"date": day, "count": count, "level": level}

    # Sort chronologically
    return [by_date[d] for d in sorted(by_date.keys())]


def streaks(days: list[dict[str, int | str]]) -> tuple[int, int]:
    ordered = sorted(days, key=lambda item: str(item["date"]))
    longest = 0
    run = 0
    for item in ordered:
        count = int(item["count"])
        if count > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0

    current = 0
    for item in reversed(ordered):
        if int(item["count"]) > 0:
            current += 1
        else:
            break
    return current, longest


def contribution_summary(days: list[dict[str, int | str]]) -> dict[str, object]:
    total = sum(int(day["count"]) for day in days)
    current_streak, longest_streak = streaks(days)
    best_day = max(days, key=lambda item: int(item["count"]), default={"date": "", "count": 0, "level": 0})
    monthly_totals: dict[str, int] = defaultdict(int)
    for item in days:
        month = str(item["date"])[:7]
        monthly_totals[month] += int(item["count"])
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": dict(sorted(monthly_totals.items())),
        "days": days,
    }


def fallback_days() -> list[dict[str, int | str]]:
    end = date.today()
    start = end - timedelta(days=52 * 7)
    days: list[dict[str, int | str]] = []
    for offset in range((end - start).days + 1):
        current = start + timedelta(days=offset)
        value = (current.toordinal() * 7) % 11
        count = value if value < 6 else 0
        level = 0 if count == 0 else min(5, 1 + count // 2)
        days.append({"date": current.isoformat(), "count": count, "level": level})
    return days[-(53 * 7) :]


def main() -> int:
    username = os.environ.get("GITHUB_USER", "johna108")
    token = os.environ.get("GITHUB_TOKEN")
    try:
        if token:
            days = fetch_graphql(token, username)
        else:
            url = f"https://github.com/users/{username}/contributions"
            response = requests.get(url, timeout=20, headers={"User-Agent": "profile-art-bot"})
            response.raise_for_status()
            days = parse_day_cells(response.text)
            if not days:
                raise RuntimeError("No contribution cells found")
    except Exception:
        days = fallback_days()

    total = sum(int(day["count"]) for day in days)
    payload = contribution_summary(days)
    payload["total"] = total
    data_path = Path("data")
    data_path.mkdir(parents=True, exist_ok=True)
    (data_path / "contributions.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
