"""
Generates every data-driven SVG in assets/:

  stats.svg   - contribution, commit, PR, review, issue and star totals
  langs.svg   - language mix by bytes, one stacked bar plus a legend
  year.svg    - contribution calendar for the current year, viridis scale

No github-readme-stats, no snake, no streak-stats service. Every pixel
comes from data fetched in github_api.py and drawn here.
"""

from __future__ import annotations

import argparse
import math
import sys
from datetime import date

from github_api import UserStats, fetch_user_stats
import theme

ASSETS = theme.REPO_ROOT / "assets"
HALF_W, HALF_H = 410, 196   # stats and langs sit side by side in README.md

# Notebook byte counts are dominated by embedded outputs (plots, tables),
# so they say little about the code written. They are left out of the mix.
EXCLUDED_LANGUAGES = {"Jupyter Notebook"}


def _open(w: int, h: int, title: str) -> list[str]:
    return [
        theme.svg_open(w, h, title),
        f"<style>{theme.font_face_css()}{theme.base_style()}</style>",
        theme.card_background(w, h),
    ]


# -------------------------------------------------------------------------
# stats.svg
# -------------------------------------------------------------------------
def render_stats(stats: UserStats) -> str:
    w, h = HALF_W, HALF_H
    active_days = sum(1 for _, c in stats.calendar_days if c > 0)
    languages = {lang for r in stats.repos for lang in r.languages}
    cells = [
        ("contributions", stats.total_contributions),
        ("commits", stats.commits),
        ("pull requests", stats.pull_requests),
        ("active days", active_days),
        ("public repos", len(stats.repos)),
        ("languages", len(languages)),
    ]

    parts = _open(w, h, "GitHub activity this year")
    parts.append(f'<text x="24" y="34" class="label accent">this year / {date.today().year}</text>')

    col_w = (w - 48) / 3
    for i, (label, value) in enumerate(cells):
        col, row = i % 3, i // 3
        x = 24 + col * col_w
        y = 86 + row * 66
        parts.append(f'<text x="{x:.0f}" y="{y}" font-size="26">{value:,}</text>')
        parts.append(
            f'<rect x="{x:.0f}" y="{y + 13}" width="7" height="7" rx="1.5" '
            f'fill="{theme.viridis(1.0 - 0.17 * i)}"/>'
        )
        parts.append(
            f'<text x="{x + 13:.0f}" y="{y + 20}" class="dim" font-size="11">{label}</text>'
        )

    parts.append("</svg>")
    return "".join(parts)


# -------------------------------------------------------------------------
# langs.svg
# -------------------------------------------------------------------------
def render_langs(stats: UserStats, top_n: int = 6) -> str:
    totals: dict[str, int] = {}
    for repo in stats.repos:
        if repo.is_archived:
            continue
        for lang, size in repo.languages.items():
            if lang not in EXCLUDED_LANGUAGES:
                totals[lang] = totals.get(lang, 0) + size

    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    grand_total = sum(totals.values()) or 1
    shown = ranked[:top_n]
    other = grand_total - sum(v for _, v in shown)
    if other > 0:
        shown.append(("Other", other))

    w, h = HALF_W, HALF_H
    parts = _open(w, h, "Languages by bytes")
    parts.append(f'<text x="24" y="34" class="label accent">languages / by bytes</text>')

    def color(i: int) -> str:
        if shown[i][0] == "Other":
            return theme.FG_FAINT
        return theme.viridis(1.0 - 0.8 * i / max(1, top_n - 1))

    # one stacked bar, clipped to a rounded rect
    bar_x, bar_y, bar_w, bar_h = 24, 52, w - 48, 10
    parts.append(
        f'<clipPath id="bar"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" '
        f'height="{bar_h}" rx="5"/></clipPath><g clip-path="url(#bar)">'
    )
    parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" fill="{theme.BORDER}"/>')
    x = float(bar_x)
    for i, (_, size) in enumerate(shown):
        seg = bar_w * size / grand_total
        parts.append(
            f'<rect x="{x:.2f}" y="{bar_y}" width="{seg + 0.5:.2f}" height="{bar_h}" fill="{color(i)}"/>'
        )
        x += seg
    parts.append("</g>")

    col_w = (w - 48) / 2
    for i, (lang, size) in enumerate(shown):
        col, row = i // 4, i % 4
        lx = 24 + col * col_w
        ly = 92 + row * 26
        parts.append(f'<rect x="{lx:.0f}" y="{ly - 8}" width="8" height="8" rx="2" fill="{color(i)}"/>')
        parts.append(f'<text x="{lx + 16:.0f}" y="{ly}" font-size="12">{theme.escape(lang)}</text>')
        parts.append(
            f'<text x="{lx + col_w - 16:.0f}" y="{ly}" class="dim" font-size="11" '
            f'text-anchor="end">{size / grand_total * 100:.1f}%</text>'
        )

    parts.append("</svg>")
    return "".join(parts)


