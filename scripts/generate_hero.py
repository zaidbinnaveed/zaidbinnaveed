"""
Generates assets/hero.svg: the profile's opening image.

The left half is a real causal self-attention map computed over the
letters of my name, the same operation as one head of the decoder-only
transformer in AI-Engineering-Assignment-01. Embeddings and projections
are random with a fixed seed, so the weights are illustrative rather than
learned, and the caption says so. Each row is one query; a CSS animation
steps through the rows and lights the matching letter of the name on the
right, so the picture reads as "this letter attends to these earlier ones".
"""

from __future__ import annotations

import numpy as np

import theme

NAME = "ZAID BIN NAVEED"
ROLE = "AI/ML Engineer"
FOCUS = "LLM agents / retrieval / computer vision / evaluation"
LINE_1 = "AI Automation Engineer @ Hemzo Media"
LINE_2 = "BS Artificial Intelligence, FAST NUCES '27"

D_MODEL = 16
SEED = 16
TEMPERATURE = 2.2   # sharpens the softmax so the structure is visible
STEP_S = 0.75       # seconds each query row stays highlighted


def attention(tokens: list[str]) -> np.ndarray:
    """Causal softmax(QK^T / sqrt(d)) for one head over character tokens."""
    rng = np.random.default_rng(SEED)
    vocab = sorted(set(tokens))
    embed = {ch: rng.normal(size=D_MODEL) for ch in vocab}
    n = len(tokens)
    pos = np.arange(n)[:, None] / np.power(10000, np.arange(D_MODEL)[None, :] / D_MODEL)
    pos_enc = np.where(np.arange(D_MODEL) % 2 == 0, np.sin(pos), np.cos(pos)) * 0.5
    x = np.stack([embed[ch] for ch in tokens]) + pos_enc
    w_q = rng.normal(size=(D_MODEL, D_MODEL)) / np.sqrt(D_MODEL)
    w_k = rng.normal(size=(D_MODEL, D_MODEL)) / np.sqrt(D_MODEL)
    scores = (x @ w_q) @ (x @ w_k).T / np.sqrt(D_MODEL) * TEMPERATURE
    scores = np.where(np.tril(np.ones((n, n), dtype=bool)), scores, -np.inf)
    scores -= scores.max(axis=1, keepdims=True)
    weights = np.exp(scores)
    return weights / weights.sum(axis=1, keepdims=True)


