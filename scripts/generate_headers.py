"""
Generates one SVG per README section heading.

Markdown headings render inconsistently across GitHub's light/dark
themes and clash with the rest of a self-generated profile, so every
section title in README.md is instead one of these SVGs. Each carries the
profile's motif, a short attention row in viridis, plus a section number.
Static content, but generated so a new section is one line of config.
"""

from __future__ import annotations

import theme

# (slug, title) in README order; the number shown is the position here.
SECTIONS = [
    ("now", "Now"),
    ("selected-work", "Selected work"),
    ("toolkit", "Toolkit"),
    ("principles", "Principles"),
    ("activity", "Activity"),
    ("contact", "Contact"),
]


def render_header(title: str, number: int, width: int = theme.CONTENT_WIDTH, height: int = 44) -> str:
    mid = height // 2
    parts = [theme.svg_open(width, height, title)]
    parts.append(f"<style>{theme.font_face_css()}{theme.base_style()}</style>")

    for s in range(5):
        parts.append(
            f'<rect x="{s * 11}" y="{mid - 5}" width="9" height="9" rx="2" '
            f'fill="{theme.viridis(0.15 + 0.85 * s / 4)}"/>'
        )
    text_x = 5 * 11 + 14
    parts.append(
        f'<text x="{text_x}" y="{mid + 5}" font-size="{theme.FONT_SIZE_HEADING}" '
        f'letter-spacing="{theme.LETTER_SPACING}">{theme.escape(title.upper())}</text>'
    )
    # monospace advance is 0.6em, plus letter-spacing of 0.14em per glyph
    text_w = len(title) * theme.FONT_SIZE_HEADING * 0.74
    num = f"{number:02d}"
    parts.append(
        f'<line x1="{text_x + text_w + 18:.0f}" y1="{mid}" x2="{width - 40}" y2="{mid}" '
        f'stroke="{theme.BORDER}" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{width}" y="{mid + 4}" class="faint" font-size="11" text-anchor="end">{num}</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    out_dir = theme.REPO_ROOT / "assets" / "headers"
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, (slug, title) in enumerate(SECTIONS, start=1):
        (out_dir / f"{slug}.svg").write_text(render_header(title, i), encoding="utf-8")
    print(f"wrote {len(SECTIONS)} section headers to {out_dir}")


if __name__ == "__main__":
    main()
