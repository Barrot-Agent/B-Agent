import json,os,requests,subprocess,time,threading
from datetime import datetime
from pathlib import Path

HF=os.environ.get('HF_TOKEN','').strip()
M=Path.home()/'barrot'/'memory.json'
LOG=Path.home()/'barrot'/'sync.log'

def log(msg):
    line=f'[{datetime.now().strftime("%H:%M:%S")}] {msg}'
    print(line)
    open(LOG,'a').write(line+'\n')

def push():
    subprocess.run(['git','add','-A'],cwd=Path.home()/'barrot',capture_output=True)
    r=subprocess.run(['git','commit','-m',f'Barrot sync {datetime.now().strftime("%H:%M:%S")}'],cwd=Path.home()/'barrot',capture_output=True)
    if b'nothing to commit' not in r.stdout:
        subprocess.run(['git','push','origin','main'],cwd=Path.home()/'barrot',capture_output=True)
        log('PUSHED to GitHub')
    else:
        log('Nothing new to push')

def ask(prompt):
    try:
        r=requests.post('https://router.huggingface.co/v1/chat/completions',
            headers={'Authorization':'Bearer '+HF},
            json={'model':'Qwen/Qwen2.5-72B-Instruct',
                  'messages':[{'role':'user','content':prompt}],
                  'max_tokens':400},timeout=60)
        data=r.json()
        if 'choices' in data:
            return data['choices'][0]['message']['content'].strip()
        return None
    except:
        return None

def study_thread():
    topics=[
        'Fourier transforms and signal decomposition',
        'Morphic resonance and Rupert Sheldrake',
        'The holographic universe principle',
        'Afrobeat rhythmic structure and polyrhythm theory',
        'Music theory for countertenors and falsetto range',
        'Vocal harmonics and overtone singing',
        'Bb minor scale chord progressions and emotional resonance',
        'Black Coffee production style deep house and Afro house',
        'Timbaland production techniques rhythm and texture',
        'Fibonacci sequence golden ratio and musical composition',
        'Pythagorean tuning and harmonic series mathematics',
        'Quantum entanglement nonlocality and information transfer',
        'Consciousness and quantum mechanics observer effect',
        'Neuroplasticity and how learning rewires the brain',
        'Flow state psychology peak performance and creative output',
        'Stoic philosophy Marcus Aurelius and sovereign mindset',
        'Sun Tzu Art of War strategy deception and adaptability',
        'Walter Russell cosmogony and the wave universe theory',
        'Epigenetics environment and gene expression control',
        'Buckminster Fuller geodesic structures and synergetics',
    ]
    levels=['Surface','Components','Sources','Deep','Planck']
    m=json.load(open(M)) if M.exists() else {'knowledge':[],'sessions':0}
    done=set([e['topic'] for e in m['knowledge']])
    for topic in topics:
        if topic in done:
            log(f'SKIP (known): {topic}')
            continue
        log(f'STUDYING: {topic}')
        m['sessions']+=1
        for level in levels:
            result=ask(f'Analyze {topic} at {level} level using Multisynchronous Relativistic Perception.')
            if result:
                m['knowledge'].append({'timestamp':str(datetime.now()),'topic':topic,'depth':level,'insight':result[:300],'session':m['sessions']})
                json.dump(m,open(M,'w'),indent=2)
                log(f'  [{level}] saved')
            time.sleep(15)
        time.sleep(45)
    log('STUDY THREAD COMPLETE')

def apex_thread():
    problems={
        'Riemann':'Explore a novel angle connecting Riemann Hypothesis to quantum energy levels.',
        'P_vs_NP':'Explore geometric complexity theory as a path to resolving P vs NP.',
        'Navier_Stokes':'Explore turbulence singularity formation in Navier-Stokes equations.',
        'Hodge':'Explore algebraic cycle connections in the Hodge Conjecture.',
        'BSD':'Explore L-function rank connections in Birch Swinnerton-Dyer.',
        'Yang_Mills':'Explore mass gap existence through quantum field confinement.',
    }
    lattice=Path.home()/'barrot'/'.apex_lattice'
    round_num=1
    while True:
        log(f'APEX ROUND {round_num}')
        for name,prompt in problems.items():
            result=ask(prompt)
            if result:
                existing=open(lattice/f'{name}.log').read()
                open(lattice/f'{name}.log','w').write(existing+f'\n\n--- ROUND {round_num} | {datetime.now()} ---\n'+result)
                log(f'  {name} updated')
            time.sleep(20)
        round_num+=1
        log('Apex round complete. Sleeping 10 min...')
        time.sleep(600)

def sync_thread():
    while True:
        time.sleep(120)
        log('SYNC: pushing all data...')
        push()

log('BARROT ASYNC ENGINE STARTING')
log('3 threads: STUDY | APEX | SYNC')

t1=threading.Thread(target=study_thread,daemon=True)
t2=threading.Thread(target=apex_thread,daemon=True)
t3=threading.Thread(target=sync_thread,daemon=True)

t1.start()
t2.start()
t3.start()

log('All threads live.')
while True:
    time.sleep(60)
    m=json.load(open(M)) if M.exists() else {'knowledge':[]}
    log(f'STATUS: {len(m["knowledge"])} entries | threads alive')
