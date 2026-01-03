#!/usr/bin/env python3
"""
Reality Drift Detection
Identify symbolic divergence between simulated and live cognition.
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path


class CognitionState:
    """Snapshot of cognition state"""
    
    def __init__(self, state_id: str, state_data: Dict[str, Any]):
        self.state_id = state_id
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.state_data = state_data
        self.metrics = self._extract_metrics(state_data)
    
    def _extract_metrics(self, state_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract key metrics from state data"""
        return {
            "memory_utilization": state_data.get("memory_utilization", 0.5),
            "matrix_coherence": state_data.get("matrix_coherence", 0.8),
            "council_consensus": state_data.get("council_consensus", 0.7),
            "glyph_emission_rate": state_data.get("glyph_emission_rate", 0.6),
            "directive_compliance": state_data.get("directive_compliance", 0.9)
        }
    
    def get_state(self) -> Dict[str, Any]:
        """Get complete state"""
        return {
            "state_id": self.state_id,
            "timestamp": self.timestamp,
            "data": self.state_data,
            "metrics": self.metrics
        }


class RealityDriftDetector:
    """Detect drift between simulated and live cognition states"""
    
    def __init__(self):
        self.live_state: Optional[CognitionState] = None
        self.simulated_states: Dict[str, CognitionState] = {}
        self.drift_history: List[Dict[str, Any]] = []
        self.drift_threshold = 0.2  # 20% divergence triggers alert
    
    def set_live_state(self, state_data: Dict[str, Any]):
        """Set the current live cognition state"""
        self.live_state = CognitionState("live", state_data)
    
    def add_simulated_state(self, simulation_id: str, state_data: Dict[str, Any]):
        """Add a simulated cognition state"""
        self.simulated_states[simulation_id] = CognitionState(simulation_id, state_data)
    
    def detect_drift(self, simulation_id: str) -> Dict[str, Any]:
        """Detect drift between live and simulated state"""
        if not self.live_state:
            raise ValueError("Live state not set")
        
        if simulation_id not in self.simulated_states:
            raise ValueError(f"Simulation {simulation_id} not found")
        
        sim_state = self.simulated_states[simulation_id]
        
        # Calculate drift for each metric
        drift_metrics = {}
        total_drift = 0.0
        
        for metric_name in self.live_state.metrics.keys():
            live_value = self.live_state.metrics[metric_name]
            sim_value = sim_state.metrics.get(metric_name, 0.0)
            
            drift = abs(live_value - sim_value)
            
            # Calculate percentage more robustly
            if live_value >= 0.01:
                drift_percentage = round((drift / live_value) * 100, 1)
            else:
                # For very small values, use absolute drift as percentage indicator
                drift_percentage = round(drift * 100, 1)
            
            drift_metrics[metric_name] = {
                "live_value": live_value,
                "simulated_value": sim_value,
                "drift": round(drift, 3),
                "drift_percentage": drift_percentage
            }
            total_drift += drift
        
        avg_drift = total_drift / len(self.live_state.metrics)
        drift_detected = avg_drift > self.drift_threshold
        
        result = {
            "simulation_id": simulation_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "drift_detected": drift_detected,
            "avg_drift": round(avg_drift, 3),
            "drift_percentage": round((avg_drift / 1.0) * 100, 1),
            "metrics": drift_metrics,
            "severity": self._calculate_severity(avg_drift),
            "recommendations": self._generate_recommendations(drift_metrics, avg_drift)
        }
        
        self.drift_history.append(result)
        
        if drift_detected:
            self._emit_drift_glyph(result)
        
        return result
    
    def _calculate_severity(self, drift: float) -> str:
        """Calculate drift severity"""
        if drift < 0.1:
            return "minimal"
        elif drift < 0.2:
            return "low"
        elif drift < 0.3:
            return "medium"
        elif drift < 0.5:
            return "high"
        else:
            return "critical"
    
    def _generate_recommendations(
        self,
        drift_metrics: Dict[str, Dict[str, Any]],
        avg_drift: float
    ) -> List[str]:
        """Generate recommendations based on drift"""
        recommendations = []
        
        if avg_drift > 0.3:
            recommendations.append("URGENT: Recalibrate simulation parameters")
        
        # Check individual metrics
        for metric, data in drift_metrics.items():
            if data["drift"] > 0.25:
                recommendations.append(f"Review {metric} modeling - significant divergence detected")
        
        if avg_drift < 0.1:
            recommendations.append("Simulation alignment excellent - maintain current parameters")
        elif avg_drift < 0.2:
            recommendations.append("Minor adjustments recommended to improve alignment")
        
        return recommendations
    
    def compare_multiple_simulations(
        self,
        simulation_ids: List[str]
    ) -> Dict[str, Any]:
        """Compare multiple simulations against live state"""
        if not self.live_state:
            raise ValueError("Live state not set")
        
        comparisons = []
        for sim_id in simulation_ids:
            if sim_id in self.simulated_states:
                drift = self.detect_drift(sim_id)
                comparisons.append(drift)
        
        if not comparisons:
            return {"error": "No valid simulations found"}
        
        # Find best and worst simulations
        best = min(comparisons, key=lambda x: x["avg_drift"])
        worst = max(comparisons, key=lambda x: x["avg_drift"])
        
        return {
            "simulations_compared": len(comparisons),
            "best_simulation": {
                "id": best["simulation_id"],
                "drift": best["avg_drift"]
            },
            "worst_simulation": {
                "id": worst["simulation_id"],
                "drift": worst["avg_drift"]
            },
            "avg_drift_across_all": round(
                sum(c["avg_drift"] for c in comparisons) / len(comparisons),
                3
            )
        }
    
    def detect_drift_trend(self, lookback: int = 10) -> Dict[str, Any]:
        """Analyze drift trend over recent history"""
        if len(self.drift_history) < 2:
            return {"status": "insufficient_data"}
        
        recent = self.drift_history[-lookback:]
        drifts = [d["avg_drift"] for d in recent]
        
        # Calculate trend
        if len(drifts) >= 2:
            trend = drifts[-1] - drifts[0]
            trend_direction = "increasing" if trend > 0.05 else "decreasing" if trend < -0.05 else "stable"
        else:
            trend = 0.0
            trend_direction = "stable"
        
        return {
            "samples": len(recent),
            "avg_drift": round(sum(drifts) / len(drifts), 3),
            "min_drift": round(min(drifts), 3),
            "max_drift": round(max(drifts), 3),
            "trend": round(trend, 3),
            "trend_direction": trend_direction,
            "alert": trend_direction == "increasing" and drifts[-1] > 0.25
        }
    
    def calibrate_threshold(self, target_sensitivity: str = "medium"):
        """Calibrate drift detection threshold"""
        thresholds = {
            "low": 0.3,
            "medium": 0.2,
            "high": 0.15,
            "critical": 0.1
        }
        
        self.drift_threshold = thresholds.get(target_sensitivity, 0.2)
    
    def _emit_drift_glyph(self, drift_data: Dict[str, Any]):
        """Emit REALITY_DRIFT_GLYPH"""
        from .simulation_engine import get_engine
        
        engine = get_engine()
        engine.log_event("REALITY_DRIFT_GLYPH", {
            "drift": drift_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def get_drift_statistics(self) -> Dict[str, Any]:
        """Get drift statistics"""
        if not self.drift_history:
            return {"status": "no_data"}
        
        drifts = [d["avg_drift"] for d in self.drift_history]
        drift_detected_count = sum(1 for d in self.drift_history if d["drift_detected"])
        
        return {
            "total_checks": len(self.drift_history),
            "drift_detected_count": drift_detected_count,
            "drift_rate": round(drift_detected_count / len(self.drift_history), 3),
            "avg_drift": round(sum(drifts) / len(drifts), 3),
            "max_drift": round(max(drifts), 3),
            "min_drift": round(min(drifts), 3),
            "current_threshold": self.drift_threshold
        }


if __name__ == "__main__":
    # Example usage
    detector = RealityDriftDetector()
    
    print("Reality Drift Detection\n")
    
    # Set live state
    detector.set_live_state({
        "memory_utilization": 0.75,
        "matrix_coherence": 0.88,
        "council_consensus": 0.82,
        "glyph_emission_rate": 0.65,
        "directive_compliance": 0.92
    })
    
    print("1. Live state set\n")
    
    # Add simulated states
    detector.add_simulated_state("sim_1", {
        "memory_utilization": 0.72,
        "matrix_coherence": 0.85,
        "council_consensus": 0.80,
        "glyph_emission_rate": 0.63,
        "directive_compliance": 0.90
    })
    
    detector.add_simulated_state("sim_2", {
        "memory_utilization": 0.65,
        "matrix_coherence": 0.75,
        "council_consensus": 0.70,
        "glyph_emission_rate": 0.55,
        "directive_compliance": 0.85
    })
    
    print("2. Simulated states added\n")
    
    # Detect drift for sim_1
    drift1 = detector.detect_drift("sim_1")
    print("3. Drift Detection - Simulation 1:")
    print(f"   Drift detected: {drift1['drift_detected']}")
    print(f"   Average drift: {drift1['avg_drift']}")
    print(f"   Severity: {drift1['severity']}")
    print(f"   Recommendations: {len(drift1['recommendations'])}\n")
    
    # Detect drift for sim_2
    drift2 = detector.detect_drift("sim_2")
    print("4. Drift Detection - Simulation 2:")
    print(f"   Drift detected: {drift2['drift_detected']}")
    print(f"   Average drift: {drift2['avg_drift']}")
    print(f"   Severity: {drift2['severity']}\n")
    
    # Compare simulations
    comparison = detector.compare_multiple_simulations(["sim_1", "sim_2"])
    print("5. Simulation Comparison:")
    print(json.dumps(comparison, indent=2))
    print()
    
    # Get statistics
    stats = detector.get_drift_statistics()
    print("6. Drift Statistics:")
    print(json.dumps(stats, indent=2))
