from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


RAMP = " .`:-=+*cs#%@"
FONT_SIZE = 10
LEFT_PAD = 10
TOP_PAD = 18
LINE_HEIGHT = 12
PORTRAIT_WIDTH = 100


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


def image_to_ascii(image: Image.Image, columns: int = PORTRAIT_WIDTH) -> list[str]:
    width, height = image.size
    aspect = height / max(width, 1)
    font = load_font()
    char_width = measure_char_width(font)
    rows = max(1, round(columns * aspect * (char_width / LINE_HEIGHT)))
    resized = image.resize((columns, rows))
    lines: list[str] = []
    ramp_max = len(RAMP) - 1
    for y in range(rows):
        chars = []
        for x in range(columns):
            shade = resized.getpixel((x, y))
            index = round((shade / 255) * ramp_max)
            chars.append(RAMP[index])
        lines.append("".join(chars).rstrip())
    return lines


def build_svg(lines: list[str], source_size: tuple[int, int]) -> str:
    source_width, source_height = source_size
    height = TOP_PAD * 2 + len(lines) * LINE_HEIGHT
    width = round(height * (source_width / max(source_height, 1)))
    char_width = (width - LEFT_PAD * 2) / PORTRAIT_WIDTH
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}" role="img" aria-label="ASCII portrait">',
        '<rect width="100%" height="100%" rx="18" fill="#0b0f14"/>',
        '<style><![CDATA[text { font-family: Consolas, "Courier New", monospace; font-size: 10px; fill: #c7d0db; white-space: pre; } .cursor { fill: #d7dee6; } ]]></style>',
    ]
    for index, line in enumerate(lines):
        y = TOP_PAD + index * LINE_HEIGHT
        clip_id = f"clip{index}"
        delay = index * 0.035
        text_width = max(1.0, PORTRAIT_WIDTH * char_width)
        parts.append(
            f'<clipPath id="{clip_id}"><rect x="{LEFT_PAD}" y="{y - 9}" width="0" height="14">'
            f'<animate attributeName="width" from="0" to="{text_width:.2f}" dur="0.9s" begin="{delay:.2f}s" fill="freeze" />'
            f"</rect></clipPath>"
        )
        parts.append(f'<g clip-path="url(#{clip_id})">')
        parts.append(f'<text x="{LEFT_PAD}" y="{y}" xml:space="preserve">{line or " "}</text>')
        parts.append("</g>")
        parts.append(
            f'<rect class="cursor" x="{LEFT_PAD}" y="{y - 9}" width="5" height="12" opacity="0">'
            f'<animate attributeName="x" from="{LEFT_PAD}" to="{LEFT_PAD + text_width:.2f}" dur="0.9s" begin="{delay:.2f}s" fill="freeze" />'
            f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;0.7;1" dur="0.9s" begin="{delay:.2f}s" fill="freeze" />'
            f"</rect>"
        )
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> int:
    image_path = Path("source-prepped.png")
    image = source_image(image_path)
    lines = image_to_ascii(image)
    Path("avi-ascii.svg").write_text(build_svg(lines, image.size), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
