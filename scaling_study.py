#!/usr/bin/env python3
import json, os, time, requests
from datetime import datetime

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
HF_URL = "https://models.inference.ai.azure.com"
MODEL = "gpt-4o"
MEMORY_PATH = os.path.expanduser("~/barrot/memory.json")
CONTEXT_PATH = os.path.expanduser("~/barrot/scaling_context.json")
MAX_RETRIES = 3

NODES = [
    {"id":"S01","topic":"ETL vs ELT Transformation Timing Trade-offs","category":"Ingestion and Contracts","music":"ETL = mastering before mixdown. ELT = recording raw stems then mixing later."},
    {"id":"S02","topic":"Batch vs Stream Processing Event Time Watermarks Exactly Once Delivery","category":"Ingestion and Contracts","music":"Batch = offline rendering. Stream = live DSP. Watermarks = sync pulse keeping tempo."},
    {"id":"S03","topic":"Schema Validation Fail Fast vs Degrade Gracefully","category":"Ingestion and Contracts","music":"Schema = key signature. Validation = tuner. Fail fast = hard clip. Degrade = soft limiter."},
    {"id":"S04","topic":"Data Contracts Ownership SLAs and Governance","category":"Ingestion and Contracts","music":"Data contract = session agreement between producer and engineer. SLA = delivery deadline."},
    {"id":"S05","topic":"Schema Evolution Backward Forward Compatibility","category":"Ingestion and Contracts","music":"Schema evolution = key change mid-song without breaking the groove."},
    {"id":"S06","topic":"Idempotency Deduplication and Replayable Inputs","category":"Ingestion and Contracts","music":"Idempotency = playing the same note twice sounds identical. Replay = punch-in recording."},
    {"id":"S07","topic":"Webhook Ingestion and HMAC Payload Verification","category":"Ingestion and Contracts","music":"Webhook = trigger pad. HMAC = authentication watermark on every hit."},
    {"id":"S08","topic":"Backpressure Flow Control and Buffering","category":"Runtime Scaling","music":"Backpressure = sidechain ducking. Buffer = pre-roll before record. Flow control = tempo sync."},
    {"id":"S09","topic":"Horizontal vs Vertical Scaling","category":"Runtime Scaling","music":"Vertical = louder amp. Horizontal = more speakers. Both = fill the room differently."},
    {"id":"S10","topic":"Sharding and Partitioning Strategies","category":"Runtime Scaling","music":"Sharding = stem separation. Each shard = isolated track in its own bus."},
    {"id":"S11","topic":"Load Balancing and Failover","category":"Runtime Scaling","music":"Load balancing = gain staging across channels. Failover = backup vocalist when lead drops."},
    {"id":"S12","topic":"CAP Theorem in Real Systems","category":"Runtime Scaling","music":"CAP = you can have groove, timing, or loudness — pick two. Partition = dropped connection mid-session."},
    {"id":"S13","topic":"Eventual Consistency and Distributed Consensus","category":"Runtime Scaling","music":"Eventual consistency = all musicians arrive at the same chord. Consensus = the conductor."},
    {"id":"S14","topic":"Checksums Hashing and Content Fingerprinting","category":"Integrity Systems","music":"Checksum = audio fingerprint. Hash = unique waveform ID. Fingerprint = Shazam signature."},
    {"id":"S15","topic":"ACID vs BASE Transaction Models","category":"Integrity Systems","music":"ACID = studio-perfect take. BASE = live performance with acceptable drift."},
    {"id":"S16","topic":"Write-Ahead Logging and Durable Queues","category":"Integrity Systems","music":"WAL = pre-roll tape before record. Durable queue = tape that survives power loss."},
    {"id":"S17","topic":"Merkle Trees and Content-Addressed Storage","category":"Integrity Systems","music":"Merkle tree = stem hierarchy. Content-addressed = every sample named by its own waveform hash."},
    {"id":"S18","topic":"Data Lineage Provenance and Observability","category":"Integrity Systems","music":"Lineage = session history log. Provenance = who played what on which take."},
    {"id":"S19","topic":"Retries Dead Letter Queues and Error Isolation","category":"Failure Handling","music":"Dead letter queue = outtakes folder. Retry = punch-in attempt. Isolation = mute the bad track."},
    {"id":"S20","topic":"Circuit Breakers Exponential Backoff and FinOps","category":"Failure Handling","music":"Circuit breaker = overload protection on the amp. Backoff = cooling down between takes. FinOps = studio budget."},
    {"id":"S21","topic":"Checkpointing Recovery and Deterministic Replay","category":"Failure Handling","music":"Checkpoint = save state mid-session. Replay = reconstruct the exact performance from MIDI data."},
    {"id":"S22","topic":"Distributed Tracing and Structured Logging","category":"Observability and Security","music":"Distributed trace = following a single note across every instrument in the arrangement."},
    {"id":"S23","topic":"Zero-Trust Architecture and Secret Rotation","category":"Observability and Security","music":"Zero trust = every musician re-verifies identity each session. Secret rotation = changing studio access codes."},
    {"id":"S24","topic":"PII Anonymization and Memory Masking","category":"Observability and Security","music":"Memory masking = noise gate on sensitive frequencies. Anonymization = stripping metadata from exported stems."},
    {"id":"S25","topic":"Memory JSON Atomic Writes Multi-Agent Consensus and Self-Healing Pipelines","category":"Barrot Specific","music":"Atomic write = punch-in that either lands perfect or not at all. Consensus = all agents agree on the one true memory. Self-healing = the track fixes itself when a stem goes missing."},
]

