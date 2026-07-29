"""
Shared visual language for every generated SVG in this repository.

Single source of truth for color, typography, and spacing so that
portrait.svg, stats.svg, langs.svg, year.svg, and every section header
render as one consistent system instead of independently-styled widgets.
"""

from __future__ import annotations

import base64
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FONT_PATH = REPO_ROOT / "assets" / "fonts" / "JetBrainsMono-Subset.woff2"

# ---- Palette -----------------------------------------------------------
# Premium dark. One accent. No gradients, no badge colors.
BG = "#0d1117"
BG_ALT = "#111820"
FG = "#e6e6e6"
FG_DIM = "#8b949e"
FG_FAINT = "#4d5560"
ACCENT = "#5ec8d8"          # single cool accent, used sparingly
ACCENT_DIM = "#2f5a62"
BORDER = "#21262d"

FONT_FAMILY = "JetBrains Mono Subset"
FONT_SIZE_HEADING = 16
FONT_SIZE_BODY = 13
FONT_SIZE_LABEL = 11
LETTER_SPACING = "0.14em"

CARD_WIDTH = 480
CORNER_RADIUS = 6


def font_face_css() -> str:
    """Return an @font-face block with the subset font embedded as a data URI.

    Embedding avoids any dependency on an external font host, matching the
    "no external services" constraint. GitHub sanitizes served SVGs but
    permits data-URI fonts inside <style>, so this renders identically
    everywhere the SVG is displayed.
    """
    data = base64.b64encode(FONT_PATH.read_bytes()).decode("ascii")
    return f"""
    @font-face {{
        font-family: '{FONT_FAMILY}';
        src: url(data:font/woff2;base64,{data}) format('woff2');
        font-weight: 400;
        font-style: normal;
    }}
    """


def base_style() -> str:
    """Shared <style> body every SVG includes, on top of font_face_css()."""
    return f"""
    text {{
        font-family: '{FONT_FAMILY}', monospace;
        fill: {FG};
    }}
    .dim {{ fill: {FG_DIM}; }}
    .faint {{ fill: {FG_FAINT}; }}
    .accent {{ fill: {ACCENT}; }}
    .label {{
        font-size: {FONT_SIZE_LABEL}px;
        letter-spacing: {LETTER_SPACING};
        text-transform: uppercase;
    }}
    """


def svg_open(width: int, height: int) -> str:
    return (
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img">'
    )


def card_background(width: int, height: int, radius: int = CORNER_RADIUS) -> str:
    return (
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" '
        f'rx="{radius}" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>'
    )
