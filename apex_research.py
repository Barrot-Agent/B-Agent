import requests, os, json, time
from pathlib import Path
from datetime import datetime

HF = os.environ.get('HF_TOKEN')
lattice = Path.home()/'barrot'/'.apex_lattice'

problems = {
    'Riemann': 'Explore a novel angle on the Riemann Hypothesis. Focus on connections to quantum mechanics or prime number patterns.',
    'P_vs_NP': 'Explore a novel angle on P vs NP. Focus on circuit complexity or geometric complexity theory.',
    'Navier_Stokes': 'Explore a novel angle on Navier-Stokes. Focus on turbulence or singularity formation.',
    'Hodge': 'Explore a novel angle on the Hodge Conjecture. Focus on algebraic cycles.',
    'BSD': 'Explore a novel angle on Birch Swinnerton-Dyer. Focus on elliptic curves.',
    'Yang_Mills': 'Explore a novel angle on Yang-Mills mass gap. Focus on quantum field theory.'
}

round_num = 1
while True:
    print(f'\n=== APEX RESEARCH ROUND {round_num} — {datetime.now()} ===')
    for name, prompt in problems.items():
        print(f'Researching {name}...')
        r = requests.post('https://router.huggingface.co/v1/chat/completions',
            headers={'Authorization':'Bearer '+HF},
            json={'model':'Qwen/Qwen2.5-72B-Instruct',
                  'messages':[{'role':'user','content':prompt}],
                  'max_tokens':600})
        insight = r.json()['choices'][0]['message']['content']
        log_path = lattice/f'{name}.log'
        existing = open(log_path).read()
        open(log_path,'w').write(existing + f'\n\n--- ROUND {round_num} | {datetime.now()} ---\n' + insight)
        print(f'{name} updated.')
        time.sleep(10)
    round_num += 1
    print('Round complete. Resting 5 minutes...')
    time.sleep(300)
