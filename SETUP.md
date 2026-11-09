# Setup

This repo is the source for github.com/zaidbinnaveed's profile README.
Everything under `assets/` is generated — don't hand-edit SVGs there,
edit the scripts and re-run.

## One-time setup

1. **Portrait**: add your source photo as `assets/portrait_source.jpg`
   (or `.jpeg`/`.png`). High resolution, even lighting, front-on or
   slight angle — this matters more than the code, since CLAHE and the
   darkening curve can't recover detail that isn't in the source.
2. Push to `main`. The `push` trigger in `refresh.yml` runs the full
   pipeline once, replacing every placeholder in `assets/` with real
   output. After that it just refreshes daily.
3. **Selected work**: the project cards are defined in the `CARDS` list
   in `scripts/generate_cards.py`, and laid out two per row in
   `README.md`. Featured repos are an editorial decision, not a data
   one, so they are not auto-selected. Copy each card's figures from
   that repo's README so the claim and its evidence stay in sync.

## Local development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export GITHUB_TOKEN=ghp_xxx   # needs public_repo + read:user scopes; or $(gh auth token)

python scripts/generate_stats.py --login zaidbinnaveed
python scripts/generate_headers.py
python scripts/generate_hero.py
python scripts/generate_cards.py
python scripts/generate_portrait.py   # optional; requires assets/portrait_source.*
```

## Repo layout

```
.github/workflows/refresh.yml   daily Action: regenerate, commit if changed
scripts/theme.py                viridis palette / typography / font embedding
scripts/github_api.py           GraphQL client (GITHUB_TOKEN only)
scripts/generate_stats.py       stats.svg, langs.svg, year.svg
scripts/generate_headers.py     section heading SVGs
scripts/generate_hero.py        hero.svg: causal attention map over the name
scripts/generate_cards.py       cards/*.svg: one evidence card per project
scripts/generate_portrait.py    animated ASCII portrait (not shown in README)
assets/fonts/                   subsetted JetBrains Mono (woff2)
assets/                         generated output, committed by the Action
```

## Repository audit (not automated)

The guide calls for auditing every repo on the profile — README,
description, topics, pinning. That's an editorial pass this pipeline
doesn't attempt to automate: it decides what a repo *is*, not what its
star count is. Suggested order:

1. List all public, non-fork repos.
2. For each: does it have a real README (architecture, install,
   screenshots if relevant)? If not, write one or archive/hide the repo.
3. Pin the 4-6 that should represent you; update the Featured Projects
   table in `README.md` to match.
