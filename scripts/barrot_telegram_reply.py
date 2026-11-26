import argparse
import json
import os
import urllib.parse
import urllib.request

INBOX_PATH = ".barrot/telegram_inbox.jsonl"


def read_latest_inbox_text() -> str:
    if not os.path.exists(INBOX_PATH):
        return ""
    lines = [line.strip() for line in open(INBOX_PATH, "r", encoding="utf-8") if line.strip()]
    if not lines:
        return ""
    last = json.loads(lines[-1])
    return str(last.get("text", "")).strip()


def send_reply(token: str, chat_id: str, text: str) -> dict:
    payload = urllib.parse.urlencode({"chat_id": chat_id, "text": text[:4000]}).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if not data.get("ok"):
        raise RuntimeError(f"Telegram sendMessage failed: {data}")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a Telegram reply to Barrot's chat.")
    parser.add_argument("message", nargs="?", help="Reply text to send")
    parser.add_argument("--from-inbox", action="store_true", help="Echo latest inbox message in reply")
    args = parser.parse_args()

    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID first.")

    text = (args.message or "").strip()
    if args.from_inbox:
        latest = read_latest_inbox_text()
        text = f"Received: {latest}" if not text else f"{text} (last msg: {latest})"
    if not text:
        raise SystemExit("Provide a reply message or pass --from-inbox.")

    send_reply(token, chat_id, text)
    print("Reply sent to Telegram.")


if __name__ == "__main__":
    main()
