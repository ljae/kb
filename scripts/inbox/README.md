# Inbox drain

Pulls Telegram messages into `/inbox/` on the SSD. The `/triage` slash command
then routes items into `<domain>/raw/<source-id>/`.

## Files

- `drain_telegram.py` — the polling script (single pass; launchd re-invokes)
- `requirements.txt` — `requests` + optional `openai-whisper`
- `.env.example` → copy to `.env` and fill in your bot token
- `local.kb-drain.plist` — launchd job, runs the script every 15 minutes
- `.state.json` — last Telegram `update_id` (auto-managed)
- `drain.log`, `drain.stdout.log`, `drain.stderr.log` — runtime logs

## One-time setup

```bash
cd /Volumes/ORICO/kb/scripts/inbox

# Create a venv so launchd has predictable deps
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Optional: voice-note transcription
.venv/bin/pip install openai-whisper
brew install ffmpeg

# Configure
cp .env.example .env
# → open .env and paste your TELEGRAM_BOT_TOKEN
```

## Test it manually

```bash
cd /Volumes/ORICO/kb/scripts/inbox

# Send a test message to your bot from your phone first, then:
.venv/bin/python drain_telegram.py

# Check what landed
ls -la /Volumes/ORICO/kb/inbox/text/$(date +%Y-%m-%d)/
tail drain.log
```

## Scheduling

Default approach is **on-demand drain** via the `/triage` slash command — it
runs the drain as its first step. See `../triage.md`. This avoids macOS TCC
restrictions on launchd accessing `/Volumes/*`.

### Optional background drain (requires Full Disk Access grant)

Only if you want auto-drain while away from Claude Code. Trade-off: you must
grant Full Disk Access to `/bin/zsh` in System Settings → Privacy & Security,
which affects all future zsh launches by LaunchAgents on this Mac.

```bash
# After granting FDA to /bin/zsh:
cp /Volumes/ORICO/kb/scripts/inbox/local.kb-drain.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/local.kb-drain.plist
launchctl kickstart gui/$(id -u)/local.kb-drain
tail ~/Library/Logs/kb-drain.stderr.log   # should be empty if FDA worked
```

To stop:

```bash
launchctl bootout gui/$(id -u)/local.kb-drain
rm ~/Library/LaunchAgents/local.kb-drain.plist
```

## Behavior notes

- Exits silently when SSD isn't mounted — safe to run away from home.
- `getUpdates` retains messages for ~24h. If you're away longer than that,
  some captures may be lost; Telegram keeps the originals in your chat history
  so you can replay them.
- Each run processes everything new since the last `update_id`, then exits.
  launchd handles the cadence.
- Photos store as full-resolution JPEG. Voice as `.oga` (Opus).
- Transcription is best-effort; if whisper fails the `.md` gets a placeholder
  and you can retry inside `/triage`.

## Security

- `.env` is in `.gitignore` — never commit your bot token.
- Set `ALLOWED_USER_IDS` in `.env` if you want a hard allowlist (recommended
  if you ever share the bot username publicly).
