from __future__ import annotations

import io
import sys
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps


def remove_background(image: Image.Image) -> Image.Image:
    try:
        from rembg import remove as rembg_remove  # type: ignore
    except Exception:
        return image.convert("RGBA")

    buffer = io.BytesIO()
    image.convert("RGBA").save(buffer, format="PNG")
    output = rembg_remove(buffer.getvalue())
    return Image.open(io.BytesIO(output)).convert("RGBA")


def boost_contrast(image: Image.Image) -> Image.Image:
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except Exception:
        return ImageEnhance.Contrast(image).enhance(1.35)

    rgb = np.array(image.convert("RGB"))
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_channel = clahe.apply(l_channel)
    merged = cv2.merge((l_channel, a_channel, b_channel))
    return Image.fromarray(cv2.cvtColor(merged, cv2.COLOR_LAB2RGB))


def prepare(input_path: Path, output_path: Path) -> None:
    image = Image.open(input_path)
    image = remove_background(image)
    image = boost_contrast(image)

    if image.mode != "RGBA":
        image = image.convert("RGBA")

    white = Image.new("RGBA", image.size, (255, 255, 255, 255))
    flattened = Image.alpha_composite(white, image)
    grayscale = ImageOps.grayscale(flattened)
    grayscale.save(output_path)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py source-photo.jpg [output.png]")
        return 1

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("source-prepped.png")
    prepare(input_path, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
