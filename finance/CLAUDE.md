# Finance Wiki — Schema

## Purpose

Personal decision-support KB for investing. Output should be usable for:
(a) my own buy/sell/hold decisions,
(b) feeding a downstream investing-copilot agent,
(c) drafting newsletter/blog posts.

NOT for: client advice, regulated recommendations.

## Page types (seed taxonomy)

### `entities/` — things that exist in the market

- `entities/companies/<slug>.md` — single ticker. Required sections:
  Overview · Business model · Numbers (rev/margin/cash) · Moat · Risks · Open questions
- `entities/sectors/<slug>.md` — semis, memory, banks, etc. Required sections:
  Structure · Players · Cycle position · Tailwinds/headwinds
- `entities/macro/<slug>.md` — themes (US rates, KRW, China property, AI capex).
- `entities/indicators/<slug>.md` — VIX, M2, ISM, KOSPI breadth, etc.

### `concepts/` — frameworks and mental models

- `concepts/<slug>.md` — base rates, Kelly criterion, expectations investing, etc.

### `theses/` — active positions and watchlist ideas

- `theses/<slug>.md`. Required sections:
  Thesis (1 sentence) · Conviction (1-5) · Time horizon · Entry rationale ·
  What would falsify · Exit conditions · Current status
- `status: active | monitoring | closed`. On close: append a `Postmortem`
  section. Never delete.

## Citation rules

- Cite raw sources with their file ID: `[bloomberg-2026-04-15]`.
- Cross-link wiki pages with Obsidian-style: `[[entities/companies/samsung-electronics]]`.
- Numbers (revenue, multiples, margins) MUST cite the specific source.
- Direct quotes from sources are wrapped in `>` blockquotes with attribution.

## Image handling

For chart-heavy sources (Bloomberg PDFs, broker reports):

1. First pass: read text only. Write skeleton wiki page.
2. Second pass: explicitly open referenced images via Read tool. Annotate
   what the chart shows in the wiki page.
3. Save extracted chart images to `raw/<source-id>/assets/`.

## Ingest specifics

When ingesting a finance source:

- Identify all tickers/companies mentioned → ensure each has an entity page.
- Identify any macro/sector themes → update or create.
- If the source contains a clear directional view, propose a thesis page
  (don't auto-create — confirm with user).
- Append to `log.md`.

## Lint specifics

- Flag any entity page with no `sources:` cited.
- Flag any thesis where `updated:` is older than 30 days AND `status: active`.
- Flag any number (a digit sequence > 3 chars) in a page that has no inline
  citation.
- Report `index.md` token count; warn at 40K, alert at 80K.
