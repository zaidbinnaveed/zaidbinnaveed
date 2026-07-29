"""
Generates one SVG per README section heading.

Markdown headings render inconsistently across GitHub's light/dark
themes and clash with the rest of a self-generated profile, so every
section title in README.md is instead one of these SVGs. Static
content, but generated (not hand-drawn) so a new section is one
line of config, not a new asset built in an image editor.
"""

from __future__ import annotations

from pathlib import Path

import theme

HEADERS = [
    "introduction",
    "current-work",
    "featured-projects",
    "research",
    "github-statistics",
    "timeline",
    "contact",
]

TITLES = {
    "introduction": "Introduction",
    "current-work": "Current Work",
    "featured-projects": "Featured Projects",
    "research": "Research",
    "github-statistics": "GitHub Statistics",
    "timeline": "Timeline",
    "contact": "Contact",
}


def render_header(title: str, width: int = theme.CARD_WIDTH, height: int = 46) -> str:
    parts = [theme.svg_open(width, height)]
    parts.append(f"<style>{theme.font_face_css()}{theme.base_style()}</style>")

    # left accent tick + title, thin rule filling the remaining width
    parts.append(f'<rect x="0" y="16" width="3" height="14" fill="{theme.ACCENT}"/>')
    parts.append(
        f'<text x="16" y="{height // 2 + 5}" font-size="{theme.FONT_SIZE_HEADING}" '
        f'letter-spacing="{theme.LETTER_SPACING}">{title.upper()}</text>'
    )
    text_width = 16 + len(title) * 11 + 24
    parts.append(
        f'<line x1="{text_width}" y1="{height // 2}" x2="{width}" y2="{height // 2}" '
        f'stroke="{theme.BORDER}" stroke-width="1"/>'
    )
    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    out_dir = theme.REPO_ROOT / "assets" / "headers"
    out_dir.mkdir(parents=True, exist_ok=True)
    for slug in HEADERS:
        svg = render_header(TITLES[slug])
        (out_dir / f"{slug}.svg").write_text(svg, encoding="utf-8")
    print(f"wrote {len(HEADERS)} section headers to {out_dir}")


if __name__ == "__main__":
    main()
