# KB — Multi-Domain LLM-Wiki

Personal knowledge base covering three domains:

- `finance/` — investing decisions, theses, market entities
- `education/` — education consulting cases, frameworks, programs
- `runstrict-sales/` — sales & growth strategy for the RunStrict mobile app

Built on the LLM-Wiki methodology: the LLM is a disciplined wiki maintainer,
not a chatbot. Knowledge accumulates at ingest time into markdown pages with
frontmatter and wikilinks. Queries synthesize from existing pages rather than
re-deriving from raw sources every turn.

## How to use

Open this directory in Claude Code. The agent reads `CLAUDE.md` automatically.

### Add a source
1. Pick a domain.
2. Pick a `source-id` — format: `<publisher>-YYYY-MM-DD[-<short-slug>]`
   (e.g. `bloomberg-2026-04-15`, `ft-2026-04-22-samsung-memory`).
3. Create `<domain>/raw/<source-id>/` and drop the file(s) inside.
4. Run: `/ingest <domain>/raw/<source-id>/`

### Ask a question
```
/query 한국 메모리 사이클이 어디쯤일까?
```
Agent will confirm the domain, find pages, synthesize with citations + confidence.

### Save a good answer
After a `/query`, run `/file-answer` to promote it into a wiki page.

### Health check
```
/lint finance
```
Reports orphans, contradictions, uncited claims, token budgets.

## Hard invariants

1. Raw sources are immutable. Never edit anything under `*/raw/`.
2. Human curates, LLM maintains. You add sources & ask questions; the agent writes pages.
3. Every claim cites its source.
4. `log.md` is append-only.
5. Cross-domain isolation. No links between `finance/wiki/` ↔ `education/wiki/` ↔ `runstrict-sales/wiki/`.

See `CLAUDE.md` for the full operating manual.
