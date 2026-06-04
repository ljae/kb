# /file-answer — Promote a query result into a wiki page

Triggered by: `/file-answer` after a `/query`. Captures the synthesis as a
durable page so future queries compound.

## Steps

1. **Propose a page type and location**:
   - If the answer characterizes a specific entity → `entities/<...>` (likely
     an update to an existing page).
   - If the answer is a framework/principle → `concepts/<slug>.md`.
   - If the answer is a comparison or distilled analysis →
     `wiki/syntheses/<slug>.md` (create this folder if needed and propose it
     to user).

   Wait for user confirmation.
2. **Write the page** with full frontmatter. Carry over `sources:` from the
   query's cited pages and raw sources.
3. **Set `confidence:`** = the query's confidence.
4. **Add backlinks**: in each page cited by the query, add a "Related" entry
   pointing to the new page.
5. **Update `index.md`** and append to `log.md`:
   ```
   ## [YYYY-MM-DD] file-answer | <title>
   - created: <path/to/new-page.md>
   ```
6. **Report** path of the new page.
