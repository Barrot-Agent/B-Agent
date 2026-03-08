import json,os,requests,subprocess
from datetime import datetime
from pathlib import Path
M=Path.home()/"barrot"/"memory.json"
T=os.environ.get("GITHUB_TOKEN","").strip()
def lm():
 if M.exists():
  return json.load(open(M))
 return {"knowledge":[],"sessions":0}
def sm(m):
 json.dump(m,open(M,"w"),indent=2)
def ask(p):
 r=requests.post("https://models.inference.ai.azure.com/chat/completions",headers={"Authorization":"Bearer "+T,"content-type":"application/json"},json={"model":"gpt-4o-mini","messages":[{"role":"user","content":p}],"max_tokens":1024})
 return r.json()["choices"][0]["message"]["content"]
def push():
 try:
  subprocess.run(["git","add","memory.json"],cwd=Path.home()/"barrot")
  subprocess.run(["git","commit","-m","Barrot memory update"],cwd=Path.home()/"barrot")
  subprocess.run(["git","push","origin","main"],cwd=Path.home()/"barrot")
  print("Memory pushed to GitHub.")
 except:
  print("Git push failed - memory saved locally.")
def think(t):
 m=lm()
 m["sessions"]+=1
 r=ask("Analyze: "+t+"\n1. Top 3 insights\n2. Next learning step")
 print(r)
 m["knowledge"].append({"timestamp":str(datetime.now()),"topic":t,"insight":r[:200],"session":m["sessions"]})
 sm(m)
 push()
 print(f"Memory: {len(m['knowledge'])} entries saved.")
print("BARROT v1.0 - ALIVE")
think(input("Learn about: "))
