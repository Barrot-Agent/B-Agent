#!/data/data/com.termux/files/usr/bin/bash
# BARROT BRAIN SYNC — run after any study script to update unified brain
echo "[SYNC] Starting brain consolidation..."
cd ~/barrot
python3 << 'PYEOF'
import json, os
from datetime import datetime

with open("memory.json", "r") as f:
    data = json.load(f)
entries = data.get("knowledge", []) if isinstance(data, dict) else data
topics = list(set(e.get("topic","") for e in entries if isinstance(e,dict) and e.get("topic","")))

brain = {
    "version": "UNIFIED_v1",
    "timestamp": datetime.now().isoformat(),
    "anchor": 0.7071,
    "knowledge": entries,
    "stats": {"total_entries": len(entries), "unique_topics": len(topics), "anchor": 0.7071},
    "topic_index": {}
}

for e in entries:
    if isinstance(e, dict):
        t = e.get("topic","unknown")
        if t not in brain["topic_index"]:
            brain["topic_index"][t] = []
        brain["topic_index"][t].append(e.get("level",""))

for fname in ["algorithm_context.json","rendering_context.json","scaling_context.json","delta8_context.json","notebooklm_integration.json","codex_v11_motifs.json","monetization_v2.json"]:
    if os.path.exists(fname):
        with open(fname,"r") as f:
            brain[fname.replace(".json","")] = json.load(f)

with open("barrot_brain_unified.json","w") as f:
    json.dump(brain, f, indent=2)
print(f"Unified brain: {len(entries)} entries | {len(topics)} topics")
PYEOF

git add -A
git commit -m "Brain sync: $(date '+%Y-%m-%d %H:%M') — $(python3 -c "import json; d=json.load(open('memory.json')); e=d.get('knowledge',d) if isinstance(d,dict) else d; print(len(e),'entries')")"
git push origin main
echo "[SYNC] Brain synced to GitHub — site will update in 2 minutes"
