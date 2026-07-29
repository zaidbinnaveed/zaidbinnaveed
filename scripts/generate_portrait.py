"""
Builds assets/portrait.svg — a typing-animation ASCII portrait.

Pipeline:
  1. Load assets/portrait_source.(jpg|png)
  2. Remove background (rembg / u2net) so the ASCII render isolates
     the subject instead of the room behind them.
  3. CLAHE contrast + bilateral filter to keep edges clean before
     they get crushed into a small character set.
  4. Darkening curve so midtones separate — a flat portrait turns
     into mush at 90 columns without this.
  5. Map luminance to a density ramp of ASCII characters, 90 columns
     wide, aspect-corrected for monospace character cells.
  6. Emit one <text> row per source row, each with a CSS animation
     delay so the portrait appears to type itself in, top to bottom.

This script requires a real source photo to run. Without one it
exits with instructions rather than emitting a placeholder, since a
placeholder ASCII portrait would be actively misleading in a README
that claims to render a real photo.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

import theme

SOURCE_CANDIDATES = ["portrait_source.jpg", "portrait_source.jpeg", "portrait_source.png"]
COLUMNS = 90
CHAR_ASPECT = 0.55  # monospace glyphs are taller than wide; corrects row count
# Density ramp, darkest -> lightest. Kept short on purpose: a long ramp
# reads as noise once a face is reduced to a JetBrains Mono grid.
RAMP = " .:-=+*#%@"


def _find_source() -> Path | None:
    assets = theme.REPO_ROOT / "assets"
    for name in SOURCE_CANDIDATES:
        candidate = assets / name
        if candidate.exists():
            return candidate
    return None


def _remove_background(img: Image.Image) -> Image.Image:
    try:
        from rembg import remove
    except ImportError:
        print("rembg not installed; proceeding without background removal", file=sys.stderr)
        return img.convert("RGB")
    result = remove(img)
    # Composite onto the theme background so removed pixels become
    # the darkest ramp character instead of transparent noise.
    bg = Image.new("RGBA", result.size, theme.BG)
    bg.alpha_composite(result.convert("RGBA"))
    return bg.convert("RGB")


def _enhance(img: Image.Image) -> np.ndarray:
    gray = np.array(img.convert("L"), dtype=np.uint8)

    try:
        import cv2

        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        gray = cv2.bilateralFilter(gray, d=5, sigmaColor=50, sigmaSpace=50)
    except ImportError:
        print("opencv-python-headless not installed; skipping CLAHE/bilateral pass", file=sys.stderr)

    # Darkening curve: gamma > 1 pulls midtones down so a face doesn't
    # collapse into a flat mid-density gray block.
    normalized = gray.astype(np.float32) / 255.0
    curved = np.power(normalized, 1.35)
    return (curved * 255).astype(np.uint8)


def _to_ascii_grid(gray: np.ndarray, columns: int = COLUMNS) -> list[str]:
    height, width = gray.shape
    rows = max(1, int((height / width) * columns * CHAR_ASPECT))

    img = Image.fromarray(gray).resize((columns, rows), Image.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0

    ramp_len = len(RAMP) - 1
    indices = (arr * ramp_len).astype(int)
    lines = ["".join(RAMP[i] for i in row) for row in indices]
    return lines


def _escape(ch: str) -> str:
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(ch, ch)


def render_portrait_svg(lines: list[str]) -> str:
    char_w = 7.2
    line_h = 13
    pad = 20
    width = int(len(lines[0]) * char_w) + pad * 2 if lines else 400
    height = len(lines) * line_h + pad * 2

    parts = [theme.svg_open(width, height)]
    style = f"""
    <style>
      {theme.font_face_css()}
      {theme.base_style()}
      text {{
          font-family: '{theme.FONT_FAMILY}', monospace;
          font-size: 10px;
          white-space: pre;
      }}
      .row {{
          fill: {theme.ACCENT};
          opacity: 0;
          animation: reveal 0.4s ease-out forwards;
      }}
      @keyframes reveal {{
          from {{ opacity: 0; transform: translateY(-2px); }}
          to   {{ opacity: 1; transform: translateY(0); }}
      }}
    </style>
    """
    parts.append(style)
    parts.append(theme.card_background(width, height))

    for i, line in enumerate(lines):
        y = pad + (i + 1) * line_h
        delay = round(i * 0.025, 3)
        escaped = "".join(_escape(c) for c in line)
        parts.append(
            f'<text x="{pad}" y="{y}" class="row" style="animation-delay:{delay}s">{escaped}</text>'
        )

    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    source = _find_source()
    if source is None:
        print(
            "No source photo found. Add one of "
            f"{SOURCE_CANDIDATES} to assets/ and re-run.\n"
            "Recommended: a high-resolution, front-or-slight-angle portrait "
            "with even lighting — the CLAHE pass helps, but it isn't a fix "
            "for a backlit or low-res source.",
            file=sys.stderr,
        )
        sys.exit(1)

    img = Image.open(source)
    img = _remove_background(img)
    gray = _enhance(img)
    lines = _to_ascii_grid(gray, columns=COLUMNS)

    svg = render_portrait_svg(lines)
    out_path = theme.REPO_ROOT / "assets" / "portrait.svg"
    out_path.write_text(svg, encoding="utf-8")
    print(f"wrote {out_path} ({len(lines)} rows x {COLUMNS} cols)", file=sys.stderr)


if __name__ == "__main__":
    main()
