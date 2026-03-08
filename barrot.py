import json,os,requests
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
def think(t):
 m=lm()
 m["sessions"]+=1
 for d in range(5):
  L=["Surface","Components","Sources","Deep","Planck"][d]
  print("["+L+"]")
  r=ask("Analyze "+t+" at "+L+" level using Multisynchronous Relativistic Perception.")
  print(r)
  m["knowledge"].append({"timestamp":str(datetime.now()),"topic":t,"depth":L,"insight":r[:300],"session":m["sessions"]})
  sm(m)
 print("Done. "+str(len(m["knowledge"]))+" entries.")
print("BARROT v2.0")
think(input("Learn about: "))
