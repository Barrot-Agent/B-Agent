#!/usr/bin/env python3
"""Generate Stupid Sindy scripts and renderer-ready episode manifests."""

import argparse
import json
import os
import urllib.request
from pathlib import Path

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")

SERIES_CONTEXT = """Stupid Sindy series. 10 episodes. Recurring characters: Sindy
(protagonist), Alex (coworker, sarcastic), Jordan (roommate, chaotic), Marcus
(love interest, oblivious). Each episode: monologue + ensemble scene. Callbacks
required. Voice: "Too Much, On Purpose."""


def parse_script_response(response):
    """Parse JSON returned plainly or in a Markdown code fence."""
    if not response:
        return None
    candidate = response.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        candidate = "\n".join(lines[1:]).rsplit("```", 1)[0].strip()
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        start, end = candidate.find("{"), candidate.rfind("}") + 1
        if start < 0 or end <= start:
            return None
        try:
            return json.loads(candidate[start:end])
        except json.JSONDecodeError:
            return None


def build_episode_manifest(ep_num, premise, script, asset_urls=()):
    """Create a portable manifest for a downstream asset/animation renderer."""
    return {
        "series": "Stupid Sindy",
        "episode": ep_num,
        "premise": premise,
        "script": script,
        "assets": [{"url": url, "status": "pending_review"} for url in asset_urls],
        "render": {
            "target": "offline",
            "quality": "cinematic",
            "resolution": "1080p",
            "fps": 24,
            "output_format": "mp4",
        },
        "provenance": {
            "source": "barrot_sindy_series_generator",
            "requires_asset_license_review": bool(asset_urls),
        },
    }


def call_groq(prompt):
    if not GROQ_KEY:
        raise RuntimeError("GROQ_API_KEY is required to generate scripts")
    body = json.dumps(
        {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {"role": "system", "content": SERIES_CONTEXT},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 2000,
            "temperature": 0.9,
        }
    ).encode()
    request = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={
            "Authorization": "Bearer " + GROQ_KEY,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return json.load(response)["choices"][0]["message"]["content"]
    except OSError as exc:
        print(f"Groq error: {exc}")
        return None


def generate_series(num_episodes=10, output_dir="episodes", asset_urls=()):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    premises = [
        "Sindy's first day at the office, meets Alex",
        "Apartment roommate Jordan throws a party",
        "Sindy runs into Marcus at a coffee shop",
        "Office disaster during a client presentation",
        "Roommate drama escalates",
        "Sindy's family Thanksgiving via video call",
        "Office Christmas party goes wrong",
        "Marcus admits feelings (awkwardly)",
        "Alex's ex shows up at work",
        "Season finale: Sindy's birthday party with everyone",
    ]

    for ep_num in range(1, num_episodes + 1):
        premise = premises[ep_num - 1] if ep_num <= len(premises) else f"Episode {ep_num}"
        try:
            response = call_groq(f"Episode {ep_num}: {premise}\nGenerate full script.")
        except RuntimeError as exc:
            print(f"✗ Episode {ep_num}: {exc}")
            continue
        script = parse_script_response(response)
        if script is None:
            print(f"✗ Episode {ep_num} parse error")
            continue

        episode_dir = output_path / f"episode-{ep_num:02d}"
        episode_dir.mkdir(parents=True, exist_ok=True)
        (episode_dir / "script.json").write_text(
            json.dumps(script, indent=2) + "\n", encoding="utf-8"
        )
        (episode_dir / "production-manifest.json").write_text(
            json.dumps(build_episode_manifest(ep_num, premise, script, asset_urls), indent=2)
            + "\n",
            encoding="utf-8",
        )
        print(f"✓ Episode {ep_num}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episodes", type=int, default=10)
    parser.add_argument("--output-dir", default="episodes")
    parser.add_argument("--asset-url", action="append", default=[], help="Reviewed asset URL")
    args = parser.parse_args()
    generate_series(args.episodes, args.output_dir, args.asset_url)
