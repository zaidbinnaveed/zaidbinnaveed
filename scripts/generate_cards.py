"""
Generates assets/cards/<slug>.svg: one evidence card per featured project.

Each card leads with the project's headline result, set large, because the
profile's rule is that every claim sits next to its evidence. The figures
below are copied from each repository's README; change them there first.
Which projects are featured is an editorial choice, so it lives here as
data rather than being derived from star counts.

Cards are laid out two per row in README.md, each linked to its repo.
"""

from __future__ import annotations

from dataclasses import dataclass

import theme

W, H = 410, 214


@dataclass
class Card:
    slug: str
    name: str
    kind: str
    summary: str
    metric: str
    metric_label: str
    detail: str
    stack: list[str]


CARDS = [
    Card(
        slug="healwright",
        name="HealWright",
        kind="pytest-playwright plugin",
        summary="Heals broken selectors, proves each heal in a sandbox, and writes a reviewable patch.",
        metric="0",
        metric_label="false heals on trap scenarios",
        detail="99.2% true heals / 100% precision / 50 scenarios",
        stack=["Python", "Playwright", "LibCST", "FastAPI", "React"],
    ),
    Card(
        slug="shakespeare-llm",
        name="Shakespearean LLM",
        kind="transformer from scratch",
        summary="Decoder-only transformer built from mathematical primitives, without the transformers library.",
        metric="10.36",
        metric_label="validation perplexity",
        detail="809,984 params / 331 tests passing",
        stack=["PyTorch", "FastAPI", "React"],
    ),
    Card(
        slug="cereberus",
        name="Cereberus",
        kind="face-gated access control",
        summary="Local-first access control with blink liveness, explicit decision states and an audit log.",
        metric="5",
        metric_label="explicit decision states",
        detail="blink liveness / engine + API unit tests",
        stack=["Python", "OpenCV", "face_recognition", "React"],
    ),
    Card(
        slug="flyrank",
        name="FlyRank Content Scoring",
        kind="ml internship",
        summary="Ranks content for editorial refresh, with leakage checks and per-item reason codes.",
        metric="0.74",
        metric_label="precision@50",
        detail="30k-row client-group holdout / leakage checks",
        stack=["Python", "scikit-learn", "pandas"],
    ),
    Card(
        slug="spidey",
        name="Spidey",
        kind="parallel web crawler",
        summary="Semaphore-gated fetching, a thread-safe inverted index and live crawl telemetry.",
        metric="SSE",
        metric_label="live telemetry stream",
        detail="pause / resume / seed control under concurrency",
        stack=["Python", "FastAPI", "React", "TypeScript"],
    ),
    Card(
        slug="hiresense",
        name="HireSense AI",
        kind="llm mock interviewer",
        summary="Level-adaptive interview plans, streamed responses and a JSON-schema scorecard.",
        metric="4 x 10",
        metric_label="seniority tracks x domains",
        detail="Llama 3.3 70B on Groq / SSE streaming",
        stack=["FastAPI", "Groq", "React"],
    ),
]


def render_card(card: Card, index: int, total: int) -> str:
    # Each card takes its own stop along the text-safe half of viridis, so
    # the grid reads as one gradient from first card to last.
    color = theme.viridis(1.0 - 0.5 * index / max(1, total - 1))
    pad = 24

    parts = [theme.svg_open(W, H, f"{card.name}: {card.metric} {card.metric_label}")]
    parts.append(f"<style>{theme.font_face_css()}{theme.base_style()}</style>")
    parts.append(theme.card_background(W, H))
    # attention-row motif: a short strip of cells in the card's color
    for s in range(5):
        parts.append(
            f'<rect x="{pad + s * 9}" y="22" width="7" height="7" rx="1.5" '
            f'fill="{color}" opacity="{0.25 + 0.75 * (s + 1) / 5:.2f}"/>'
        )
    parts.append(
        f'<text x="{pad + 54}" y="29" class="label faint">{theme.escape(card.kind)}</text>'
    )
    parts.append(
        f'<text x="{W - pad}" y="29" class="faint" font-size="11" text-anchor="end">'
        f"{index + 1:02d}</text>"
    )
    parts.append(f'<text x="{pad}" y="60" font-size="19">{theme.escape(card.name)}</text>')

    for i, line in enumerate(theme.wrap(card.summary, 50)[:2]):
        parts.append(
            f'<text x="{pad}" y="{84 + i * 17}" class="dim" font-size="12">{theme.escape(line)}</text>'
        )

    metric_size = 34
    metric_w = len(card.metric) * metric_size * 0.6
    parts.append(
        f'<text x="{pad - 1}" y="152" font-size="{metric_size}" style="fill:{color}">'
        f"{theme.escape(card.metric)}</text>"
    )
    parts.append(
        f'<text x="{pad + metric_w + 12:.0f}" y="150" font-size="12">{theme.escape(card.metric_label)}</text>'
    )
    parts.append(
        f'<text x="{pad}" y="174" class="dim" font-size="11">{theme.escape(card.detail)}</text>'
    )

    parts.append(
        f'<line x1="{pad}" y1="188" x2="{W - pad}" y2="188" stroke="{theme.BORDER}"/>'
    )
    parts.append(
        f'<text x="{pad}" y="203" class="faint" font-size="10.5">'
        f'{theme.escape("  ".join(card.stack))}</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    out_dir = theme.REPO_ROOT / "assets" / "cards"
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, card in enumerate(CARDS):
        (out_dir / f"{card.slug}.svg").write_text(render_card(card, i, len(CARDS)), encoding="utf-8")
    print(f"wrote {len(CARDS)} project cards to {out_dir}")


if __name__ == "__main__":
    main()
