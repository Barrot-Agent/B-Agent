#!/usr/bin/env python3
"""Generate full Stupid Sindy series: 10 episodes, consistent characters, callbacks."""
import os, json, urllib.request

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")

SERIES_CONTEXT = """Stupid Sindy series. 10 episodes. Recurring characters: Sindy (protagonist), Alex (coworker, sarcastic), Jordan (roommate, chaotic), Marcus (love interest, oblivious).
Each episode: monologue + ensemble scene. Callbacks required. Voice: "Too Much, On Purpose."""

def call_groq(prompt):
    body = json.dumps({"model": "openai/gpt-oss-120b", "messages": [{"role": "system", "content": SERIES_CONTEXT}, {"role": "user", "content": prompt}], "max_tokens": 2000, "temperature": 0.9}).encode()
    req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=body, headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.load(resp)["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq error: {e}")
        return None

def generate_series(num_episodes=10):
    os.makedirs("episodes", exist_ok=True)
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
        prompt = f"Episode {ep_num}: {premise}\nGenerate full script."
        response = call_groq(prompt)
        
        if response:
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                script = json.loads(response[start:end])
                ep_dir = f"episodes/episode-{ep_num:02d}"
                os.makedirs(ep_dir, exist_ok=True)
                with open(f"{ep_dir}/script.json", "w") as f:
                    json.dump(script, f, indent=2)
                print(f"✓ Episode {ep_num}")
            except:
                print(f"✗ Episode {ep_num} parse error")

if __name__ == "__main__":
    generate_series(10)
