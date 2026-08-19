#!/usr/bin/env python3
"""
BARROT-Ω FREE IMAGE GENERATION — via Hugging Face's ZeroGPU-backed
black-forest-labs/FLUX.1-dev Space. Genuinely free, no API key beyond
your normal HF token, no per-generation cost - the tradeoff is a shared
GPU queue (may wait) and a daily GPU-time cap.

Deliberately avoids the `gradio_client` library - it pulls in
`huggingface_hub`, which cannot be pip installed on this hardware
(compiling a transitive dependency SIGKILLs from OOM). This talks to the
Space's underlying Gradio HTTP API directly with plain urllib instead -
zero heavy dependencies, matches every other script in this project.

Gradio's queue API (used for GPU-backed / generator functions):
  1. POST /call/<api_name>  {"data": [...]}  -> {"event_id": "..."}
  2. GET  /call/<api_name>/<event_id>  -> Server-Sent Events stream,
     one "event: complete" (or similar) message per yield from the
     underlying function. FLUX.1-dev's `infer()` yields multiple times
     (intermediate previews during diffusion) - the LAST event is the
     final, full-quality image.

api_name is inferred as "infer" from the function name in app.py
(confirmed by reading the Space's real source), since no explicit
api_name was set - Gradio's documented default naming behavior. Verify
via the printed response in this script's first real run; if it 404s,
the actual api_name will need confirming another way.
"""

import json
import os
import sys
import time
import urllib.request

SPACE_BASE = "https://black-forest-labs-flux-1-dev.hf.space"
API_NAME = "infer"
HF_TOKEN = os.environ.get("HF_TOKEN", "")

PROMPT = (
    os.environ.get("IMAGE_PROMPT", "").strip()
    or "a simple test image, red circle on white background"
)
OUT_DIR = "generated_images"


def call_gradio(
    prompt, seed=0, randomize_seed=True, width=1024, height=1024, guidance_scale=3.5, steps=28
):
    headers = {"Content-Type": "application/json"}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"

    body = json.dumps(
        {"data": [prompt, seed, randomize_seed, width, height, guidance_scale, steps]}
    ).encode()

    req = urllib.request.Request(
        f"{SPACE_BASE}/gradio_api/call/{API_NAME}", data=body, headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        submit_resp = json.load(r)
    event_id = submit_resp.get("event_id")
    if not event_id:
        raise RuntimeError(f"No event_id in submit response: {submit_resp}")
    print(f"Submitted. event_id={event_id}")

    # Poll the SSE stream for results - take the LAST complete event
    result_req = urllib.request.Request(
        f"{SPACE_BASE}/gradio_api/call/{API_NAME}/{event_id}",
        headers={"Authorization": headers.get("Authorization", "")} if HF_TOKEN else {},
    )
    last_data = None
    current_event = None
    with urllib.request.urlopen(result_req, timeout=180) as r:
        for raw_line in r:
            line = raw_line.decode("utf-8", errors="ignore").strip()
            if line.startswith("event:"):
                current_event = line[len("event:") :].strip()
                continue
            if not line.startswith("data:"):
                continue
            payload = line[len("data:") :].strip()
            if payload in ("", "[DONE]", "null"):
                continue
            try:
                parsed = json.loads(payload)
            except json.JSONDecodeError:
                continue
            if current_event == "generating":
                print("  ...intermediate preview received")
            elif current_event == "complete":
                print("  final image received")
                last_data = parsed
                break

    if not last_data:
        raise RuntimeError(
            "No 'complete' event received from SSE stream - generation may have failed or timed out"
        )
    return last_data


def main():
    if not HF_TOKEN:
        print(
            "Warning: HF_TOKEN not set - proceeding unauthenticated, "
            "may fail if the model requires accepting its license first."
        )

    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Prompt: {PROMPT}")

    result = call_gradio(PROMPT)
    image_info, seed_used = result[0], result[1]
    image_url = image_info["url"]
    print(f"Image URL: {image_url}")
    print(f"Seed used: {seed_used}")

    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    dest = os.path.join(OUT_DIR, f"image_{ts}.webp")
    req = urllib.request.Request(image_url)
    with urllib.request.urlopen(req, timeout=60) as r:
        with open(dest, "wb") as f:
            f.write(r.read())
    print(f"Downloaded to {dest}")


if __name__ == "__main__":
    main()
