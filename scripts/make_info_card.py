from __future__ import annotations

import os
from pathlib import Path


LINES = [
    ("Now", "Building a README that looks like a terminal"),
    ("Prev", "Turning static profile content into SVG art"),
    ("Stack", "Python · SVG · GitHub Actions · public HTML"),
    ("Highlights", "ASCII portrait · neofetch card · live heatmap"),
]


def build_svg(static: bool = False) -> str:
    width = 490
    height = 250
    title = "johna108@github:~$ neofetch"
    content_top = 58
    row_gap = 34
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Profile info card">',
        '<rect width="100%" height="100%" rx="18" fill="#0b0f14"/>',
        '<rect x="1" y="1" width="488" height="248" rx="17" fill="none" stroke="#1f2a35" stroke-width="2"/>',
        '<rect x="18" y="16" width="454" height="22" rx="11" fill="#10161d" stroke="#1f2a35"/>',
        '<circle cx="34" cy="27" r="4" fill="#ff5f57"/>',
        '<circle cx="48" cy="27" r="4" fill="#febc2e"/>',
        '<circle cx="62" cy="27" r="4" fill="#28c840"/>',
        f'<text x="84" y="31" fill="#8aa0b5" font-family="Consolas, Courier New, monospace" font-size="11">{title}</text>',
        '<style><![CDATA[text { font-family: Consolas, "Courier New", monospace; } .label { fill: #7dd3fc; font-size: 13px; } .value { fill: #d8e1ea; font-size: 13px; }]]></style>',
    ]
    for index, (label, value) in enumerate(LINES):
        y = content_top + index * row_gap
        delay = 0 if static else index * 0.14
        parts.append(
            f'<g opacity="0" transform="translate(0,8)">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.45s" begin="{delay:.2f}s" fill="freeze" />'
            f'<animateTransform attributeName="transform" type="translate" from="0 8" to="0 0" dur="0.45s" begin="{delay:.2f}s" fill="freeze" />'
            f'<text class="label" x="28" y="{y}">{label}</text>'
            f'<text class="value" x="132" y="{y}">{value}</text>'
            f'</g>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> int:
    static = os.environ.get("STATIC") == "1"
    Path("info-card.svg").write_text(build_svg(static=static), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
