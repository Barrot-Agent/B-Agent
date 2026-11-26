import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path


def tg_api(method: str, token: str, params: dict | None = None) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    if params:
        data = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
    else:
        req = urllib.request.Request(url, method="GET")

    with urllib.request.urlopen(req, timeout=15) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        if not body.get("ok"):
            raise RuntimeError(f"Telegram API error on {method}: {body}")
        return body


def resolve_chat_id(token: str) -> int:
    data = tg_api("getUpdates", token)
    for item in reversed(data.get("result", [])):
        msg = item.get("message") or item.get("edited_message") or {}
        chat = msg.get("chat") or {}
        if "id" in chat:
            return int(chat["id"])
    raise RuntimeError(
        "No chat.id found in getUpdates. Send a fresh message (like /start or hello) "
        "to your bot in Telegram and run --get-chat-id again."
    )


def send_telegram(text: str, token: str, chat_id: str) -> None:
    tg_api(
        "sendMessage",
        token,
        {
            "chat_id": chat_id,
            "text": text[:4000],
            "disable_web_page_preview": "true",
        },
    )


def gh_get(path: str, token: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Barrot-Omega-Telegram-Reporter",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"https://api.github.com{path}", headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_report(repo: str, gh_token: str, command: str) -> str:
    commits = gh_get(f"/repos/{repo}/commits?per_page=1", gh_token)
    prs = gh_get(f"/repos/{repo}/pulls?state=open&per_page=10", gh_token)
    issues = gh_get(f"/repos/{repo}/issues?state=open&per_page=20", gh_token)
    open_issues = [i for i in issues if "pull_request" not in i]

    lines = [f"Barrot Report ({repo}) [{command}]"]
    if commits:
        sha = commits[0]["sha"][:7]
        msg = commits[0]["commit"]["message"].splitlines()[0][:80]
        lines.append(f"HEAD: {sha} - {msg}")
    lines.append(f"Open PRs: {len(prs)} | Open Issues: {len(open_issues)}")

    for pr in prs[:3]:
        lines.append(f"  PR #{pr['number']}: {pr['title'][:60]}")

    report_file = os.environ.get("BARROT_REPORT_FILE", "")
    if report_file and Path(report_file).is_file():
        snippet = Path(report_file).read_text(encoding="utf-8").strip()[:500]
        lines.append("Open-Code / Artifact Summary:")
        lines.append(snippet)

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Barrot Telegram Reporter & Chat ID Resolver")
    parser.add_argument(
        "--get-chat-id",
        action="store_true",
        help="Fetch and print the latest Telegram chat.id using TELEGRAM_BOT_TOKEN",
    )
    args = parser.parse_args()

    tg_token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TOKEN", "")
    if not tg_token:
        print("Error: set TELEGRAM_BOT_TOKEN (or TOKEN) in your environment.", file=sys.stderr)
        return 1

    if args.get_chat_id:
        chat_id = resolve_chat_id(tg_token)
        print(chat_id)
        return 0

    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not chat_id:
        print(
            "Error: set TELEGRAM_CHAT_ID explicitly; refusing to infer a Telegram recipient.",
            file=sys.stderr,
        )
        return 1

    repo = os.environ.get("GITHUB_REPOSITORY", "Barrot-Agent/B-Agent")
    gh_token = os.environ.get("GITHUB_TOKEN", "")
    command = os.environ.get("BARROT_COMMAND", "manual")
    send_telegram(build_report(repo, gh_token, command), tg_token, chat_id)
    print("Reply sent to Telegram.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
