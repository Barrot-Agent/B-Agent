#!/usr/bin/env python3
"""
BARROT-Ω AUDIO INGESTION — real transcription of video/podcast/interview audio.
yt-dlp pulls audio -> Groq whisper-large-v3 transcribes -> entry appended to the
knowledge base -> existing knowledge_distill.py distills it like any other source.
Honest: a failed fetch or transcription is reported, never invented.
"""
import json, os, subprocess, sys, uuid
from datetime import datetime, timezone

KEY = os.environ.get("GROQ_API_KEY", "")
KB = "ping-pongings/knowledge-base/log.jsonl"
CFG = "ping-pongings/knowledge-base/config.json"
MAX_MB = 24

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr

def fetch_audio(url, out_base):
    cmd = (f'yt-dlp -x --audio-format mp3 --audio-quality 9 '
           f'--postprocessor-args "-ac 1 -ar 16000 -b:a 48k" '
           f'-o "{out_base}.%(ext)s" --no-playlist '
           f'--print-to-file "%(title)s" "{out_base}.title" "{url}"')
    code, out, err = run(cmd)
    path = f"{out_base}.mp3"
    if code != 0 or not os.path.exists(path):
        raise RuntimeError(f"yt-dlp failed: {err[:300]}")
    title = url
    if os.path.exists(f"{out_base}.title"):
        title = open(f"{out_base}.title").read().strip() or url
    mb = os.path.getsize(path) / 1e6
    return path, title, mb

def transcribe_chunked(path):
    """Split into 10-min chunks so any length fits the whisper size limit."""
    import glob
    d = os.path.dirname(path) or "."
    stem = os.path.join(d, "chunk_" + os.path.basename(path).replace(".mp3", ""))
    code, out, err = run(f'ffmpeg -hide_banner -loglevel error -i "{path}" '
                         f'-f segment -segment_time 600 -c copy "{stem}_%03d.mp3"')
    chunks = sorted(glob.glob(f"{stem}_*.mp3"))
    if not chunks:
        chunks = [path]
    texts = []
    for i, c in enumerate(chunks):
        cmb = os.path.getsize(c) / 1e6
        if cmb > MAX_MB:
            print(f"  chunk {i+1} {cmb:.1f}MB too large, skipped")
            continue
        try:
            texts.append(transcribe(c))
            print(f"  chunk {i+1}/{len(chunks)} ({cmb:.1f}MB) transcribed")
        except Exception as e:
            print(f"  chunk {i+1} failed: {str(e)[:100]}")
        finally:
            if c != path and os.path.exists(c):
                os.remove(c)
    if not texts:
        raise RuntimeError("all chunks failed to transcribe")
    return " ".join(texts)


def transcribe(path):
    code, out, err = run(
        f'curl -s -X POST https://api.groq.com/openai/v1/audio/transcriptions '
        f'-H "Authorization: Bearer {KEY}" '
        f'-F "file=@{path}" -F "model=whisper-large-v3" -F "response_format=json"')
    if code != 0:
        raise RuntimeError(f"curl failed: {err[:200]}")
    try:
        data = json.loads(out)
    except Exception:
        raise RuntimeError(f"non-JSON from whisper: {out[:200]}")
    if "text" not in data:
        raise RuntimeError(f"whisper error: {json.dumps(data)[:300]}")
    return data["text"].strip()

def already_have(url):
    if not os.path.exists(KB):
        return False
    with open(KB) as f:
        for line in f:
            try:
                if json.loads(line).get("url") == url:
                    return True
            except Exception:
                pass
    return False

def append_entry(url, title, text, mb):
    os.makedirs(os.path.dirname(KB), exist_ok=True)
    entry = {
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "source": "video_audio",
        "title": title[:300],
        "url": url,
        "published": "",
        "summary": text[:4000],
        "transcript_chars": len(text),
        "audio_mb": round(mb, 2),
    }
    with open(KB, "a") as f:
        f.write(json.dumps(entry) + "\n")
    if os.path.exists(CFG):
        try:
            cfg = json.load(open(CFG))
            src = cfg.setdefault("sources", {}).setdefault("video_audio", {"enabled": True, "entries_ingested": 0})
            src["entries_ingested"] = src.get("entries_ingested", 0) + 1
            cfg["last_updated"] = datetime.now(timezone.utc).isoformat()
            json.dump(cfg, open(CFG, "w"), indent=2)
        except Exception as e:
            print(f"config update skipped: {e}")
    return entry

def main():
    urls = [u.strip() for u in os.environ.get("AUDIO_URLS", "").split(",") if u.strip()]
    if not urls:
        sys.exit("AUDIO_URLS not set (comma-separated)")
    if not KEY:
        sys.exit("GROQ_API_KEY not set")
    done = 0
    for url in urls:
        if already_have(url):
            print(f"skip (already ingested): {url}")
            continue
        base = f"/tmp/audio_{uuid.uuid4().hex[:8]}"
        try:
            path, title, mb = fetch_audio(url, base)
            print(f"fetched {mb:.1f}MB: {title[:70]}")
            text = transcribe_chunked(path)
            print(f"transcribed {len(text)} chars")
            append_entry(url, title, text, mb)
            done += 1
            print(f"INGESTED: {title[:70]}")
        except Exception as e:
            print(f"FAILED {url}: {e}")
        finally:
            for ext in (".mp3", ".title"):
                p = base + ext
                if os.path.exists(p):
                    os.remove(p)
    print(f"\n{done}/{len(urls)} audio sources ingested.")

if __name__ == "__main__":
    main()
