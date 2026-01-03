#!/usr/bin/env python3
"""
Council Echo Testing
Simulate council deliberations under altered symbolic conditions.
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import random


class CouncilAgent:
    """Simulated council agent"""
    
    def __init__(self, name: str, bias: str, weight: float = 1.0):
        self.name = name
        self.bias = bias
        self.weight = weight
        self.vote_history = []
    
    def cast_vote(self, topic: str, conditions: Dict[str, Any]) -> float:
        """Cast a vote based on bias and conditions"""
        base_score = random.uniform(0.3, 0.9)
        
        # Adjust based on bias and conditions
        adjustment = self._apply_bias_adjustment(conditions)
        score = max(0.0, min(1.0, base_score + adjustment))
        
        self.vote_history.append({
            "topic": topic,
            "score": score,
            "conditions": conditions,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return score
    
    def _apply_bias_adjustment(self, conditions: Dict[str, Any]) -> float:
        """Apply bias-based adjustment"""
        adjustment = 0.0
        
        # Map bias to conditions
        bias_condition_map = {
            "practical_solutions": ("practicality", 0.2),
            "conceptual_frameworks": ("complexity", -0.1),
            "critical_analysis": ("complexity", 0.1),
            "opportunity_seeking": ("opportunity", 0.15),
            "risk_mitigation": ("risk", -0.2),
            "empirical_validation": ("practicality", 0.15),
            "fault_detection": ("risk", -0.15)
        }
        
        if self.bias in bias_condition_map:
            condition_key, bias_adjustment = bias_condition_map[self.bias]
            condition_value = conditions.get(condition_key, "medium")
            
            # Apply adjustment based on condition value
            if condition_value == "high" and bias_adjustment > 0:
                adjustment = bias_adjustment
            elif condition_value == "high" and bias_adjustment < 0:
                adjustment = bias_adjustment
            elif condition_value == "low" and bias_adjustment < 0:
                adjustment = -bias_adjustment * 0.5
        
        return adjustment
    
    def get_agent_data(self) -> Dict[str, Any]:
        """Get agent data"""
        return {
            "name": self.name,
            "bias": self.bias,
            "weight": self.weight,
            "total_votes": len(self.vote_history),
            "avg_vote": sum(v["score"] for v in self.vote_history) / len(self.vote_history) if self.vote_history else 0.0
        }


class CouncilEchoSimulator:
    """Simulate council deliberations under various conditions"""
    
    def __init__(self):
        self.agents = self._initialize_agents()
        self.simulation_history = []
    
    def _initialize_agents(self) -> List[CouncilAgent]:
        """Initialize council agents"""
        return [
            CouncilAgent("Pragmatist", "practical_solutions", 1.2),
            CouncilAgent("Theorist", "conceptual_frameworks", 1.0),
            CouncilAgent("Skeptic", "critical_analysis", 0.9),
            CouncilAgent("Optimist", "opportunity_seeking", 1.1),
            CouncilAgent("Guardian", "risk_mitigation", 1.3),
            CouncilAgent("Experimentalist", "empirical_validation", 1.0),
            CouncilAgent("Error Spotter", "fault_detection", 0.8)
        ]
    
    def simulate_deliberation(
        self,
        topic: str,
        conditions: Dict[str, Any],
        altered_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Simulate a council deliberation"""
        
        # Run baseline deliberation
        baseline_votes = self._collect_votes(topic, conditions)
        baseline_consensus = self._calculate_consensus(baseline_votes)
        
        result = {
            "topic": topic,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "baseline": {
                "conditions": conditions,
                "votes": baseline_votes,
                "consensus": baseline_consensus
            }
        }
        
        # If altered conditions provided, run comparison
        if altered_conditions:
            altered_votes = self._collect_votes(topic, altered_conditions)
            altered_consensus = self._calculate_consensus(altered_votes)
            
            result["altered"] = {
                "conditions": altered_conditions,
                "votes": altered_votes,
                "consensus": altered_consensus
            }
            
            result["delta"] = self._calculate_delta(
                baseline_consensus,
                altered_consensus
            )
        
        self.simulation_history.append(result)
        self._emit_council_echo_glyph(result)
        
        return result
    
    def _collect_votes(self, topic: str, conditions: Dict[str, Any]) -> Dict[str, float]:
        """Collect votes from all agents"""
        votes = {}
        for agent in self.agents:
            votes[agent.name] = agent.cast_vote(topic, conditions) * agent.weight
        return votes
    
    def _calculate_consensus(self, votes: Dict[str, float]) -> Dict[str, Any]:
        """Calculate consensus from votes"""
        vote_values = list(votes.values())
        avg_agreement = sum(vote_values) / len(vote_values)
        
        # Calculate disagreement level
        disagreement = sum(abs(v - avg_agreement) for v in vote_values) / len(vote_values)
        
        # Consensus reached if avg > 0.6 and disagreement < 0.25
        reached = avg_agreement > 0.6 and disagreement < 0.25
        
        return {
            "reached": reached,
            "avg_agreement": round(avg_agreement, 3),
            "disagreement_level": round(disagreement, 3),
            "participating_agents": len(votes)
        }
    
    def _calculate_delta(
        self,
        baseline: Dict[str, Any],
        altered: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate delta between baseline and altered consensus"""
        return {
            "agreement_change": round(
                altered["avg_agreement"] - baseline["avg_agreement"],
                3
            ),
            "disagreement_change": round(
                altered["disagreement_level"] - baseline["disagreement_level"],
                3
            ),
            "consensus_changed": baseline["reached"] != altered["reached"]
        }
    
    def test_condition_sensitivity(
        self,
        topic: str,
        base_conditions: Dict[str, Any],
        varying_parameter: str,
        values: List[Any]
    ) -> Dict[str, Any]:
        """Test sensitivity to a specific condition parameter"""
        results = []
        
        for value in values:
            conditions = base_conditions.copy()
            conditions[varying_parameter] = value
            
            votes = self._collect_votes(topic, conditions)
            consensus = self._calculate_consensus(votes)
            
            results.append({
                "parameter_value": value,
                "consensus": consensus
            })
        
        return {
            "topic": topic,
            "varying_parameter": varying_parameter,
            "sensitivity_test": results,
            "parameter_impact": self._analyze_parameter_impact(results)
        }
    
    def _analyze_parameter_impact(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze impact of parameter variation"""
        agreements = [r["consensus"]["avg_agreement"] for r in results]
        
        return {
            "min_agreement": min(agreements),
            "max_agreement": max(agreements),
            "range": max(agreements) - min(agreements),
            "impact_level": "high" if max(agreements) - min(agreements) > 0.3 else "medium" if max(agreements) - min(agreements) > 0.15 else "low"
        }
    
    def simulate_paradox_resolution(
        self,
        paradox: str,
        conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate how council resolves a paradox"""
        # Add contradiction flag to conditions
        paradox_conditions = conditions.copy()
        paradox_conditions["paradox"] = True
        paradox_conditions["complexity"] = "high"
        
        result = self.simulate_deliberation(
            f"PARADOX: {paradox}",
            paradox_conditions
        )
        
        result["paradox_resolved"] = result["baseline"]["consensus"]["reached"]
        result["resolution_quality"] = result["baseline"]["consensus"]["avg_agreement"]
        
        return result
    
    def _emit_council_echo_glyph(self, result: Dict[str, Any]):
        """Emit COUNCIL_ECHO_GLYPH"""
        from .simulation_engine import get_engine
        
        engine = get_engine()
        engine.log_event("COUNCIL_ECHO_GLYPH", {
            "deliberation": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def get_agent_statistics(self) -> List[Dict[str, Any]]:
        """Get statistics for all agents"""
        return [agent.get_agent_data() for agent in self.agents]
    
    def get_simulation_summary(self) -> Dict[str, Any]:
        """Get summary of all simulations"""
        total_sims = len(self.simulation_history)
        
        if total_sims == 0:
            return {"simulations": 0}
        
        baseline_consensuses = [
            s["baseline"]["consensus"]["reached"]
            for s in self.simulation_history
        ]
        
        return {
            "total_simulations": total_sims,
            "consensus_rate": sum(baseline_consensuses) / total_sims,
            "avg_agreement": sum(
                s["baseline"]["consensus"]["avg_agreement"]
                for s in self.simulation_history
            ) / total_sims,
            "agents": self.get_agent_statistics()
        }


if __name__ == "__main__":
    # Example usage
    simulator = CouncilEchoSimulator()
    
    print("Council Echo Simulation\n")
    
    # Simulate basic deliberation
    result1 = simulator.simulate_deliberation(
        "Implement new memory protocol",
        {
            "practicality": "high",
            "complexity": "medium",
            "risk": "low",
            "opportunity": "high"
        }
    )
    
    print("1. Basic Deliberation:")
    print(f"   Consensus: {result1['baseline']['consensus']['reached']}")
    print(f"   Agreement: {result1['baseline']['consensus']['avg_agreement']:.3f}\n")
    
    # Simulate with altered conditions
    result2 = simulator.simulate_deliberation(
        "Deploy experimental feature",
        {
            "practicality": "medium",
            "complexity": "high",
            "risk": "medium",
            "opportunity": "medium"
        },
        altered_conditions={
            "practicality": "high",
            "complexity": "low",
            "risk": "low",
            "opportunity": "high"
        }
    )
    
    print("2. Deliberation with Altered Conditions:")
    print(f"   Baseline consensus: {result2['baseline']['consensus']['reached']}")
    print(f"   Altered consensus: {result2['altered']['consensus']['reached']}")
    print(f"   Agreement change: {result2['delta']['agreement_change']:.3f}\n")
    
    # Test condition sensitivity
    sensitivity = simulator.test_condition_sensitivity(
        "Optimize glyph cascade",
        {"practicality": "medium", "complexity": "medium", "opportunity": "medium"},
        "risk",
        ["low", "medium", "high"]
    )
    
    print("3. Risk Sensitivity Test:")
    print(f"   Impact level: {sensitivity['parameter_impact']['impact_level']}")
    print(f"   Agreement range: {sensitivity['parameter_impact']['range']:.3f}\n")
    
    # Simulate paradox resolution
    paradox = simulator.simulate_paradox_resolution(
        "Maximize both speed and accuracy simultaneously",
        {"practicality": "medium", "opportunity": "high"}
    )
    
    print("4. Paradox Resolution:")
    print(f"   Resolved: {paradox['paradox_resolved']}")
    print(f"   Quality: {paradox['resolution_quality']:.3f}\n")
    
    # Get summary
    summary = simulator.get_simulation_summary()
    print("\nSimulation Summary:")
    print(json.dumps(summary, indent=2))
