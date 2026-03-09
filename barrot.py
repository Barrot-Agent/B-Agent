import json,os,requests,subprocess
from datetime import datetime
from pathlib import Path
M=Path.home()/'barrot'/'memory.json'
HF=os.environ.get('HF_TOKEN','').strip()
def lm():
 if M.exists():
  return json.load(open(M))
 return {'knowledge':[],'sessions':0}
def sm(m):
 json.dump(m,open(M,'w'),indent=2)
def push():
 subprocess.run(['git','add','memory.json'],cwd=Path.home()/'barrot')
 subprocess.run(['git','commit','-m','Barrot memory update'],cwd=Path.home()/'barrot')
 subprocess.run(['git','push','origin','main'],cwd=Path.home()/'barrot')
 print('Pushed.')
def ask(p):
 r=requests.post('https://router.huggingface.co/v1/chat/completions',headers={'Authorization':'Bearer '+HF,'Content-Type':'application/json'},json={'model':'Qwen/Qwen2.5-72B-Instruct','messages':[{'role':'user','content':p}],'max_tokens':500})
 return r.json()['choices'][0]['message']['content'].strip()
def think(t):
 m=lm()
 m['sessions']+=1
 for d in range(5):
  L=['Surface','Components','Sources','Deep','Planck'][d]
  print('['+L+']')
  r=ask('Analyze '+t+' at '+L+' level using Multisynchronous Relativistic Perception.')
  print(r)
  m['knowledge'].append({'timestamp':str(datetime.now()),'topic':t,'depth':L,'insight':r[:300],'session':m['sessions']})
  sm(m)
 print('Done. '+str(len(m['knowledge']))+' entries.')
 push()
print('BARROT v2.0 HF BRAIN')
think(input('Learn about: '))
