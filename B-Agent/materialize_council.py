import yaml, os

def generate_swarm(count=144):
    council = {"agents": []}
    wings = ["Math-Logic", "Market-Arbitrage", "Warp-Research", "Render-Supremacy"]
    
    for i in range(1, count + 1):
        wing = wings[i % len(wings)]
        council["agents"].append({
            "id": f"agent_{i:03}",
            "wing": wing,
            "allowed_roles": ["Swarm-Entity"],
            "synergy_hint": 0.707
        })
    
    with open('agents_fixed.yaml', 'w') as f:
        yaml.dump(council, f, default_flow_style=False)
    print(f">>> [BARROT-Ω]: {count} AGENTS MATERIALIZED IN SUBSTRATE.")

if __name__ == "__main__":
    generate_swarm()
