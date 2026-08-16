from __future__ import annotations

import os
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape


LINES = [
    ("John.AI:", "Hi! I'm glad you found me because I was getting bored... anyway here is my info card"),
    ("Name", "Jakkula John Samuel Levith"),
    ("Focus", "AI/ML + full-stack systems"),
    ("Contact", "Hyderabad | jhonsamliv@gmail.com | +91 7396657238"),
    ("Education", "Malla Reddy University, B.Tech AIML, CGPA 8.1"),
    ("Experience", "Student Tribe intern; data annotation + quality"),
    ("Projects", "Document Extracter · Planify AI · Startup-Ops"),
    ("Wins", "2x national hackathon winner; 1st prize at IIT Jammu + MRU"),
    ("Skills", "LLMs, RAG, Python, PyTorch, Docker, FastAPI, GCP"),
]


def build_svg(static: bool = False) -> str:
    width = 490
    title = "johna108@github:~$ neofetch"
    content_top = 58
    line_height = 14
    row_gap = 8
    value_x = 132
    max_value_chars = 44

    def wrap_value(value: str) -> list[str]:
        paragraphs: list[str] = []
        for paragraph in value.splitlines() or [value]:
            if not paragraph.strip():
                paragraphs.append("")
                continue
            paragraphs.extend(
                textwrap.wrap(
                    paragraph,
                    width=max_value_chars,
                    break_long_words=False,
                    break_on_hyphens=False,
                )
                or [paragraph]
            )
        return paragraphs or [value]

    rows = [(label, wrap_value(value)) for label, value in LINES]
    row_heights = [max(1, len(lines)) * line_height + row_gap for _, lines in rows]
    height = content_top + sum(row_heights) + 18

    def render_multiline_text(x: int, y: int, classes: str, lines: list[str]) -> str:
        tspans = []
        for index, line in enumerate(lines):
            dy = 0 if index == 0 else line_height
            tspans.append(
                f'<tspan x="{x}" dy="{dy}">{escape(line)}</tspan>'
            )
        return f'<text class="{classes}" x="{x}" y="{y}">' + "".join(tspans) + "</text>"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Profile info card">',
        '<rect width="100%" height="100%" rx="18" fill="#0b0f14"/>',
        f'<rect x="1" y="1" width="488" height="{height - 2}" rx="17" fill="none" stroke="#1f2a35" stroke-width="2"/>',
        '<rect x="18" y="16" width="454" height="22" rx="11" fill="#10161d" stroke="#1f2a35"/>',
        '<circle cx="34" cy="27" r="4" fill="#ff5f57"/>',
        '<circle cx="48" cy="27" r="4" fill="#febc2e"/>',
        '<circle cx="62" cy="27" r="4" fill="#28c840"/>',
        f'<text x="84" y="31" fill="#8aa0b5" font-family="Consolas, Courier New, monospace" font-size="11">{escape(title)}</text>',
        '<style><![CDATA[text { font-family: Consolas, "Courier New", monospace; } .label { fill: #7dd3fc; font-size: 11px; } .value { fill: #d8e1ea; font-size: 11px; }]]></style>',
    ]
    cursor = content_top
    for index, (label, value_lines) in enumerate(rows):
        y = cursor
        delay = 0 if static else index * 0.055
        row_height = row_heights[index]
        parts.append(
            f'<g opacity="0" transform="translate(0,8)">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.22s" begin="{delay:.2f}s" fill="freeze" />'
            f'<animateTransform attributeName="transform" type="translate" from="0 8" to="0 0" dur="0.22s" begin="{delay:.2f}s" fill="freeze" />'
            f'<text class="label" x="28" y="{y}">{escape(label)}</text>'
            f'{render_multiline_text(value_x, y, "value", value_lines)}'
            f'</g>'
        )
        cursor += row_height
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> int:
    static = os.environ.get("STATIC") == "1"
    Path("info-card.svg").write_text(build_svg(static=static), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
