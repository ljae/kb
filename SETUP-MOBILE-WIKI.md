# Mobile wiki setup — one-time walkthrough

End-to-end setup for the capture → triage → ingest → mobile-view pipeline.
Allow ~90 minutes. Everything below is free; no recurring cost.

## Architecture recap

```
Phone (anywhere)        Mac at home (only)              iPhone (Obsidian)
─────────────────       ────────────────────────        ──────────────────
Telegram bot DM    ─→   launchd /15min →                Obsidian Git plugin
                        drain_telegram.py               pulls from GitHub
                        ↓                          ↑
                        /inbox/  (gitignored)      │
                        ↓ (you, in Claude Code)    │
                        /triage → assign domain   │
                        ↓                          │
                        <domain>/raw/<source-id>/  │
                        ↓                          │
                        /ingest → wiki pages       │
                        ↓                          │
                        Obsidian Git auto-push ────┘
                              ↓
                        GitHub private repo
```

---

## 1. Create a Telegram bot (5 min)

1. Open Telegram → search `@BotFather` → start chat.
2. `/newbot` → name it (e.g. "KB Inbox") → username must end in `bot` (e.g. `jaelee_kb_bot`).
3. Save the bot token BotFather sends back — it looks like
   `1234567890:AAH...`. Treat it like a password.
4. DM your new bot once (send any message) so it can later reply to you.
5. (Recommended) `/setprivacy` → select your bot → `Disable`. This lets the bot
   read all messages in groups/channels if you ever expand later. For DM-only
   it doesn't matter.
6. (Optional, recommended) DM `@userinfobot` to find your numeric Telegram user
   ID. You'll paste it into `ALLOWED_USER_IDS` so only you can post.

## 2. Install drain dependencies (10 min)

```bash
cd /Volumes/ORICO/kb/scripts/inbox

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Optional but recommended for voice memos:
.venv/bin/pip install openai-whisper
brew install ffmpeg

# Configure
cp .env.example .env
# → edit .env, paste TELEGRAM_BOT_TOKEN and (optional) ALLOWED_USER_IDS
```

## 3. Test the drain manually (5 min)

```bash
# From your phone: send a text message to your bot
# Then on the Mac:
cd /Volumes/ORICO/kb/scripts/inbox
.venv/bin/python drain_telegram.py

# Inspect what landed:
ls -la /Volumes/ORICO/kb/inbox/text/$(date +%Y-%m-%d)/
tail drain.log
```

Send one of each: text, photo, voice note, PDF — verify all four land in their
respective `/inbox/` subfolders.

## 4. Drain scheduling — on-demand, not background

The original plan used a launchd job to drain every 15 minutes. **Don't do
this** on recent macOS. The launchd process is sandboxed by TCC (Transparency,
Consent, Control) and rejected access to anything on `/Volumes/*` — including
the script binary, working directory, and stdout/stderr log paths. Symptom:
`last exit code = 1`, stderr says `realpath: ... Operation not permitted`.

Instead, the drain runs as the **first step of `/triage`** in Claude Code.
Since Claude Code's shell session inherits your terminal's permissions, /Volumes
access works. When you sit down at the Mac to process your captures, you run
`/triage` and the drain happens automatically before the triage UI appears.

If you ever want to drain outside a Claude Code session:

```bash
cd /Volumes/ORICO/kb/scripts/inbox && .venv/bin/python drain_telegram.py
```

Add a shell alias to your `~/.zshrc` if you find yourself doing this a lot:

```bash
alias kbdrain='cd /Volumes/ORICO/kb/scripts/inbox && ./.venv/bin/python drain_telegram.py'
```

### Optional: background drain via launchd

If you want background draining (e.g., to drain while you're away from Claude
Code), grant Full Disk Access to `/bin/zsh`:

1. System Settings → Privacy & Security → Full Disk Access
2. Click "+" (auth required)
3. Press ⌘⇧G → type `/bin/zsh` → Enter (the `/bin` folder is normally hidden)
4. Select `zsh` → Open → make sure the new entry is toggled ON
5. Re-install the launchd job:
   ```bash
   cp /Volumes/ORICO/kb/scripts/inbox/local.kb-drain.plist ~/Library/LaunchAgents/
   launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/local.kb-drain.plist
   launchctl kickstart gui/$(id -u)/local.kb-drain
   tail ~/Library/Logs/kb-drain.stderr.log   # should be empty
   ```

To pause: `launchctl bootout gui/$(id -u)/local.kb-drain`.

Granting `/bin/zsh` Full Disk Access affects ALL future zsh launches by
LaunchAgents on this Mac — not just this drain. Decide if that's acceptable.

## 5. Create the GitHub mirror (10 min)

1. github.com → New repository → name `kb` (or whatever) → **Private** → no README/gitignore (we have them).
2. On the Mac:
   ```bash
   cd /Volumes/ORICO/kb
   git remote add origin git@github.com:<your-handle>/kb.git
   git add .
   git commit -m "feat: add /inbox staging + telegram drain + /triage"
   git push -u origin main
   ```
   If SSH isn't set up, use HTTPS and a Personal Access Token instead.

