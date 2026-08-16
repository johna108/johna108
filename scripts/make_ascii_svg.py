from __future__ import annotations

import html
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


RAMP = " .`:-=+*cs#%@"
FONT_SIZE = 10
LEFT_PAD = 10
TOP_PAD = 18
LINE_HEIGHT = 12
PORTRAIT_WIDTH = 60
CHAR_DELAY = 0.00002
CHAR_STEP = 0.0020
CHAR_FADE = 0.010
LINE_GAP = 0.000
CROP_THRESHOLD = 245
CROP_MARGIN = 0.06


def load_font() -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
        "DejaVuSansMono.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, FONT_SIZE)
        except Exception:
            continue
    return ImageFont.load_default()


def measure_char_width(font: ImageFont.FreeTypeFont | ImageFont.ImageFont) -> float:
    bbox = font.getbbox("M")
    return float(bbox[2] - bbox[0]) if bbox else 6.0


def source_image(path: Path) -> Image.Image:
    if path.exists():
        return Image.open(path).convert("L")

    width, height = 360, 360
    image = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(image)
    draw.ellipse((70, 55, 290, 275), fill=185)
    draw.ellipse((120, 120, 150, 150), fill=60)
    draw.ellipse((210, 120, 240, 150), fill=60)
    draw.arc((120, 165, 240, 250), start=15, end=165, fill=70, width=8)
    draw.rectangle((130, 270, 230, 340), fill=210)
    return image


def crop_portrait(image: Image.Image) -> Image.Image:
    mask = image.point(lambda pixel: 255 if pixel < CROP_THRESHOLD else 0)
    bbox = mask.getbbox()
    if not bbox:
        return image

    left, top, right, bottom = bbox
    width, height = image.size
    pad_x = max(4, round((right - left) * CROP_MARGIN))
    pad_y = max(4, round((bottom - top) * CROP_MARGIN))

    return image.crop(
        (
            max(0, left - pad_x),
            max(0, top - pad_y),
            min(width, right + pad_x),
            min(height, bottom + pad_y),
        )
    )


def image_to_ascii(image: Image.Image, columns: int = PORTRAIT_WIDTH) -> list[str]:
    image = crop_portrait(image)
    width, height = image.size
    aspect = height / max(width, 1)
    font = load_font()
    char_width = measure_char_width(font)
    rows = max(1, round(columns * aspect * (char_width / LINE_HEIGHT)))
    resized = image.resize((columns, rows), Image.Resampling.LANCZOS)
    lines: list[str] = []
    ramp_max = len(RAMP) - 1
    for y in range(rows):
        chars = []
        for x in range(columns):
            shade = resized.getpixel((x, y))
            index = round((shade / 255) * ramp_max)
            chars.append(RAMP[index])
        lines.append("".join(chars))
    return lines


def build_svg(lines: list[str], font: ImageFont.FreeTypeFont | ImageFont.ImageFont, columns: int) -> str:
    char_width = measure_char_width(font)
    width = round(LEFT_PAD * 2 + columns * char_width)
    height = TOP_PAD * 2 + len(lines) * LINE_HEIGHT
    line_duration = columns * CHAR_STEP + LINE_GAP
    cursor_width = max(4.0, round(char_width * 0.75, 2))
    cursor_height = max(8.0, round(LINE_HEIGHT * 0.72, 2))
    cursor_y_offset = round((LINE_HEIGHT - cursor_height) / 2, 2)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}" role="img" aria-label="ASCII portrait">',
        '<rect width="100%" height="100%" rx="18" fill="#0b0f14"/>',
        '<style><![CDATA[text { font-family: Consolas, "Courier New", monospace; font-size: 10px; fill: #c7d0db; white-space: pre; } .cursor { fill: #d7dee6; }]]></style>',
    ]
    for index, line in enumerate(lines):
        y = TOP_PAD + index * LINE_HEIGHT
        line_delay = index * line_duration
        parts.append(f'<text xml:space="preserve" font-size="10px" y="{y}">')
        for column, character in enumerate(line):
            char_delay = line_delay + column * CHAR_STEP
            x = LEFT_PAD + column * char_width
            escaped = html.escape(character or " ")
            parts.append(
                f'<tspan x="{x:.2f}" y="{y}" opacity="0">{escaped}'
                f'<animate attributeName="opacity" from="0" to="1" dur="{CHAR_FADE:.3f}s" begin="{char_delay:.3f}s" fill="freeze" />'
                f'</tspan>'
            )
        parts.append("</text>")
        cursor_positions = [LEFT_PAD + column * char_width for column in range(min(columns, len(line)))]
        if not cursor_positions:
            cursor_positions = [LEFT_PAD]
        cursor_values = ";".join(f"{position:.2f}" for position in cursor_positions)
        cursor_key_times = ";".join(
            f"{(index / max(1, len(cursor_positions) - 1)):.4f}"
            for index in range(len(cursor_positions))
        )
        cursor_x = cursor_positions[0]
        cursor_y = y - LINE_HEIGHT + cursor_y_offset
        parts.append(
            f'<rect class="cursor" x="{cursor_x:.2f}" y="{cursor_y:.2f}" width="{cursor_width:.2f}" height="{cursor_height:.2f}" opacity="0">'
            f'<animate attributeName="x" values="{cursor_values}" keyTimes="{cursor_key_times}" dur="{line_duration:.3f}s" begin="{line_delay:.3f}s" calcMode="discrete" fill="freeze" />'
            f'<animate attributeName="opacity" values="0;1;1;0" dur="0.18s" begin="{line_delay:.3f}s" repeatCount="indefinite" />'
            f'<animate attributeName="opacity" values="1;0" dur="0.01s" begin="{line_delay + line_duration:.3f}s" fill="freeze" />'
            f'</rect>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> int:
    image_path = Path("source-prepped.png")
    image = source_image(image_path)
    font = load_font()
    lines = image_to_ascii(image)
    Path("avi-ascii.svg").write_text(build_svg(lines, font, PORTRAIT_WIDTH), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
