#!/usr/bin/env python3
"""
Telegram → KB inbox drain.

Polls a Telegram bot for new messages and files them into /inbox/ on the SSD
as a pre-domain staging area. The /triage slash command then moves items into
<domain>/raw/<source-id>/ for canonical, immutable storage.

Designed to run periodically via launchd. Exits silently if the SSD isn't
mounted, so it's safe to invoke when you're away from home.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
VAULT = SCRIPT_DIR.parent.parent
INBOX = VAULT / "inbox"
STATE_FILE = SCRIPT_DIR / ".state.json"
LOG_FILE = SCRIPT_DIR / "drain.log"
ENV_FILE = SCRIPT_DIR / ".env"

# Pre-flight: silent exit if SSD not mounted (launchd safety)
if not VAULT.exists():
    sys.exit(0)
INBOX.mkdir(parents=True, exist_ok=True)

try:
    import requests
except ImportError:
    sys.stderr.write(
        f"Missing dependency 'requests'. Run:\n"
        f"  {SCRIPT_DIR}/.venv/bin/pip install -r {SCRIPT_DIR}/requirements.txt\n"
    )
    sys.exit(1)


def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


env = load_env(ENV_FILE)
TOKEN = env.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    sys.stderr.write(
        "TELEGRAM_BOT_TOKEN not set. Copy .env.example → .env and fill it in.\n"
    )
    sys.exit(1)

ALLOWED_USER_IDS = {
    int(x) for x in (env.get("ALLOWED_USER_IDS") or "").split(",") if x.strip().isdigit()
}
WHISPER_MODEL = env.get("WHISPER_MODEL") or "base"
WHISPER_LANGUAGE = env.get("WHISPER_LANGUAGE") or ""

API = f"https://api.telegram.org/bot{TOKEN}"
FILE_API = f"https://api.telegram.org/file/bot{TOKEN}"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("drain")


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            log.warning("state file corrupt; resetting")
    return {"offset": 0}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


def get_updates(offset: int) -> list:
    r = requests.get(
        f"{API}/getUpdates",
        params={
            "offset": offset,
            "timeout": 0,
            "allowed_updates": json.dumps(["message", "channel_post"]),
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["result"]


def get_file_path(file_id: str) -> str:
    r = requests.get(f"{API}/getFile", params={"file_id": file_id}, timeout=15)
    r.raise_for_status()
    return r.json()["result"]["file_path"]


def download(file_id: str, dest: Path) -> None:
    file_path = get_file_path(file_id)
    url = f"{FILE_API}/{file_path}"
    r = requests.get(url, timeout=120, stream=True)
    r.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)


def now_stamp() -> tuple[str, str]:
    n = datetime.now()
    return n.strftime("%Y-%m-%d"), n.strftime("%H%M%S")


def day_dir(kind: str) -> Path:
    day, _ = now_stamp()
    d = INBOX / kind / day
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_slug(msg: dict) -> str:
    """`HHMMSS-<msg_id>` — unique even when messages arrive in the same second."""
    _, ts = now_stamp()
    return f"{ts}-{msg.get('message_id', 'x')}"


def sender_label(msg: dict) -> str:
    if "from" in msg:
        u = msg["from"]
        name = (u.get("username")
                or " ".join(filter(None, [u.get("first_name"), u.get("last_name")]))
                or str(u.get("id", "?")))
        return name
    if "sender_chat" in msg:
        return msg["sender_chat"].get("title", "channel")
    return "unknown"


def fm(data: dict) -> str:
    """Minimal frontmatter writer — quotes values with special chars."""
    def fmt(v):
        if isinstance(v, str):
            if v == "" or any(c in v for c in ':#@&*!|>%`,[]{}"\n') or v.strip() != v:
                return '"' + v.replace('"', '\\"') + '"'
            return v
        return str(v)
    lines = ["---"]
    for k, v in data.items():
        lines.append(f"{k}: {fmt(v)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def handle_text(msg: dict) -> None:
    text = (msg.get("text") or "").strip()
    if not text:
        return
    slug = make_slug(msg)
    path = day_dir("text") / f"{slug}.md"
    body = fm({
        "source": "telegram",
        "kind": "text",
        "sender": sender_label(msg),
        "captured": datetime.now().isoformat(timespec="seconds"),
        "telegram_msg_id": msg.get("message_id"),
    }) + "\n" + text + "\n"
    path.write_text(body)
    log.info(f"text → {path.relative_to(VAULT)}")


def handle_photo(msg: dict) -> None:
    photos = msg.get("photo") or []
    if not photos:
        return
    largest = max(photos, key=lambda p: p.get("file_size", 0))
    slug = make_slug(msg)
    img_dest = day_dir("photos") / f"{slug}.jpg"
    download(largest["file_id"], img_dest)
    caption = msg.get("caption") or ""
    md_dest = day_dir("photos") / f"{slug}.md"
    body = fm({
        "source": "telegram",
        "kind": "photo",
        "sender": sender_label(msg),
        "captured": datetime.now().isoformat(timespec="seconds"),
        "image": f"{slug}.jpg",
        "telegram_msg_id": msg.get("message_id"),
    }) + f"\n![[{slug}.jpg]]\n\n{caption}\n"
    md_dest.write_text(body)
    log.info(f"photo → {img_dest.relative_to(VAULT)}")


def handle_voice(msg: dict) -> None:
    voice = msg.get("voice") or msg.get("audio")
    if not voice:
        return
    slug = make_slug(msg)
    audio_dest = day_dir("voice") / f"{slug}.oga"
    download(voice["file_id"], audio_dest)
    duration = voice.get("duration", 0)
    transcript = transcribe(audio_dest)
    md_dest = day_dir("voice") / f"{slug}.md"
    body = fm({
        "source": "telegram",
        "kind": "voice",
        "sender": sender_label(msg),
        "captured": datetime.now().isoformat(timespec="seconds"),
        "audio": f"{slug}.oga",
        "duration_s": duration,
        "telegram_msg_id": msg.get("message_id"),
    }) + f"\nAudio: `{slug}.oga` ({duration}s)\n\n## Transcript\n\n{transcript}\n"
    md_dest.write_text(body)
    log.info(f"voice → {audio_dest.relative_to(VAULT)} ({duration}s)")


def handle_document(msg: dict) -> None:
    doc = msg.get("document")
    if not doc:
        return
    slug = make_slug(msg)
    name = doc.get("file_name") or f"{slug}.bin"
    ext = name.lower().rsplit(".", 1)[-1] if "." in name else ""
    if ext in {"txt", "md", "json", "html", "htm"}:
        kind = "chats"
    else:
        kind = "pdfs"
    safe_name = f"{slug}-{name}"
    file_dest = day_dir(kind) / safe_name
    download(doc["file_id"], file_dest)
    size_mb = (doc.get("file_size") or 0) / 1024 / 1024
    caption = msg.get("caption") or ""
    md_dest = day_dir(kind) / f"{slug}.md"
    body = fm({
        "source": "telegram",
        "kind": kind.rstrip("s"),
        "sender": sender_label(msg),
        "captured": datetime.now().isoformat(timespec="seconds"),
        "file": safe_name,
        "size_mb": f"{size_mb:.2f}",
        "telegram_msg_id": msg.get("message_id"),
    }) + f"\nFile: `{safe_name}` ({size_mb:.1f} MB)\n\n{caption}\n"
    md_dest.write_text(body)
    log.info(f"{kind[:-1]} → {file_dest.relative_to(VAULT)} ({size_mb:.1f} MB)")


def transcribe(audio_path: Path) -> str:
    """Try local whisper; on any failure, write a placeholder for later retry."""
    if subprocess.run(["which", "whisper"], capture_output=True).returncode != 0:
        return "_[whisper not installed — `pip install openai-whisper` to enable]_"
    try:
        cmd = [
            "whisper", str(audio_path),
            "--model", WHISPER_MODEL,
            "--output_format", "txt",
            "--output_dir", str(audio_path.parent),
            "--fp16", "False",
        ]
        if WHISPER_LANGUAGE:
            cmd.extend(["--language", WHISPER_LANGUAGE])
        result = subprocess.run(cmd, capture_output=True, timeout=600, text=True)
        txt_file = audio_path.with_suffix(".txt")
        if txt_file.exists():
            text = txt_file.read_text().strip()
            txt_file.unlink()
            return text or "_[empty transcription]_"
        log.warning(f"whisper produced no output: {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        log.warning("whisper timed out")
    except Exception as e:
        log.warning(f"whisper error: {e}")
    return "_[transcription failed — retry via triage]_"


def handle_message(msg: dict) -> None:
    sender_id = (msg.get("from") or {}).get("id")
    if ALLOWED_USER_IDS and sender_id not in ALLOWED_USER_IDS:
        log.warning(f"ignored non-allowed sender {sender_id}")
        return

    has_attachment = False
    if "photo" in msg:
        handle_photo(msg); has_attachment = True
    if "voice" in msg or "audio" in msg:
        handle_voice(msg); has_attachment = True
    if "document" in msg:
        handle_document(msg); has_attachment = True
    if "text" in msg and not has_attachment:
        handle_text(msg)


def main() -> int:
    state = load_state()
    offset = state["offset"]
    try:
        updates = get_updates(offset)
    except requests.RequestException as e:
        log.error(f"getUpdates failed: {e}")
        return 1
    if not updates:
        return 0
    for u in updates:
        try:
            msg = u.get("message") or u.get("channel_post")
            if msg:
                handle_message(msg)
        except Exception as e:
            log.exception(f"failed update {u.get('update_id')}: {e}")
        state["offset"] = u["update_id"] + 1
        save_state(state)
    log.info(f"processed {len(updates)} updates, offset → {state['offset']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