# -------------------------------------------------------------------------
# year.svg - contribution calendar
# -------------------------------------------------------------------------
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def render_year(stats: UserStats) -> str:
    w = theme.CONTENT_WIDTH
    pad, label_w = 24, 30
    pitch = (w - 2 * pad - label_w) / 53
    cell = pitch - 3
    grid_x, grid_y = pad + label_w, 70
    h = int(grid_y + 7 * pitch + 46)

    days = stats.calendar_days
    today = date.today()
    first = date.fromisoformat(days[0][0]) if days else today
    offset = (first.weekday() + 1) % 7          # GitHub weeks start on Sunday
    max_count = max((c for _, c in days), default=0)

    def level(count: int) -> int:
        if count <= 0 or max_count == 0:
            return 0
        return min(4, math.ceil(4 * count / max_count))

    level_colors = [theme.CELL_EMPTY] + [theme.viridis(t) for t in (0.42, 0.62, 0.82, 1.0)]

    parts = _open(w, h, f"{stats.total_contributions} contributions in {today.year}")
    parts.append(f'<text x="{pad}" y="34" class="label accent">contributions / {today.year}</text>')
    parts.append(
        f'<text x="{w - pad}" y="34" class="dim" font-size="12" text-anchor="end">'
        f"{stats.total_contributions:,} this year</text>"
    )
    for d, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(
            f'<text x="{pad}" y="{grid_y + d * pitch + cell - 1:.1f}" class="faint" font-size="9.5">{name}</text>'
        )

    seen_months: set[int] = set()
    for idx, (iso, count) in enumerate(days):
        d = date.fromisoformat(iso)
        slot = idx + offset
        col, row = slot // 7, slot % 7
        x = grid_x + col * pitch
        y = grid_y + row * pitch
        if d.month not in seen_months and d.day <= 7:
            seen_months.add(d.month)
            parts.append(
                f'<text x="{x:.1f}" y="{grid_y - 9}" class="faint" font-size="9.5">{MONTHS[d.month - 1]}</text>'
            )
        if d > today:
            parts.append(
                f'<rect x="{x + 0.5:.1f}" y="{y + 0.5:.1f}" width="{cell - 1:.1f}" height="{cell - 1:.1f}" '
                f'rx="2" fill="none" stroke="{theme.CELL_EMPTY}"/>'
            )
            continue
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="2" '
            f'fill="{level_colors[level(count)]}"/>'
        )

    ly = h - 20
    lx = w - pad - 5 * 14 - 34
    parts.append(f'<text x="{lx - 8}" y="{ly + 9}" class="faint" font-size="10" text-anchor="end">less</text>')
    for i, c in enumerate(level_colors):
        parts.append(f'<rect x="{lx + i * 14}" y="{ly}" width="10" height="10" rx="2" fill="{c}"/>')
    parts.append(f'<text x="{lx + 5 * 14 + 4}" y="{ly + 9}" class="faint" font-size="10">more</text>')

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
    print("wrote stats.svg, langs.svg, year.svg", file=sys.stderr)


if __name__ == "__main__":
    main()