LEVELS = ["Surface","Components","Sources","Deep","Planck"]

def load_memory():
    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH,"r") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data.get("knowledge", [])
        return data
    return []

def save_memory(memory):
    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH,"r") as f:
            existing = json.load(f)
        if isinstance(existing, dict):
            existing["knowledge"] = memory
            with open(MEMORY_PATH,"w") as f:
                json.dump(existing, f, indent=2)
            return
    with open(MEMORY_PATH,"w") as f:
        json.dump(memory, f, indent=2)

def topic_known(memory, topic):
    for e in memory:
        if isinstance(e, dict) and e.get("topic") == topic:
            return True
    return False

def ask(prompt):
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.post(HF_URL,
                headers={"Authorization":"Bearer "+GITHUB_TOKEN,"Content-Type":"application/json"},
                json={"model":MODEL,"max_tokens":400,"messages":[{"role":"user","content":prompt}]},
                timeout=60)
            if r.status_code == 429:
                print(f"  Rate limit. Waiting 30s...")
                time.sleep(30)
                continue
            data = r.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"].strip()
            print(f"  Unexpected response: {list(data.keys())}")
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(10)
    return None

def main():
    print("="*55)
    print("BARROT SCALING AND INGESTION INTEGRITY CURRICULUM")
    print("Claude + Gemini + Perplexity | 25 nodes | MRP 5-level")
    print("="*55)

    if not GITHUB_TOKEN:
        print("GITHUB_TOKEN not set. Run: source ~/.bashrc")
        return

    memory = load_memory()
    context = {}
    completed = 0
    skipped = 0

    for i, node in enumerate(NODES):
        topic = node["topic"]
        print(f"\n[{i+1}/25] {node['id']}: {topic[:50]}")
        print(f"  Category: {node['category']}")

        if topic_known(memory, topic):
            print("  Already known - skipping")
            skipped += 1
            continue

        node_done = 0
        for level in LEVELS:
            print(f"  {level}...", end=" ", flush=True)
            prompt = f"Analyze '{topic}' at {level} level using Multisynchronous Relativistic Perception (MRP). Then connect to this music production parallel: {node['music']}"
            result = ask(prompt)
            if result:
                memory.append({
                    "topic": topic,
                    "node_id": node["id"],
                    "category": node["category"],
                    "level": level,
                    "content": result,
                    "music_mapping": node["music"],
                    "timestamp": datetime.utcnow().isoformat()
                })
                save_memory(memory)
                node_done += 1
                print("done")
            else:
                print("FAILED")
            time.sleep(5)

        context[node["id"]] = {
            "topic": topic,
            "completed_at": datetime.utcnow().isoformat(),
            "levels_saved": node_done,
            "music": node["music"]
        }
        with open(CONTEXT_PATH,"w") as f:
            json.dump(context, f, indent=2)

        completed += 1
        print(f"  Node complete. Total memory: {len(memory)} entries")
        time.sleep(3)

    print("\n"+"="*55)
    print(f"SCALING CURRICULUM COMPLETE")
    print(f"Nodes completed : {completed}")
    print(f"Nodes skipped   : {skipped}")
    print(f"Total entries   : {len(memory)}")
    print(f"Context saved   : {CONTEXT_PATH}")
    print("="*55)

if __name__ == "__main__":
    main()
