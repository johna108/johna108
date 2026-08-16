from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path


PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
GRID_X = 64
GRID_Y = 48


def load_data() -> dict[str, object]:
    data_file = Path("data/contributions.json")
    if data_file.exists():
        return json.loads(data_file.read_text(encoding="utf-8"))
    return {"days": [], "total": 0, "current_streak": 0, "longest_streak": 0, "best_day": {"date": "", "count": 0, "level": 0}}


def week_grid() -> list[list[str]]:
    today = date.today()
    start = today - timedelta(days=370)
    columns: list[list[str]] = [[] for _ in range(53)]
    cursor = start
    for index in range(371):
        week = index // 7
        if week < 53:
            columns[week].append(cursor.isoformat())
        cursor += timedelta(days=1)
    return columns


def rect_for(index_x: int, index_y: int, level: int, count: int, day: str) -> str:
    x = GRID_X + index_x * 14
    y = GRID_Y + index_y * 14
    fill = PALETTE[min(level, 5)]
    delay = (index_x * 0.03) + (index_y * 0.015)
    return (
        f'<rect x="{x}" y="{y}" width="11" height="11" rx="3" fill="{fill}" opacity="0">'
        f'<title>{day}: {count} contributions</title>'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.35s" begin="{delay:.2f}s" fill="freeze" />'
        f"</rect>"
    )


def build_svg(data: dict[str, object]) -> str:
    days = {str(day["date"]): day for day in data.get("days", [])}
    columns = week_grid()
    total = int(data.get("total", 0))
    current_streak = int(data.get("current_streak", 0))
    longest_streak = int(data.get("longest_streak", 0))
    best_day = data.get("best_day", {"date": "", "count": 0})
    best_count = int(best_day.get("count", 0)) if isinstance(best_day, dict) else 0
    best_date = str(best_day.get("date", "")) if isinstance(best_day, dict) else ""
    width = 860
    height = 188
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Contribution heatmap">',
        '<rect width="100%" height="100%" rx="18" fill="#0b0f14"/>',
        '<rect x="1" y="1" width="858" height="186" rx="17" fill="none" stroke="#1f2a35" stroke-width="2"/>',
        '<style><![CDATA[text { font-family: Consolas, "Courier New", monospace; fill: #d8e1ea; } .muted { fill: #8aa0b5; }]]></style>',
        '<text x="18" y="28" font-size="14">Last 53 weeks</text>',
        f'<text x="18" y="168" font-size="12" class="muted">{total:,} contributions in the last year</text>',
        f'<text x="250" y="168" font-size="12" class="muted">Current streak: {current_streak}</text>',
        f'<text x="408" y="168" font-size="12" class="muted">Longest streak: {longest_streak}</text>',
        f'<text x="566" y="168" font-size="12" class="muted">Peak level: {best_date} ({best_count})</text>',
    ]
    labels = ["Mon", "Wed", "Fri"]
    for idx, label in enumerate(labels):
        parts.append(f'<text x="12" y="{64 + idx * 28}" font-size="10" class="muted">{label}</text>')

    for week_index, column in enumerate(columns):
        for day_index, day_str in enumerate(column):
            day = days.get(day_str, {"count": 0, "level": 0})
            count = int(day.get("count", 0)) if isinstance(day, dict) else 0
            level = int(day.get("level", 0)) if isinstance(day, dict) else 0
            parts.append(rect_for(week_index, day_index, level, count, day_str))

    legend_x = 620
    parts.append(f'<text x="{legend_x}" y="28" font-size="12" class="muted">Less</text>')
    for index, fill in enumerate(PALETTE):
        parts.append(f'<rect x="{legend_x + 38 + index * 18}" y="18" width="11" height="11" rx="3" fill="{fill}"/>')
    parts.append(f'<text x="{legend_x + 138}" y="28" font-size="12" class="muted">More</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> int:
    data = load_data()
    Path("contrib-heatmap.svg").write_text(build_svg(data), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
