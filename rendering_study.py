#!/usr/bin/env python3
import json, os, time, requests
from datetime import datetime

HF_TOKEN = os.environ.get("HF_TOKEN", "")
HF_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL = "Qwen/Qwen2.5-72B-Instruct"
MEMORY_PATH = os.path.expanduser("~/barrot/memory.json")
CONTEXT_PATH = os.path.expanduser("~/barrot/rendering_context.json")
MAX_RETRIES = 3

NODES = [
    {"id":"R01","topic":"Rasterization vs Ray Tracing","category":"Foundations","prerequisites":[],"track":"software","music":"Rasterization = quantized waveform. Ray tracing = convolution reverb."},
    {"id":"R02","topic":"The Rendering Equation Kajiya 1986","category":"Foundations","prerequisites":["R01"],"track":"software","music":"Energy conservation in audio mixing. Light bounces = harmonic overtones."},
    {"id":"R03","topic":"Shaders Vertex Fragment and Compute","category":"Foundations","prerequisites":["R01"],"track":"gpu","music":"Vertex = pitch transform. Fragment = timbre color. Compute = DSP batch."},
    {"id":"R04","topic":"GPU Architecture and the Render Pipeline","category":"Foundations","prerequisites":["R03"],"track":"gpu","music":"GPU pipeline = parallel audio track processing. SIMD = chord voicing."},
    {"id":"R05","topic":"Z-Buffering and Depth Testing","category":"Foundations","prerequisites":["R01"],"track":"software","music":"Z-buffer = audio priority mixing. Depth test = sidechain compression."},
    {"id":"R06","topic":"glTF 2.0 and OBJ File Parsing","category":"Asset Pipeline","prerequisites":["R04"],"track":"software","music":"glTF = stem file format. Binary blobs = raw audio buffers."},
    {"id":"R07","topic":"Spatial Hierarchies and Scene Graphs","category":"Asset Pipeline","prerequisites":["R06"],"track":"software","music":"Scene graph = song arrangement. Parent-child = sends and returns."},
    {"id":"R08","topic":"Global Illumination","category":"Advanced","prerequisites":["R02","R05"],"track":"software","music":"Global illumination = room acoustics. Bounce = early reverb reflections."},
    {"id":"R09","topic":"Path Tracing","category":"Advanced","prerequisites":["R08"],"track":"software","music":"Path tracing = Monte Carlo noise floor. Convergence = de-noising with more samples."},
    {"id":"R10","topic":"Shadow Mapping","category":"Advanced","prerequisites":["R05","R08"],"track":"software","music":"Shadow map = audio masking. Penumbra = frequency overlap between sounds."},
    {"id":"R11","topic":"Ambient Occlusion","category":"Advanced","prerequisites":["R08"],"track":"gpu","music":"Ambient occlusion = sub-bass in tight spaces. Crevice = low-end buildup."},
    {"id":"R12","topic":"Vulkan Memory Allocator VMA","category":"GPU Systems","prerequisites":["R04"],"track":"gpu","music":"VMA = audio buffer pool. Suballocation = sample slicing and reuse."},
    {"id":"R13","topic":"Compute Shaders and Tiled Deferred Lighting","category":"GPU Systems","prerequisites":["R03","R12"],"track":"gpu","music":"Compute = parallel DSP. Tiled deferred = multiband compressor."},
    {"id":"R14","topic":"Deferred Rendering","category":"GPU Systems","prerequisites":["R13"],"track":"gpu","music":"G-buffer = stem separation. Deferred pass = mixing after all tracks recorded."},
    {"id":"R15","topic":"Temporal Anti-Aliasing TAA","category":"GPU Systems","prerequisites":["R14"],"track":"gpu","music":"TAA = audio smoothing across frames. Ghost artifacts = IIR filter pre-ringing."},
    {"id":"R16","topic":"Neural Rendering DLSS and FSR","category":"AI Rendering","prerequisites":["R15"],"track":"gpu","music":"DLSS = AI upsampling like iZotope RX restoration."},
    {"id":"R17","topic":"NeRF Neural Radiance Fields","category":"AI Rendering","prerequisites":["R09","R16"],"track":"gpu","music":"NeRF = reconstructing 3D audio from sparse mic captures."},
    {"id":"R18","topic":"Gaussian Splatting","category":"AI Rendering","prerequisites":["R17"],"track":"gpu","music":"Gaussian splatting = granular synthesis. Each splat = a grain."},
    {"id":"R19","topic":"Real-Time Ray Tracing with AI Denoising","category":"AI Rendering","prerequisites":["R09","R16"],"track":"gpu","music":"RT denoising = noise reduction on recorded audio."},
    {"id":"R20","topic":"Rendering for Music Visualization Spectral to Visual","category":"Music Visualization","prerequisites":["R14","R19"],"track":"bridge","music":"FFT spectrum to color. Bass = red. Mid = green. High = blue. BPM = frame rate."},
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
    with open(MEMORY_PATH,"w") as f:
        json.dump(memory,f,indent=2)

def topic_known(memory, topic):
    if isinstance(memory, dict):
        entries = memory.get("knowledge", [])
    else:
        entries = memory
    for e in entries:
        if isinstance(e, dict) and e.get("topic") == topic:
            return True
    return False

def get_entries(memory):
    if isinstance(memory, dict):
        return memory.get("knowledge", [])
    return memory

def ask(prompt):
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.post(HF_URL,
                headers={"Authorization":"Bearer "+HF_TOKEN,"Content-Type":"application/json"},
                json={"model":MODEL,"max_tokens":400,"messages":[{"role":"user","content":prompt}]},
                timeout=60)
            if r.status_code == 429:
                print(f"  Rate limit. Waiting 30s...")
                time.sleep(30)
                continue
            data = r.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(10)
    return None

def main():
    print("="*50)
    print("BARROT RENDERING CURRICULUM")
    print("20 nodes | MRP 5-level | Music mapped")
    print("="*50)

    if not HF_TOKEN:
        print("HF_TOKEN not set. Run: source ~/.bashrc")
        return

    memory = load_memory()
    context = {}
    completed = 0

    for i, node in enumerate(NODES):
        topic = node["topic"]
        print(f"\n[{i+1}/20] {node['id']}: {topic}")

        if topic_known(memory, topic):
            print("  Already known - skipping")
            continue

        for level in LEVELS:
            print(f"  {level}...", end=" ", flush=True)
            prompt = f"Analyze {topic} at {level} level using MRP. Music parallel: {node['music']}"
            result = ask(prompt)
            if result:
                memory.append({
                    "topic": topic,
                    "node_id": node["id"],
                    "category": node["category"],
                    "track": node["track"],
                    "level": level,
                    "content": result,
                    "music_mapping": node["music"],
                    "timestamp": datetime.utcnow().isoformat()
                })
                save_memory(memory)
                print("done")
            else:
                print("FAILED")
            time.sleep(5)

        context[node["id"]] = {"topic":topic,"done":datetime.utcnow().isoformat(),"music":node["music"]}
        with open(CONTEXT_PATH,"w") as f:
            json.dump(context,f,indent=2)
        completed += 1
        print(f"  Node complete. Total entries: {len(memory)}")
        time.sleep(3)

    print("\n"+"="*50)
    print(f"COMPLETE. Nodes: {completed} | Entries: {len(memory)}")
    print("="*50)

if __name__ == "__main__":
    main()
