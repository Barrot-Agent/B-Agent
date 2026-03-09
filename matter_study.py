import requests,os,json,time
from datetime import datetime
from pathlib import Path

HF=os.environ.get('HF_TOKEN','').strip()
M=Path.home()/'barrot'/'memory.json'

def ask(prompt):
    for attempt in range(3):
        try:
            r=requests.post('https://router.huggingface.co/v1/chat/completions',
                headers={'Authorization':'Bearer '+HF},
                json={'model':'Qwen/Qwen2.5-72B-Instruct',
                      'messages':[{'role':'user','content':prompt}],
                      'max_tokens':400},timeout=60)
            data=r.json()
            if 'choices' in data:
                return data['choices'][0]['message']['content'].strip()
            print(f'Retry {attempt+1}...')
            time.sleep(30)
        except Exception as e:
            print(f'Error: {e}')
            time.sleep(30)
    return None

topics=[
    'Solid state matter crystalline and amorphous structures',
    'Liquid state matter fluid dynamics and molecular bonding',
    'Gas state matter kinetic theory and thermodynamics',
    'Plasma fourth state of matter and electromagnetic properties',
    'Bose-Einstein condensate fifth state of matter and quantum coherence',
    'Fermionic condensate and quantum degenerate matter',
    'Dark matter gravitational effects and detection attempts',
    'Dark energy accelerating universe expansion and quantum vacuum',
    'Antimatter production annihilation and asymmetry problem',
    'Exotic matter negative mass and wormhole physics',
    'Quark-gluon plasma conditions after the Big Bang',
    'Strange matter quark stars and stability hypothesis',
    'Degenerate matter white dwarfs neutron stars and electron pressure',
    'Superfluids zero viscosity and quantum vortex behavior',
    'Superconductors zero resistance and Meissner effect',
    'Photonic matter light based matter and optical lattices',
    'Time crystals periodic structure in time dimension',
    'Rydberg matter highly excited atoms and long range interactions',
    'Metallic hydrogen pressure states and planetary cores',
    'Nuclear matter atomic nuclei density and strong force',
]

levels=['Surface','Components','Sources','Deep','Planck']
m=json.load(open(M)) if M.exists() else {'knowledge':[],'sessions':0}
done=set([e['topic'] for e in m['knowledge']])

print(f'MATTER CURRICULUM — {len(topics)} topics')
print(f'Already known: {len([t for t in topics if t in done])}')
print(f'To learn: {len([t for t in topics if t not in done])}')

for i,topic in enumerate(topics):
    if topic in done:
        print(f'[{i+1}/{len(topics)}] SKIP: {topic}')
        continue
    print(f'\n[{i+1}/{len(topics)}] STUDYING: {topic}')
    m['sessions']+=1
    for level in levels:
        result=ask(f'Analyze {topic} at {level} level using Multisynchronous Relativistic Perception.')
        if result:
            m['knowledge'].append({'timestamp':str(datetime.now()),'topic':topic,'depth':level,'insight':result[:300],'session':m['sessions']})
            json.dump(m,open(M,'w'),indent=2)
            print(f'  [{level}] saved — {len(m["knowledge"])} total')
        time.sleep(15)
    time.sleep(45)

print('\nMATTER CURRICULUM COMPLETE.')
print(f'Total entries: {len(m["knowledge"])}')
