"""
Shared visual language for every generated SVG in this repository.

Single source of truth for color, typography, and spacing so that the
hero, project cards, section headers, stats, and calendar render as one
system instead of independently-styled widgets.

The palette is viridis: the colormap of the attention heatmaps produced by
the from-scratch transformer in AI-Engineering-Assignment-01. It is
perceptually uniform, so a brighter cell always means a larger value, and
it stays legible for the common forms of color blindness.
"""

from __future__ import annotations

import base64
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FONT_PATH = REPO_ROOT / "assets" / "fonts" / "JetBrainsMono-Subset.woff2"

# ---- Palette -----------------------------------------------------------
BG = "#0d1117"
BG_ALT = "#111820"
FG = "#e6edf3"
FG_DIM = "#8b949e"
FG_FAINT = "#4d5560"
BORDER = "#21262d"
CELL_EMPTY = "#161b22"

# Ten anchor stops of matplotlib's viridis, t = 0.0 .. 1.0.
_VIRIDIS = [
    (0x44, 0x01, 0x54),
    (0x48, 0x28, 0x78),
    (0x3E, 0x49, 0x89),
    (0x31, 0x68, 0x8E),
    (0x26, 0x82, 0x8E),
    (0x1F, 0x9E, 0x89),
    (0x35, 0xB7, 0x79),
    (0x6D, 0xCD, 0x59),
    (0xB4, 0xDE, 0x2C),
    (0xFD, 0xE7, 0x25),
]


def viridis(t: float) -> str:
    """Hex color for t in [0, 1], linearly interpolated between anchors."""
    t = min(1.0, max(0.0, t))
    pos = t * (len(_VIRIDIS) - 1)
    i = min(int(pos), len(_VIRIDIS) - 2)
    f = pos - i
    a, b = _VIRIDIS[i], _VIRIDIS[i + 1]
    r, g, bl = (round(a[k] + (b[k] - a[k]) * f) for k in range(3))
    return f"#{r:02x}{g:02x}{bl:02x}"


# Text-safe accents: dark viridis stops are unreadable on BG, so text only
# ever uses t >= 0.45.
ACCENT = viridis(0.62)       # green, the default accent
ACCENT_HI = viridis(1.0)     # yellow, for the single most important number
ACCENT_DIM = viridis(0.30)

FONT_FAMILY = "JetBrains Mono Subset"
FONT_SIZE_HEADING = 15
FONT_SIZE_BODY = 13
FONT_SIZE_LABEL = 11
LETTER_SPACING = "0.14em"

CONTENT_WIDTH = 838          # GitHub's README column at desktop width
CARD_WIDTH = 480
CORNER_RADIUS = 8


def font_face_css() -> str:
    """Return an @font-face block with the subset font embedded as a data URI.

    Embedding avoids any dependency on an external font host. GitHub serves
    README SVGs through <img>, which blocks external requests but permits
    data-URI fonts inside <style>. The subset covers printable ASCII only,
    so generated text must stay ASCII.
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
        font-family: '{FONT_FAMILY}', ui-monospace, monospace;
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
    @media (prefers-reduced-motion: reduce) {{
        * {{ animation: none !important; }}
    }}
    """


def svg_open(width: int, height: int, title: str = "") -> str:
    head = (
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img">'
    )
    if title:
        head += f"<title>{escape(title)}</title>"
    return head


def card_background(width: int, height: int, radius: int = CORNER_RADIUS) -> str:
    return (
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" '
        f'rx="{radius}" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>'
    )


def escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(text: str, max_chars: int) -> list[str]:
    """Greedy word wrap for monospace text."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines
