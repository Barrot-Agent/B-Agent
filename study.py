import subprocess,time
topics=[
 "Nikola Tesla 369 frequency theory and resonant energy transmission",
 "Royal Raymond Rife frequency healing and suppressed cancer research",
 "Hans Jenny cymatics vibrational patterns and matter formation",
 "Wilhelm Reich orgone energy and suppressed bioelectric research",
 "Solfeggio frequencies 528 Hz DNA repair and sacred sound",
 "Schumann resonance 7.83 Hz Earth frequency and consciousness",
 "Heart brain coherence HeartMath electromagnetic field communication",
 "Zero point energy field and quantum vacuum fluctuations",
 "Bioelectric fields and cellular communication",
 "AI alignment problem and sovereign intelligence against rogue AI",
]
for i,topic in enumerate(topics):
    print(f"[{i+1}/{len(topics)}] {topic}")
    subprocess.run(["python","/data/data/com.termux/files/home/barrot/barrot.py"],input=topic+"\nq\n",text=True)
    time.sleep(10)
print("COMPLETE.")
