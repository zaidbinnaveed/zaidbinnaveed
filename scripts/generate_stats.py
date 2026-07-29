"""
Generates every data-driven SVG in assets/:

  stats.svg   — commit / PR / review / issue totals + star count
  langs.svg   — top languages by byte-weight, horizontal bars
  year.svg    — GitHub-style contribution calendar for the current year
  streak.svg  — current streak + longest streak this year

No github-readme-stats, no snake, no streak-stats service. Every pixel
comes from data fetched in github_api.py and drawn here.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from github_api import UserStats, fetch_user_stats
import theme

ASSETS = theme.REPO_ROOT / "assets"


# -------------------------------------------------------------------------
# stats.svg
# -------------------------------------------------------------------------
def render_stats(stats: UserStats) -> str:
    w, h = theme.CARD_WIDTH, 150
    total_stars = sum(r.stars for r in stats.repos)

    rows = [
        ("Commits", stats.commits),
        ("Pull Requests", stats.pull_requests),
        ("Code Reviews", stats.reviews),
        ("Issues", stats.issues),
        ("Stars Earned", total_stars),
    ]

    parts = [theme.svg_open(w, h), f"<style>{theme.font_face_css()}{theme.base_style()}</style>"]
    parts.append(theme.card_background(w, h))
    parts.append(
        f'<text x="24" y="32" class="label accent">github statistics · {date.today().year}</text>'
    )

    col_split = w // 2
    for i, (label, value) in enumerate(rows):
        col = i // 3
        row = i % 3
        x = 24 + col * (col_split - 12)
        y = 62 + row * 28
        parts.append(f'<text x="{x}" y="{y}" class="dim" font-size="{theme.FONT_SIZE_BODY}">{label}</text>')
        parts.append(
            f'<text x="{x + col_split - 48}" y="{y}" class="accent" '
            f'font-size="{theme.FONT_SIZE_BODY}" text-anchor="end">{value:,}</text>'
        )

    parts.append("</svg>")
    return "".join(parts)


# -------------------------------------------------------------------------
# langs.svg
# -------------------------------------------------------------------------
def render_langs(stats: UserStats, top_n: int = 6) -> str:
    totals: dict[str, int] = {}
    colors: dict[str, str] = {}
    for repo in stats.repos:
        if repo.is_archived:
            continue
        for lang, size in repo.languages.items():
            totals[lang] = totals.get(lang, 0) + size

    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    grand_total = sum(v for _, v in ranked) or 1

    w = theme.CARD_WIDTH
    h = 46 + 26 * len(ranked)
    parts = [theme.svg_open(w, h), f"<style>{theme.font_face_css()}{theme.base_style()}</style>"]
    parts.append(theme.card_background(w, h))
    parts.append(f'<text x="24" y="32" class="label accent">languages</text>')

    bar_max = w - 48 - 90
    for i, (lang, size) in enumerate(ranked):
        y = 54 + i * 26
        pct = size / grand_total
        bar_w = max(2, int(bar_max * pct))
        parts.append(f'<text x="24" y="{y + 5}" class="dim" font-size="{theme.FONT_SIZE_LABEL}">{lang}</text>')
        parts.append(
            f'<rect x="130" y="{y - 8}" width="{bar_max}" height="10" rx="3" '
            f'fill="{theme.BORDER}"/>'
        )
        parts.append(
            f'<rect x="130" y="{y - 8}" width="{bar_w}" height="10" rx="3" '
            f'fill="{theme.ACCENT}"/>'
        )
        parts.append(
            f'<text x="{w - 24}" y="{y + 5}" class="faint" font-size="{theme.FONT_SIZE_LABEL}" '
            f'text-anchor="end">{pct * 100:.1f}%</text>'
        )

    parts.append("</svg>")
    return "".join(parts)


# -------------------------------------------------------------------------
# year.svg — contribution calendar
# -------------------------------------------------------------------------
def render_year(stats: UserStats) -> str:
    cell = 10
    gap = 3
    days = stats.calendar_days
    if not days:
        weeks = []
    else:
        weeks = [days[i : i + 7] for i in range(0, len(days), 7)]

    w = 40 + len(weeks) * (cell + gap)
    h = 100
    parts = [theme.svg_open(w, h), f"<style>{theme.font_face_css()}{theme.base_style()}</style>"]
    parts.append(theme.card_background(w, h))
    parts.append(f'<text x="24" y="26" class="label accent">contributions · {date.today().year}</text>')

    max_count = max((c for _, c in days), default=1) or 1

    def shade(count: int) -> str:
        if count == 0:
            return theme.BORDER
        ratio = min(1.0, count / max_count)
        # Interpolate between ACCENT_DIM and ACCENT
        return theme.ACCENT if ratio > 0.66 else theme.ACCENT_DIM if ratio > 0.2 else "#2a3236"

    for wi, week in enumerate(weeks):
        for di, (iso_date, count) in enumerate(week):
            x = 24 + wi * (cell + gap)
            y = 40 + di * (cell + gap)
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" '
                f'fill="{shade(count)}"><title>{iso_date}: {count} contributions</title></rect>'
            )

    parts.append("</svg>")
    return "".join(parts)


# -------------------------------------------------------------------------
# streak.svg
# -------------------------------------------------------------------------
def render_streak(stats: UserStats) -> str:
    counts = [c for _, c in stats.calendar_days]

    def longest_streak(seq: list[int]) -> int:
        best = cur = 0
        for c in seq:
            cur = cur + 1 if c > 0 else 0
            best = max(best, cur)
        return best

    def current_streak(seq: list[int]) -> int:
        cur = 0
        for c in reversed(seq):
            if c == 0:
                break
            cur += 1
        return cur

    longest = longest_streak(counts)
    current = current_streak(counts)

    w, h = theme.CARD_WIDTH, 100
    parts = [theme.svg_open(w, h), f"<style>{theme.font_face_css()}{theme.base_style()}</style>"]
    parts.append(theme.card_background(w, h))
    parts.append(f'<text x="24" y="32" class="label accent">streak</text>')

    parts.append(f'<text x="24" y="66" class="accent" font-size="28">{current}</text>')
    parts.append(f'<text x="24" y="84" class="dim" font-size="{theme.FONT_SIZE_LABEL}">current (days)</text>')

    parts.append(f'<text x="{w // 2}" y="66" class="accent" font-size="28">{longest}</text>')
    parts.append(
        f'<text x="{w // 2}" y="84" class="dim" font-size="{theme.FONT_SIZE_LABEL}">longest this year</text>'
    )

    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", default="zaidbinnaveed")
    args = parser.parse_args()

    stats = fetch_user_stats(args.login)

    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "stats.svg").write_text(render_stats(stats), encoding="utf-8")
    (ASSETS / "langs.svg").write_text(render_langs(stats), encoding="utf-8")
    (ASSETS / "year.svg").write_text(render_year(stats), encoding="utf-8")
    (ASSETS / "streak.svg").write_text(render_streak(stats), encoding="utf-8")
    print("wrote stats.svg, langs.svg, year.svg, streak.svg", file=sys.stderr)


if __name__ == "__main__":
    main()
