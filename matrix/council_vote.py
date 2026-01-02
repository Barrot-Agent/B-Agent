#!/usr/bin/env python3
"""
Node: Council Vote
Simulates agent disagreements and emits COUNCIL_ALIGNMENT_GLYPH upon consensus.
Represents multi-perspective reasoning and dialectical synthesis.
"""

import json
import random
from pathlib import Path
from datetime import datetime

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
GLYPHS_PATH = REPO_ROOT / "glyphs"
BUNDLES_PATH = REPO_ROOT / "memory-bundles"
TRACE_LOG_PATH = BUNDLES_PATH / "TRACE_LOG.md"

# Council agents with different perspectives
COUNCIL_AGENTS = [
    {
        "name": "Pragmatist",
        "bias": "practical_solutions",
        "weight": 1.0
    },
    {
        "name": "Theorist",
        "bias": "conceptual_frameworks",
        "weight": 0.8
    },
    {
        "name": "Skeptic",
        "bias": "critical_analysis",
        "weight": 1.2
    },
    {
        "name": "Optimist",
        "bias": "opportunity_seeking",
        "weight": 0.7
    },
    {
        "name": "Guardian",
        "bias": "risk_mitigation",
        "weight": 1.1
    }
]

def simulate_deliberation(topic="system_alignment"):
    """Simulate council deliberation on a topic"""
    print(f"[COUNCIL_VOTE] Topic: {topic}")
    
    votes = []
    arguments = []
    
    for agent in COUNCIL_AGENTS:
        # Each agent votes with some randomness influenced by their bias
        base_vote = random.uniform(0, 1)
        weighted_vote = base_vote * agent['weight']
        
        # Normalize to agreement scale (0-1)
        agreement = min(1.0, weighted_vote)
        
        votes.append({
            'agent': agent['name'],
            'agreement': agreement,
            'bias': agent['bias']
        })
        
        # Generate argument
        if agreement > 0.7:
            stance = "strongly supports"
        elif agreement > 0.5:
            stance = "supports"
        elif agreement > 0.3:
            stance = "has reservations about"
        else:
            stance = "opposes"
        
        argument = f"{agent['name']} ({agent['bias']}) {stance} this approach"
        arguments.append(argument)
        print(f"[COUNCIL_VOTE]   {argument} (score: {agreement:.2f})")
    
    return votes, arguments

def calculate_consensus(votes):
    """Calculate whether consensus is reached"""
    # Calculate average agreement
    avg_agreement = sum(v['agreement'] for v in votes) / len(votes)
    
    # Calculate variance (disagreement level)
    variance = sum((v['agreement'] - avg_agreement) ** 2 for v in votes) / len(votes)
    
    # Consensus requires high average and low variance
    consensus_reached = avg_agreement > 0.6 and variance < 0.1
    
    return {
        'reached': consensus_reached,
        'avg_agreement': avg_agreement,
        'disagreement_level': variance,
        'threshold': 0.6
    }

def emit_glyph(consensus, votes, arguments):
    """Emit COUNCIL_ALIGNMENT_GLYPH when consensus reached"""
    glyph_file = GLYPHS_PATH / "council_alignment_glyph.yml"
    
    glyph_content = f"""glyph_name: COUNCIL_ALIGNMENT_GLYPH
glyph_id: COUNCIL-001
version: 1.0.0
timestamp: {datetime.utcnow().isoformat()}Z

description: >
  Emitted when the council of diverse agent perspectives reaches consensus.
  Represents dialectical synthesis through multi-perspective deliberation.

symbolic_representation: "⚖ 🗳 ✓"

properties:
  dimension: multi_perspective
  mutability: consensus_based
  trigger: council_deliberation
  
attributes:
  - dialectical_reasoning
  - perspective_synthesis
  - consensus_building
  - disagreement_resolution
  
consensus_metrics:
  reached: {str(consensus['reached']).lower()}
  avg_agreement: {consensus['avg_agreement']:.2f}
  disagreement_level: {consensus['disagreement_level']:.3f}
  participating_agents: {len(votes)}

council_votes:
{chr(10).join([f"  - {v['agent']}: {v['agreement']:.2f} ({v['bias']})" for v in votes])}

integration_points:
  - multi_agent_reasoning
  - consensus_protocols
  - dialectical_synthesis
  
usage_context: >
  Invoke when simulating multi-perspective deliberation to ensure decisions
  incorporate diverse viewpoints and reach genuine consensus rather than
  premature agreement.
"""
    
    with open(glyph_file, 'w') as f:
        f.write(glyph_content)
    
    print(f"[COUNCIL_VOTE] Emitted COUNCIL_ALIGNMENT_GLYPH -> {glyph_file}")

def log_deliberation(consensus, votes, arguments):
    """Log council deliberation to TRACE_LOG.md"""
    log_entry = f"""
## Council Deliberation: {datetime.utcnow().isoformat()}Z

**Consensus Reached:** {"Yes" if consensus['reached'] else "No"}
**Average Agreement:** {consensus['avg_agreement']:.2f}
**Disagreement Level:** {consensus['disagreement_level']:.3f}

### Council Arguments
"""
    
    for arg in arguments:
        log_entry += f"- {arg}\n"
    
    log_entry += f"""
### Decision
{'The council has reached consensus and moves forward with this approach.' if consensus['reached'] else 'The council requires further deliberation due to disagreement.'}

---
"""
    
    # Append to trace log
    with open(TRACE_LOG_PATH, 'a') as f:
        f.write(log_entry)
    
    print(f"[COUNCIL_VOTE] Logged deliberation to TRACE_LOG.md")

def main():
    print("[COUNCIL_VOTE] Convening council for deliberation...")
    
    # Simulate deliberation
    votes, arguments = simulate_deliberation("system_alignment")
    
    # Calculate consensus
    consensus = calculate_consensus(votes)
    
    # Report results
    print(f"[COUNCIL_VOTE] Average agreement: {consensus['avg_agreement']:.2f}")
    print(f"[COUNCIL_VOTE] Disagreement level: {consensus['disagreement_level']:.3f}")
    
    if consensus['reached']:
        print("[COUNCIL_VOTE] ✓ Consensus reached!")
        emit_glyph(consensus, votes, arguments)
    else:
        print("[COUNCIL_VOTE] ✗ No consensus - further deliberation needed")
    
    # Always log the deliberation
    log_deliberation(consensus, votes, arguments)

if __name__ == "__main__":
    main()
