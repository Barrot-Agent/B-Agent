#!/usr/bin/env python3
"""
Simulation Engine
Core engine for the symbolic simulation layer.
Orchestrates simulation chambers, manages simulation state, and coordinates subsystems.
"""

import json
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
SIM_PATH = REPO_ROOT / "barrot_sim"
SIM_STATE_PATH = SIM_PATH / "simulation_state.json"
SIM_LOG_PATH = REPO_ROOT / "memory-bundles" / "simulation_log.md"


class SimulationMode(Enum):
    """Simulation execution modes"""
    FORECAST = "forecast"  # Predict outcomes
    TEST = "test"  # Test scenarios
    STRESS = "stress"  # Stress testing
    PARADOX = "paradox"  # Paradox resolution
    RECURSIVE = "recursive"  # Recursive simulation


class SimulationChamber:
    """Isolated symbolic simulation chamber"""
    
    def __init__(self, chamber_id: str, mode: SimulationMode):
        self.chamber_id = chamber_id
        self.mode = mode
        self.state = {
            "created": datetime.now(timezone.utc).isoformat(),
            "agents": [],
            "directives": [],
            "glyphs_emitted": [],
            "council_votes": [],
            "reality_drift": 0.0
        }
        self.active = True
    
    def add_agent(self, agent_config: Dict[str, Any]):
        """Add an agent to the chamber"""
        self.state["agents"].append({
            "id": agent_config.get("id", f"agent_{len(self.state['agents'])}"),
            "name": agent_config.get("name", "Unknown"),
            "config": agent_config,
            "mutations": [],
            "added_at": datetime.now(timezone.utc).isoformat()
        })
    
    def inject_directive(self, directive: Dict[str, Any]):
        """Inject a directive into the chamber"""
        self.state["directives"].append({
            "directive": directive,
            "injected_at": datetime.now(timezone.utc).isoformat(),
            "impact": None
        })
    
    def emit_glyph(self, glyph_name: str, context: Dict[str, Any]):
        """Record glyph emission in chamber"""
        self.state["glyphs_emitted"].append({
            "glyph_name": glyph_name,
            "context": context,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def record_council_vote(self, vote_data: Dict[str, Any]):
        """Record council deliberation"""
        self.state["council_votes"].append({
            "vote": vote_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def update_reality_drift(self, drift: float):
        """Update reality drift measurement"""
        self.state["reality_drift"] = drift
    
    def get_state(self) -> Dict[str, Any]:
        """Get current chamber state"""
        return {
            "chamber_id": self.chamber_id,
            "mode": self.mode.value,
            "active": self.active,
            "state": self.state
        }
    
    def close(self):
        """Close the chamber"""
        self.active = False
        self.state["closed_at"] = datetime.now(timezone.utc).isoformat()


class SimulationEngine:
    """Main simulation engine"""
    
    def __init__(self):
        self.chambers: Dict[str, SimulationChamber] = {}
        self.simulation_history: List[Dict[str, Any]] = []
        self.load_state()
    
    def load_state(self):
        """Load simulation state from disk"""
        if SIM_STATE_PATH.exists():
            try:
                with open(SIM_STATE_PATH, 'r') as f:
                    state = json.load(f)
                    self.simulation_history = state.get("history", [])
            except Exception as e:
                print(f"Warning: Could not load simulation state: {e}")
    
    def save_state(self):
        """Save simulation state to disk"""
        SIM_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "active_chambers": list(self.chambers.keys()),
            "history": self.simulation_history
        }
        with open(SIM_STATE_PATH, 'w') as f:
            json.dump(state, f, indent=2)
    
    def create_chamber(self, chamber_id: str, mode: SimulationMode) -> SimulationChamber:
        """Create a new simulation chamber"""
        if chamber_id in self.chambers:
            raise ValueError(f"Chamber {chamber_id} already exists")
        
        chamber = SimulationChamber(chamber_id, mode)
        self.chambers[chamber_id] = chamber
        
        self.log_event("CHAMBER_CREATED", {
            "chamber_id": chamber_id,
            "mode": mode.value
        })
        
        return chamber
    
    def get_chamber(self, chamber_id: str) -> Optional[SimulationChamber]:
        """Get a chamber by ID"""
        return self.chambers.get(chamber_id)
    
    def close_chamber(self, chamber_id: str) -> Dict[str, Any]:
        """Close a chamber and record results"""
        chamber = self.chambers.get(chamber_id)
        if not chamber:
            raise ValueError(f"Chamber {chamber_id} not found")
        
        chamber.close()
        results = chamber.get_state()
        
        self.simulation_history.append(results)
        del self.chambers[chamber_id]
        
        self.log_event("CHAMBER_CLOSED", {
            "chamber_id": chamber_id,
            "results": results
        })
        
        self.save_state()
        return results
    
    def run_simulation(
        self,
        chamber_id: str,
        scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a simulation scenario"""
        chamber = self.get_chamber(chamber_id)
        if not chamber:
            raise ValueError(f"Chamber {chamber_id} not found")
        
        # Execute scenario based on chamber mode
        results = {
            "chamber_id": chamber_id,
            "scenario": scenario,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "outcomes": []
        }
        
        # Mode-specific execution
        if chamber.mode == SimulationMode.FORECAST:
            results["outcomes"] = self._run_forecast(chamber, scenario)
        elif chamber.mode == SimulationMode.TEST:
            results["outcomes"] = self._run_test(chamber, scenario)
        elif chamber.mode == SimulationMode.STRESS:
            results["outcomes"] = self._run_stress(chamber, scenario)
        elif chamber.mode == SimulationMode.PARADOX:
            results["outcomes"] = self._run_paradox(chamber, scenario)
        elif chamber.mode == SimulationMode.RECURSIVE:
            results["outcomes"] = self._run_recursive(chamber, scenario)
        
        results["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        self.log_event("SIMULATION_COMPLETED", results)
        return results
    
    def _run_forecast(self, chamber: SimulationChamber, scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run forecasting simulation"""
        from .directive_forecast import DirectiveForecaster
        
        forecaster = DirectiveForecaster()
        outcomes = []
        
        for directive in scenario.get("directives", []):
            chamber.inject_directive(directive)
            # Use actual forecasting logic
            forecast_report = forecaster.forecast_directive(directive)
            outcome = {
                "directive": directive,
                "predicted_impact": forecast_report["impacts"],
                "confidence": forecast_report["confidence"],
                "risks": forecast_report["risks"],
                "opportunities": forecast_report["opportunities"]
            }
            outcomes.append(outcome)
        return outcomes
    
    def _run_test(self, chamber: SimulationChamber, scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run testing simulation"""
        outcomes = []
        protocols = scenario.get("protocols", [])
        
        for protocol in protocols:
            # Simulate protocol testing with varying results
            protocol_name = protocol.get("name", "UNKNOWN")
            constraints = protocol.get("constraints", [])
            
            # Base consistency and stability
            consistency = 0.95 - (len(constraints) * 0.02)  # More constraints = lower consistency
            stability = 0.92 - (len(constraints) * 0.015)
            
            outcome = {
                "protocol": protocol,
                "test_result": "passed" if consistency > 0.8 else "failed",
                "metrics": {
                    "consistency": max(0.5, min(1.0, consistency)),
                    "stability": max(0.5, min(1.0, stability))
                }
            }
            outcomes.append(outcome)
        return outcomes
    
    def _run_stress(self, chamber: SimulationChamber, scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run stress testing simulation"""
        outcomes = []
        stress_level = scenario.get("stress_level", "medium")
        
        # Map stress level to resilience
        stress_impact = {
            "low": 0.95,
            "medium": 0.88,
            "high": 0.75,
            "extreme": 0.60
        }
        
        resilience = stress_impact.get(stress_level, 0.88)
        
        # Determine if breaking point is reached
        breaking_point = None if resilience > 0.70 else f"at_{stress_level}_stress"
        
        outcome = {
            "stress_level": stress_level,
            "breaking_point": breaking_point,
            "resilience_score": resilience,
            "recommendation": "increase_capacity" if breaking_point else "within_limits"
        }
        outcomes.append(outcome)
        return outcomes
    
    def _run_paradox(self, chamber: SimulationChamber, scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run paradox resolution simulation"""
        outcomes = []
        paradoxes = scenario.get("paradoxes", [])
        
        for paradox in paradoxes:
            # Analyze paradox complexity
            paradox_text = str(paradox).lower()
            has_contradiction = "and" in paradox_text or "but" in paradox_text
            
            # Resolution strategy based on paradox type
            if has_contradiction:
                resolution = "polarity_navigation"
                coherence = 0.82
            else:
                resolution = "synthesis"
                coherence = 0.90
            
            outcome = {
                "paradox": paradox,
                "resolution": resolution,
                "coherence": coherence,
                "strategy": "hermetic_polarity" if has_contradiction else "dialectic_synthesis"
            }
            outcomes.append(outcome)
        return outcomes
    
    def _run_recursive(self, chamber: SimulationChamber, scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run recursive simulation"""
        outcomes = []
        depth = scenario.get("recursion_depth", 3)
        max_depth = min(depth, 10)  # Cap at 10 to prevent infinite loops
        
        # Simulate convergence behavior
        convergence = depth <= 5  # Deeper recursion = less likely to converge
        
        if convergence:
            final_state = "stable"
            iterations = depth
        else:
            final_state = "oscillating"
            iterations = max_depth
        
        outcome = {
            "recursion_depth": depth,
            "max_depth_reached": iterations,
            "convergence": convergence,
            "final_state": final_state,
            "iterations_to_converge": iterations if convergence else None
        }
        outcomes.append(outcome)
        return outcomes
    
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log simulation event"""
        SIM_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        log_entry = f"\n## {event_type}\n"
        log_entry += f"**Timestamp:** {datetime.now(timezone.utc).isoformat()}\n\n"
        log_entry += f"```json\n{json.dumps(data, indent=2)}\n```\n"
        
        with open(SIM_LOG_PATH, 'a') as f:
            f.write(log_entry)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get simulation statistics"""
        return {
            "active_chambers": len(self.chambers),
            "total_simulations": len(self.simulation_history),
            "chambers": [c.get_state() for c in self.chambers.values()]
        }


# Singleton instance
_engine = None

def get_engine() -> SimulationEngine:
    """Get the singleton simulation engine instance"""
    global _engine
    if _engine is None:
        _engine = SimulationEngine()
    return _engine


if __name__ == "__main__":
    # Example usage
    engine = get_engine()
    
    # Create a chamber
    chamber = engine.create_chamber("test_chamber_1", SimulationMode.FORECAST)
    
    # Add an agent
    chamber.add_agent({"name": "Test Agent", "type": "forecaster"})
    
    # Run simulation
    results = engine.run_simulation("test_chamber_1", {
        "directives": [
            {"name": "TEST_DIRECTIVE", "impact": "analyze"}
        ]
    })
    
    print("Simulation Results:")
    print(json.dumps(results, indent=2))
    
    # Close chamber
    engine.close_chamber("test_chamber_1")
    
    # Print statistics
    print("\nEngine Statistics:")
    print(json.dumps(engine.get_statistics(), indent=2))
