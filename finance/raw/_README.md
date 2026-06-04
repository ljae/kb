# Finance Raw Sources

Drop new sources here as: `<source-id>/<original-filename>`

Where `<source-id>` follows: `<publisher-or-origin>-YYYY-MM-DD[-<short-slug>]`

Examples:
```
raw/bloomberg-2026-04-15/article.pdf
raw/ft-2026-04-22-samsung-memory/article.html
raw/sk-hynix-q1-2026/earnings-transcript.txt
```

## Hard rule

These files are **immutable**. The agent reads them but never edits, renames,
or deletes them. If a source needs correction, drop a new source-id (e.g.,
`-corrected`) and link from the wiki page.