def render_hero() -> str:
    tokens = [ch for ch in NAME if ch != " "]
    n = len(tokens)
    weights = attention(tokens)

    w, h = theme.CONTENT_WIDTH, 340
    cell, gap = 15, 2
    pitch = cell + gap
    mx, my = 64, 74                       # matrix origin
    cycle = n * STEP_S
    on = 100 / n                          # % of the cycle a row is lit

    css = f"""
    {theme.font_face_css()}
    {theme.base_style()}
    .hl {{ animation: mv {cycle:.2f}s steps({n}, end) infinite; }}
    @keyframes mv {{ from {{ transform: translateY(0); }} to {{ transform: translateY({n * pitch}px); }} }}
    .ql {{ fill: {theme.FG_DIM}; animation: ql {cycle:.2f}s linear infinite; }}
    @keyframes ql {{
        0% {{ fill: {theme.ACCENT_HI}; }} {on * 0.98:.2f}% {{ fill: {theme.ACCENT_HI}; }}
        {on:.2f}% {{ fill: {theme.FG_DIM}; }} 100% {{ fill: {theme.FG_DIM}; }}
    }}
    .nl {{ fill: {theme.FG}; animation: nl {cycle:.2f}s linear infinite; }}
    @keyframes nl {{
        0% {{ fill: {theme.ACCENT_HI}; }} {on * 0.98:.2f}% {{ fill: {theme.ACCENT_HI}; }}
        {on:.2f}% {{ fill: {theme.FG}; }} 100% {{ fill: {theme.FG}; }}
    }}
    @media (prefers-reduced-motion: reduce) {{ .hl {{ display: none; }} }}
    """

    parts = [theme.svg_open(w, h, f"{NAME.title()}, {ROLE}"), f"<style>{css}</style>"]
    parts.append(theme.card_background(w, h))

    # --- attention matrix ------------------------------------------------
    parts.append(f'<text x="{mx}" y="38" class="label faint">keys</text>')
    for j, ch in enumerate(tokens):
        cx = mx + j * pitch + cell / 2
        parts.append(
            f'<text x="{cx:.1f}" y="{my - 9}" font-size="11" class="dim" '
            f'text-anchor="middle">{ch}</text>'
        )
    # masked (future) cells: faint outlines so the causal triangle reads
    for i in range(n):
        for j in range(i + 1, n):
            x, y = mx + j * pitch, my + i * pitch
            parts.append(
                f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{cell - 1}" height="{cell - 1}" '
                f'rx="2" fill="none" stroke="{theme.BORDER}"/>'
            )
    for i in range(n):
        row_max = weights[i, : i + 1].max()
        delay = i * STEP_S
        parts.append("<g>")
        parts.append(
            f'<text x="{mx - 10}" y="{my + i * pitch + 11.5}" font-size="11" class="ql" '
            f'style="animation-delay:{delay:.2f}s" text-anchor="end">{tokens[i]}</text>'
        )
        for j in range(i + 1):
            t = weights[i, j] / row_max
            x, y = mx + j * pitch, my + i * pitch
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" '
                f'fill="{theme.viridis(0.08 + 0.92 * t)}"/>'
            )
        parts.append("</g>")
    parts.append(
        f'<rect class="hl" x="{mx - 3.5}" y="{my - 2.5}" width="{n * pitch + 3}" '
        f'height="{pitch + 1}" rx="4" fill="none" stroke="{theme.ACCENT_HI}" stroke-width="1.5"/>'
    )
    parts.append(
        f'<text x="{mx - 46}" y="{my + n * pitch / 2}" class="label faint" '
        f'transform="rotate(-90 {mx - 46} {my + n * pitch / 2})" text-anchor="middle">queries</text>'
    )

    # --- identity block --------------------------------------------------
    tx = mx + n * pitch + 70
    letter_spans = []
    k = 0
    for ch in NAME:
        if ch == " ":
            letter_spans.append(" ")
            continue
        letter_spans.append(
            f'<tspan class="nl" style="animation-delay:{k * STEP_S:.2f}s">{ch}</tspan>'
        )
        k += 1
    parts.append(
        f'<text x="{tx}" y="140" font-size="38" xml:space="preserve">{"".join(letter_spans)}</text>'
    )
    parts.append(
        f'<text x="{tx + 2}" y="174" class="label" style="fill:{theme.ACCENT_HI}" '
        f'font-size="12">{theme.escape(ROLE)}</text>'
    )
    parts.append(f'<text x="{tx + 2}" y="210" class="dim" font-size="13">{theme.escape(FOCUS)}</text>')
    parts.append(f'<text x="{tx + 2}" y="240" font-size="13">{theme.escape(LINE_1)}</text>')
    parts.append(f'<text x="{tx + 2}" y="262" class="dim" font-size="13">{theme.escape(LINE_2)}</text>')

    # --- caption + legend ------------------------------------------------
    cap_y = my + n * pitch + 34
    parts.append(
        f'<text x="{mx - 46}" y="{cap_y}" class="faint" font-size="10.5">'
        f"fig. 1  causal self-attention over the letters of my name: one head, d={D_MODEL}, "
        f"fixed seed, untrained weights.</text>"
    )
    lx = tx + 2
    ly = 290
    parts.append(f'<text x="{lx}" y="{ly + 9}" class="faint" font-size="10">0</text>')
    for s in range(10):
        parts.append(
            f'<rect x="{lx + 14 + s * 9}" y="{ly}" width="9" height="11" fill="{theme.viridis(s / 9)}"/>'
        )
    parts.append(
        f'<text x="{lx + 14 + 96}" y="{ly + 9}" class="faint" font-size="10">weight / row max</text>'
    )

    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    out = theme.REPO_ROOT / "assets" / "hero.svg"
    out.write_text(render_hero(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
