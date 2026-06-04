# /lint — Health-check a domain

Triggered by: `/lint <domain>`. Read-only by default; offers fixes.

## Checks (run all, group results by severity)

### Structural (errors)

- Pages missing required frontmatter fields (`title`, `id`, `type`, `sources`,
  `confidence`, `created`, `updated`).
- `sources:` referencing nonexistent `raw/` files.
- Filename ≠ `id` field.
- Wikilinks to nonexistent pages (broken `[[...]]`).
- Cross-domain links (any link pointing outside `<domain>/wiki/`).

### Content (warnings)

- Uncited paragraphs (a paragraph with a digit sequence > 3 chars and no
  `[...]` citation).
- Entity pages with empty required sections (per domain schema).
- Theses with `status: active` and `updated:` older than 30 days.
- Stale `confidence: low` pages older than 30 days.
- Pages where `updated:` < newest cited source's date (source has moved
  past the page).

### Graph health (warnings)

- Orphan pages (no inbound `[[...]]`).
- Concepts mentioned in 3+ pages with no page of their own.
- `index.md` token count: warn at 40K, alert at 80K. Above 80K propose a
  shard plan (e.g., split into `index-entities.md`, `index-concepts.md`).

### Contradictions (warnings)

- Same fact stated differently across pages (e.g., "revenue 2024: $X" vs
  "revenue 2024: $Y"). Report both pages and their source citations.

## Output format

- Group by severity (errors → warnings → graph → contradictions).
- Show file:line where possible.
- End with a "Suggested fixes" section. For each, the user can approve to
  have you apply it now.

## Append-only log

After lint completes, append to `log.md`:
```
## [YYYY-MM-DD] lint | <domain>
- errors: <count>
- warnings: <count>
```