## 6. Generate a GitHub Personal Access Token (5 min)

You need this for the iPhone Obsidian Git plugin (Obsidian on mobile uses HTTPS).

1. GitHub → Settings → Developer settings → **Fine-grained tokens** → Generate new.
2. Repository access → **Only select repositories** → pick your `kb` repo.
3. Permissions → Repository → **Contents: Read and write**.
4. Expiry: pick 1 year for low-rotation friction.
5. Generate → copy the token (starts with `github_pat_...`) — you only see it once.

## 7. Install Obsidian on Mac (10 min)

1. obsidian.md → download Mac app → install.
2. Open vault → "Open folder as vault" → select `/Volumes/ORICO/kb`.
3. Settings → Community plugins → enable → Browse → install **Obsidian Git**.
4. Configure Obsidian Git:
   - Vault backup interval: `30` (minutes)
   - Auto pull on startup: ON
   - Auto pull interval: `30`
   - Commit message: `vault: {{date}} {{numFiles}} files`
   - Author name / email: your git identity
5. (Optional) Install plugins: **Templater**, **Dataview**, **Excalidraw** as you need them.

## 8. Install Obsidian on iPhone (10 min)

1. App Store → install Obsidian (free).
2. First launch → "Create new vault" — pick a local name (it'll be replaced).
3. Settings → Community plugins → **turn on community plugins** (one tap).
4. Browse → install **Obsidian Git** (mobile version exists, less polished but works).
5. Configure plugin → Clone URL: `https://github.com/<your-handle>/kb.git`
6. Authentication → username = your GitHub handle, password = the PAT from step 6.
7. Clone → wait — the SSD-mirrored vault appears.
8. Pull-to-refresh from the file pane, or use the plugin's pull/push buttons.

## 9. Test the full loop (5 min)

1. **Phone**: send a voice note to your bot.
2. **Wait up to 15 min** (or run `launchctl kickstart gui/$(id -u)/local.kb-drain`).
3. **Mac**: `ls /Volumes/ORICO/kb/inbox/voice/$(date +%Y-%m-%d)/` — see your `.oga` + `.md`.
4. **Mac**: `cd /Volumes/ORICO/kb && claude` → `/triage` → confirm domain + source-id → it moves to `<domain>/raw/...`.
5. **Mac**: `/ingest <domain>/raw/<source-id>/` → wiki pages created.
6. **Mac**: Obsidian Git auto-push within 30 min (or hit "Commit + Push" manually).
7. **iPhone**: Obsidian Git → Pull. The new wiki pages appear.

---

## Daily flow once everything's set up

| When | Where | What |
|---|---|---|
| Throughout day | Phone, anywhere | Fire web clippings, photos, voice memos, PDFs at your Telegram bot |
| Implicit | Mac at home | launchd drains every 15 min into `/inbox/` |
| Evening | Mac, terminal | `cd /Volumes/ORICO/kb && claude` → `/triage` → assign domains + source-ids → `/ingest <path>` per source |
| Implicit | Mac, Obsidian | Auto-commits + pushes to GitHub every 30 min |
| Next day, away | iPhone | Open Obsidian → Pull → read the curated wiki pages |
| On the go | iPhone, Claude app | Use the GitHub connector pointed at the `kb` repo to ask questions about your wiki |

## Common ops

| Task | Command |
|---|---|
| Pause the drain | `launchctl bootout gui/$(id -u)/local.kb-drain` |
| Resume the drain | `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/local.kb-drain.plist` |
| Run the drain right now | `launchctl kickstart gui/$(id -u)/local.kb-drain` |
| View drain logs | `tail -f /Volumes/ORICO/kb/scripts/inbox/drain.log` |
| See last update_id | `cat /Volumes/ORICO/kb/scripts/inbox/.state.json` |
| Reset Telegram offset (replay last 24h) | edit `.state.json` to `{"offset": 0}` |
| Manually transcribe a voice note | `cd /Volumes/ORICO/kb/scripts/inbox && .venv/bin/whisper /path/to/voice.oga --model base --output_format txt --output_dir /tmp` |

## Constraints worth knowing

- **24h Telegram retention**: if the Mac is off for >24h, messages older than
  that may be lost from `getUpdates`. Originals stay in your Telegram chat
  history, so you can scroll back and re-send.
- **GitHub repo size**: tracked photos and PDFs will add up. If your repo
  exceeds ~1GB GitHub will start warning. Mitigation: add per-extension
  gitignore patterns (e.g. `*/raw/**/*.jpg` to keep only the markdown stubs
  in git while images stay SSD-only), or migrate heavy assets to Git LFS.
- **No background ingest**: `/triage` and `/ingest` are explicit human steps.
  This is by design — the architecture's invariant #2 is "human curates, LLM
  maintains". The drain is the only fully automatic step.
- **Mobile is read-mostly**: Obsidian Git on iOS supports editing + push, but
  it's slower than Mac. The intended pattern is capture-on-mobile, curate-on-Mac,
  view-on-mobile.
