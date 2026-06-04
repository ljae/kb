# /ingest — Process a new raw source

Triggered by: `/ingest <path>` where `<path>` is a file or folder under `<domain>/raw/`.

## Steps (do them in order, narrate as you go)

1. **Read** the source file. If it's a PDF/image-heavy doc, do the text pass
   only on this step.
2. **Identify the domain** from the path. Load `<domain>/CLAUDE.md` if not
   already in context.
3. **Discuss takeaways with the user**: 3-5 bullets, what's new vs. what's
   already known. Wait for user input before proceeding.
4. **Plan the wiki updates**: list every page you intend to create or modify.
   For each, say "create" or "update" and which sections will change. Get
   user confirmation before writing.
5. **Create a source-summary page** at `<domain>/wiki/sources/<source-id>.md`
   with full frontmatter (`type: summary`), 1-paragraph TL;DR, key claims with
   quotes, and open questions.
6. **Update or create entity pages** per the domain schema. Respect citations
   — every new fact gets `[source-id]`.
7. **Update concepts/theses/cases/plays** where the source bears on them.
8. **Update `index.md`** with any new pages (alphabetical within section).
9. **Append to `log.md`**:
   ```
   ## [YYYY-MM-DD] ingest | <source title>
   - <bullet list of pages touched>
   ```
10. **Image second pass** (if applicable): open referenced images via Read,
    annotate what they show in the relevant wiki pages. Save extracted chart
    images to `raw/<source-id>/assets/`.
11. **Report**: summary of what changed, total pages touched.

## Stop conditions
- If the source duplicates an existing source ID → ask the user how to proceed.
- If you cannot identify the domain → ask, do not guess.
- If a proposed change would violate cross-domain isolation → refuse, explain.
