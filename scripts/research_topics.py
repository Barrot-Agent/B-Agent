#!/usr/bin/env python3
"""
BARROT-Ω TOPIC RESEARCH — real, honest research on the curriculum topic list
recovered from the (unusable, 300-char-truncated) workspace.barrot.brain table.
Separate from the XRP-signal knowledge-base/log.jsonl on purpose: these are not
news items, have no URL, and don't fit the sentiment/catalyst/xrp_relevance
schema. Idempotent: skips topics already present in the output file.

Paces requests to stay under Groq's per-minute rate limit (a prior version
hit that limit after 30 requests in 24s and wrongly treated it as the daily
token cap being exhausted). On a real 429, distinguishes: if Groq's error
body says per-minute/RPM, backs off and retries; if it says per-day/TPD,
stops the run cleanly for a later re-trigger.
"""
import json, os, sys, time, urllib.request, urllib.error

TOPICS_PATH = "brain_corpus/topics.txt"
OUT_PATH = "ping-pongings/knowledge-base/topics_log.jsonl"
KEY = os.environ.get("GROQ_API_KEY", "")
MODEL = os.environ.get("BRAIN_MODEL", "").strip() or "openai/gpt-oss-120b"
MIN_INTERVAL = 2.5  # seconds between requests -- keeps us under typical 30 RPM caps


def ask(prompt):
    body = json.dumps(
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 400,
            "temperature": 0.3,
        }
    ).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def build_prompt(topic):
    return (
        f"Give a real, substantive, factually grounded explanation of: {topic}\n\n"
        "Write plainly. No invented frameworks, no fictional terminology, no "
        "'through the lens of' framing devices. If the topic is genuinely "
        "speculative or fringe, say so directly instead of writing around it. "
        "3-5 sentences, dense with real content."
    )


class DailyCapHit(Exception):
    pass


def ask_with_backoff(prompt):
    """Returns text, or raises DailyCapHit if Groq's error says per-day/token-quota."""
    attempts = 0
    while True:
        try:
            return ask(prompt)
        except urllib.error.HTTPError as e:
            body_txt = ""
            try:
                body_txt = e.read().decode("utf-8", "ignore")
            except Exception:
                pass
            if e.code != 429:
                raise
            lower = body_txt.lower()
            if "per day" in lower or "tpd" in lower or "daily" in lower:
                raise DailyCapHit(body_txt)
            attempts += 1
            if attempts > 5:
                raise DailyCapHit(f"gave up after 5 retries: {body_txt}")
            retry_after = e.headers.get("Retry-After")
            wait = float(retry_after) if retry_after else min(10 * attempts, 60)
            print(f"    rate limited (per-minute), backing off {wait:.0f}s (attempt {attempts})")
            time.sleep(wait)


def main():
    if not KEY:
        sys.exit("GROQ_API_KEY not set")
    if not os.path.exists(TOPICS_PATH):
        sys.exit(f"missing {TOPICS_PATH}")

    with open(TOPICS_PATH) as f:
        topics = [l.strip() for l in f if l.strip() and not l.lstrip().startswith("#")]

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    done_topics = set()
    if os.path.exists(OUT_PATH):
        with open(OUT_PATH) as f:
            for l in f:
                if l.strip():
                    try:
                        done_topics.add(json.loads(l)["topic"])
                    except Exception:
                        pass

    todo = [t for t in topics if t not in done_topics]
    print(f"{len(done_topics)} already researched, {len(todo)} remaining")

    completed_this_run = 0
    last_call = 0.0
    with open(OUT_PATH, "a") as out:
        for topic in todo:
            elapsed = time.time() - last_call
            if elapsed < MIN_INTERVAL:
                time.sleep(MIN_INTERVAL - elapsed)
            try:
                last_call = time.time()
                text = ask_with_backoff(build_prompt(topic))
                rec = {
                    "topic": topic,
                    "analysis": text.strip(),
                    "model": MODEL,
                    "researched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "source": "topic_research_pipeline",
                }
                out.write(json.dumps(rec) + "\n")
                out.flush()
                completed_this_run += 1
                print(f"  done: {topic[:70]}")
            except DailyCapHit as ex:
                print(f"Daily token cap hit after {completed_this_run} topics this run. "
                      f"{len(todo) - completed_this_run} remain -- re-run later, "
                      f"already-done topics will be skipped automatically. ({ex})")
                break
            except Exception as ex:
                print(f"  skip ({ex}): {topic[:60]}")

    print(f"Completed {completed_this_run} this run. "
          f"{len(done_topics) + completed_this_run}/{len(topics)} total done.")


if __name__ == "__main__":
    main()
