import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

INBOX_PATH = ".barrot/telegram_inbox.jsonl"
OFFSET_PATH = ".barrot/telegram_offset.txt"


def load_offset() -> int | None:
    if not os.path.exists(OFFSET_PATH):
        return None
    raw = open(OFFSET_PATH, "r", encoding="utf-8").read().strip()
    return int(raw) if raw.isdigit() else None


def save_offset(next_offset: int) -> None:
    with open(OFFSET_PATH, "w", encoding="utf-8") as f:
        f.write(str(next_offset))


def fetch_updates(token: str, offset: int | None, timeout: int = 25) -> list[dict]:
    params = {"timeout": str(timeout), "allowed_updates": json.dumps(["message"])}
    if offset is not None:
        params["offset"] = str(offset)
    url = f"https://api.telegram.org/bot{token}/getUpdates?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=timeout + 10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if not data.get("ok"):
        raise RuntimeError(f"Telegram getUpdates failed: {data}")
    return data.get("result", [])


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    expected_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not expected_chat_id:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID first.")

    offset = load_offset()
    while True:
        try:
            updates = fetch_updates(token, offset=offset)
            for upd in updates:
                upd_id = upd.get("update_id")
                if isinstance(upd_id, int):
                    offset = upd_id + 1
                    save_offset(offset)

                msg = upd.get("message") or {}
                chat = msg.get("chat") or {}
                sender = msg.get("from") or {}
                text = (msg.get("text") or "").strip()
                if sender.get("is_bot") or not text:
                    continue
                if str(chat.get("id", "")) != expected_chat_id:
                    continue

                record = {
                    "received_at": datetime.now(timezone.utc).isoformat(),
                    "update_id": upd_id,
                    "chat_id": chat.get("id"),
                    "from_username": sender.get("username"),
                    "text": text,
                }
                with open(INBOX_PATH, "a", encoding="utf-8") as out:
                    out.write(json.dumps(record) + "\n")
                print(f"[INBOX] {text}")
        except KeyboardInterrupt:
            print("\nStopped Telegram reply poller.")
            break
        except Exception as exc:
            print(f"[WARN] Poll error: {exc}")
            time.sleep(5)


if __name__ == "__main__":
    main()
