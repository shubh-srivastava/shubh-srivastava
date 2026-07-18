from __future__ import annotations

import argparse
import html
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
RAMP = " .`:-=+*cs#%@"


def cover_crop(image: Image.Image, target_ratio: float) -> Image.Image:
    width, height = image.size
    ratio = width / height
    if ratio > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        return image.crop((left, 0, left + new_width, height))

    new_height = int(width / target_ratio)
    top = max(0, (height - new_height) // 8)
    return image.crop((0, top, width, top + new_height))


def image_to_ascii(path: Path, cols: int, rows: int) -> list[str]:
    img = Image.open(path).convert("RGB")
    img = ImageOps.exif_transpose(img)
    img = cover_crop(img, target_ratio=(cols / rows) * 0.48)
    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img, cutoff=2)
    img = ImageEnhance.Contrast(img).enhance(1.9)
    img = ImageEnhance.Sharpness(img).enhance(1.4)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=150, threshold=3))
    img = img.resize((cols, rows), Image.Resampling.LANCZOS)

    pixels = list(img.getdata())
    lines: list[str] = []
    for row in range(rows):
        chars = []
        for col in range(cols):
            value = pixels[row * cols + col]
            index = int((255 - value) / 255 * (len(RAMP) - 1))
            chars.append(RAMP[index])
        lines.append("".join(chars).rstrip())
    return lines


def make_svg(lines: list[str], output: Path, name: str) -> None:
    char_w = 7.4
    line_h = 10.6
    pad_x = 18
    pad_y = 22
    width = 620
    height = int(pad_y * 2 + len(lines) * line_h)
    text_width = max(len(line) for line in lines) * char_w

    row_parts = []
    clip_parts = []
    cursor_parts = []
    for idx, line in enumerate(lines):
        y = pad_y + idx * line_h
        delay = idx * 0.028
        clip_id = f"clip-row-{idx}"
        clip_parts.append(
            f'<clipPath id="{clip_id}"><rect x="{pad_x}" y="{y - 8}" width="0" height="{line_h + 2}">'
            f'<animate attributeName="width" from="0" to="{text_width:.1f}" dur="0.55s" begin="{delay:.3f}s" fill="freeze" />'
            "</rect></clipPath>"
        )
        row_parts.append(
            f'<text clip-path="url(#{clip_id})" x="{pad_x}" y="{y}" fill="#c9d1d9">'
            f"{html.escape(line)}</text>"
        )
        cursor_parts.append(
            f'<rect x="{pad_x}" y="{y - 8}" width="6" height="9" fill="#39d353" opacity="0.85">'
            f'<animate attributeName="x" from="{pad_x}" to="{pad_x + text_width:.1f}" dur="0.55s" begin="{delay:.3f}s" fill="freeze" />'
            f'<animate attributeName="opacity" values="0;0.9;0.9;0" dur="0.65s" begin="{delay:.3f}s" fill="freeze" />'
            "</rect>"
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(name)} ASCII portrait">
  <title>{html.escape(name)} ASCII portrait</title>
  <defs>
    <filter id="softGlow">
      <feDropShadow dx="0" dy="0" stdDeviation="1.2" flood-color="#39d353" flood-opacity="0.35" />
    </filter>
    {''.join(clip_parts)}
  </defs>
  <rect width="100%" height="100%" rx="12" fill="#0d1117" />
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="11" fill="none" stroke="#30363d" />
  <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="10" filter="url(#softGlow)">
    {''.join(row_parts)}
    {''.join(cursor_parts)}
  </g>
</svg>
"""
    output.write_text(svg, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an animated ASCII portrait SVG.")
    parser.add_argument("image", nargs="?", default="IMG_3011.JPG")
    parser.add_argument("--output", default="shubh-ascii.svg")
    parser.add_argument("--name", default="Shubh Srivastava")
    parser.add_argument("--cols", type=int, default=76)
    parser.add_argument("--rows", type=int, default=58)
    args = parser.parse_args()

    image_path = (ROOT / args.image).resolve()
    output_path = (ROOT / args.output).resolve()
    lines = image_to_ascii(image_path, args.cols, args.rows)
    make_svg(lines, output_path, args.name)


if __name__ == "__main__":
    main()
