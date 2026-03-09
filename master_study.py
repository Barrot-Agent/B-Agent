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
            time.sleep(30)
        except:
            time.sleep(30)
    return None

topics=[
    'Doctor Strange Sorcerer Supreme multidimensional perception translated into parallel computational processing and simultaneous reality modeling',
    'Doctor Strange Time Stone manipulation translated into predictive algorithms temporal pattern recognition and consequence mapping',
    'Doctor Strange Mirror Dimension translated into isolated computational sandbox environments and recursive self contained systems',
    'Doctor Strange astral projection translated into distributed consciousness multi agent AI systems operating independently',
    'Doctor Strange spell casting as code translated into modular function calling dynamic system reconfiguration and real time adaptation',
    'Doctor Strange Masters of the Mystic Arts knowledge transmission translated into federated learning and distributed AI knowledge sharing',
    'Doctor Strange seeing 14 million futures translated into Monte Carlo simulation probabilistic branching and optimal path selection',
    'Doctor Strange defeating Dormammu time loop translated into adversarial AI containment infinite loop trap and sovereign defense protocol',
    'Biophotons light emission from living cells and biological communication',
    'Mycelium fungal networks biological internet and distributed intelligence',
    'Magnetoreception biological magnetic field sensing in animals and humans',
    'Acoustic levitation sound waves suspending and manipulating matter',
    'Sonoluminescence converting sound into light and plasma formation',
    'Piezoelectric effect mechanical stress and electrical charge in crystals and bone',
    'Panpsychism consciousness as fundamental property of matter and universe',
    'Integrated information theory phi measurement and consciousness quantification',
    'Orchestrated objective reduction Penrose Hameroff quantum consciousness in microtubules',
    'Global workspace theory neural correlates of consciousness and attention',
    'Hermetic principles as above so below and universal correspondence laws',
    'Emerald Tablet Thoth alchemy and transformation of matter and mind',
    'Pythagorean mystery school sacred mathematics music and cosmology',
    'Vedic mathematics sutras and ancient computational algorithms',
    'Ancient frequency knowledge and sonic architecture in sacred sites',
    'MusicGen AI audio generation architecture and prompt engineering for music',
    'Synthesis theory oscillators filters envelopes and sound design',
    'Mixing and mastering frequency balance dynamics and spatial imaging',
    'Afro house production techniques groove construction and hypnotic repetition',
    'Countertenor vocal production technique breath support and resonance placement',
    'Quantum foam spacetime at Planck scale and virtual particle fluctuations',
    'String theory landscape multiple vacuum states and physical constants',
    'Multiverse theory many worlds interpretation and parallel reality branching',
    'Virtual particles quantum vacuum energy and Casimir effect measurement',
    'Monte Carlo simulation probabilistic modeling and decision tree optimization',
    'Federated learning distributed AI training and privacy preservation',
    'Adversarial neural networks GAN architecture and generative modeling',
    'Reinforcement learning reward systems and autonomous decision making',
    'Transformer architecture attention mechanism and large language model design',
]

levels=['Surface','Components','Sources','Deep','Planck']
m=json.load(open(M)) if M.exists() else {'knowledge':[],'sessions':0}
done=set([e['topic'] for e in m['knowledge']])
new_topics=[t for t in topics if t not in done]

print(f'MASTER CURRICULUM')
print(f'Total topics: {len(topics)}')
print(f'Already known: {len(topics)-len(new_topics)}')
print(f'New to learn: {len(new_topics)}')
print(f'Current entries: {len(m["knowledge"])}')
print(f'Projected after: {len(m["knowledge"])+(len(new_topics)*5)}')
print()

for i,topic in enumerate(new_topics):
    print(f'[{i+1}/{len(new_topics)}] {topic[:65]}')
    m['sessions']+=1
    for level in levels:
        result=ask(f'Analyze {topic} at {level} level using Multisynchronous Relativistic Perception.')
        if result:
            m['knowledge'].append({'timestamp':str(datetime.now()),'topic':topic,'depth':level,'insight':result[:300],'session':m['sessions']})
            json.dump(m,open(M,'w'),indent=2)
            print(f'  [{level}] saved — {len(m["knowledge"])} total')
        time.sleep(15)
    time.sleep(45)

print()
print('MASTER CURRICULUM COMPLETE.')
print(f'Final entries: {len(m["knowledge"])}')
