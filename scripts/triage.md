# /triage — Route inbox items into domains

Triggered by: `/triage` (no args). Pulls any pending Telegram messages, then
routes everything in `/inbox/` into the appropriate `<domain>/raw/<source-id>/`
location.

`/inbox/` is the pre-domain staging area where mobile captures land. The drain
runs as the FIRST step of triage (not on a background schedule — that would
require granting Full Disk Access to /bin/zsh due to macOS TCC restrictions on
launchd accessing /Volumes/*). Running drain interactively from your Claude
Code session inherits the terminal's permissions and Just Works.

## Pre-flight

1. **Drain Telegram first.** Run:
   ```bash
   cd /Volumes/ORICO/kb/scripts/inbox && .venv/bin/python drain_telegram.py
   ```
   Report how many new updates landed (read the last line of `drain.log`). If
   the drain errors out, surface the error and stop — don't proceed with stale
   inbox.

2. List the contents of `/inbox/` grouped by kind: `text/`, `photos/`, `voice/`,
   `pdfs/`, `chats/`. Show count per kind. If everything is empty, say so and stop.
2. For each kind, list items oldest-first with a one-line preview:
   - **text**: first 200 chars of the body
   - **photos**: filename + caption (from the `.md` stub)
   - **voice**: duration + first 200 chars of transcript
   - **pdfs**: filename + size in MB
   - **chats**: filename + first 200 chars

## Triage loop (process one item at a time)

For each item, propose to the user:

1. **Domain**: `finance` | `education` | `runstrict-sales`. If the content
   doesn't clearly fit one of the three, propose to leave it in `/inbox/` and
   move on — do NOT guess across domain boundaries (hard invariant #5).
2. **Source-id**: `<publisher-or-origin>-YYYY-MM-DD[-<short-slug>]` per
   `CLAUDE.md`. Origin for Telegram drops is typically:
   - `tg-voice` for your own voice memos
   - `tg-photo` for ad-hoc photo captures
   - The publisher slug for clipped articles (e.g. `bloomberg-2026-05-19`)
   - `chat-claude` / `chat-gpt` for exported chat history
3. **Wait for user confirmation** before moving anything.

On confirmation, for each item:
1. Create `<domain>/raw/<source-id>/` if it doesn't exist.
2. Move all related files from `/inbox/<kind>/<day>/` into that folder.
   Files are named `<HHMMSS>-<msg_id>` so a single Telegram message produces:
   - text: one `<slug>.md`
   - photo: `<slug>.jpg` + `<slug>.md`
   - voice: `<slug>.oga` + `<slug>.md`
   - pdf/chat: `<slug>-<original-filename>` + `<slug>.md`
   The slug (the `<HHMMSS>-<msg_id>` prefix) groups them — move every file
   that shares that prefix.
3. Use plain `mv` — source is gitignored, so `git mv` would fail.
4. `git add <domain>/raw/<source-id>/` to stage the new immutable source.

After the batch:
- Report items moved (grouped by domain) and items deferred.
- Print the suggested next commands:
  ```
  /ingest finance/raw/bloomberg-2026-05-19/
  /ingest runstrict-sales/raw/tg-voice-2026-05-19-pricing-idea/
  ```
- Do NOT auto-run `/ingest` — keep operations separate per the existing workflow.

## Stop conditions

- Two items propose the same source-id → ask the user how to disambiguate.
- An item could plausibly fit multiple domains → ask, do not guess.
- A voice transcript is the placeholder `[transcription failed]` → ask the user
  whether to re-run whisper now (`whisper /inbox/voice/.../<ts>.oga --model base`),
  transcribe manually, or defer.
- Never delete inbox originals on partial failure; leave them for retry.

## Notes

- `/inbox/` is gitignored — content there is only on the SSD and not mirrored
  to GitHub. Once moved into `<domain>/raw/`, it joins the canonical, mirrored
  vault and becomes immutable per invariant #1.
- Frontmatter on inbox items is informal (`source`, `kind`, `sender`, `captured`).
  Proper wiki frontmatter gets created later by `/ingest`.
