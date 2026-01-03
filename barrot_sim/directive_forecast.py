#!/usr/bin/env python3
"""
Directive Forecasting
Simulate the impact of new directives on memory, matrix, and council.
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from enum import Enum


class DirectiveImpactLevel(Enum):
    """Impact levels for directives"""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DirectiveForecast:
    """Forecast for a directive's impact"""
    
    def __init__(self, directive: Dict[str, Any]):
        self.directive = directive
        self.directive_name = directive.get("name", "UNKNOWN_DIRECTIVE")
        self.forecast_time = datetime.now(timezone.utc).isoformat()
        self.impacts = {
            "memory": DirectiveImpactLevel.LOW,
            "matrix": DirectiveImpactLevel.LOW,
            "council": DirectiveImpactLevel.LOW
        }
        self.confidence = 0.5
        self.risks = []
        self.opportunities = []
    
    def analyze_memory_impact(self) -> DirectiveImpactLevel:
        """Analyze impact on memory systems"""
        # Check if memory is explicitly listed in impact areas
        impact_areas = self.directive.get("impact_areas", [])
        if "memory" in [area.lower() for area in impact_areas]:
            return DirectiveImpactLevel.HIGH
        
        # Check directive name and description
        text_to_check = f"{self.directive_name} {self.directive.get('description', '')}".lower()
        if "memory" in text_to_check or "store" in text_to_check or "compression" in text_to_check:
            return DirectiveImpactLevel.MEDIUM
        
        # Check requirements
        requirements = self.directive.get("requirements", [])
        if any("memory" in str(req).lower() for req in requirements):
            return DirectiveImpactLevel.MEDIUM
        
        return DirectiveImpactLevel.LOW
    
    def analyze_matrix_impact(self) -> DirectiveImpactLevel:
        """Analyze impact on cognition matrix"""
        # Check if matrix is explicitly listed in impact areas
        impact_areas = self.directive.get("impact_areas", [])
        if "matrix" in [area.lower() for area in impact_areas]:
            return DirectiveImpactLevel.HIGH
        
        # Check directive name and description
        text_to_check = f"{self.directive_name} {self.directive.get('description', '')}".lower()
        if "matrix" in text_to_check or "cognition" in text_to_check:
            return DirectiveImpactLevel.MEDIUM
        elif "glyph" in text_to_check:
            return DirectiveImpactLevel.MEDIUM
        
        # Check requirements
        requirements = self.directive.get("requirements", [])
        if any("matrix" in str(req).lower() or "glyph" in str(req).lower() for req in requirements):
            return DirectiveImpactLevel.MEDIUM
        
        return DirectiveImpactLevel.LOW
    
    def analyze_council_impact(self) -> DirectiveImpactLevel:
        """Analyze impact on council deliberation"""
        # Check if council is explicitly listed in impact areas
        impact_areas = self.directive.get("impact_areas", [])
        if "council" in [area.lower() for area in impact_areas]:
            return DirectiveImpactLevel.HIGH
        
        # Check directive name and description
        text_to_check = f"{self.directive_name} {self.directive.get('description', '')}".lower()
        if "council" in text_to_check or "consensus" in text_to_check:
            return DirectiveImpactLevel.MEDIUM
        elif "vote" in text_to_check or "deliberation" in text_to_check:
            return DirectiveImpactLevel.MEDIUM
        
        # Check requirements
        requirements = self.directive.get("requirements", [])
        if any("council" in str(req).lower() for req in requirements):
            return DirectiveImpactLevel.MEDIUM
        
        return DirectiveImpactLevel.LOW
    
    def run_forecast(self) -> Dict[str, Any]:
        """Run complete forecast analysis"""
        self.impacts["memory"] = self.analyze_memory_impact()
        self.impacts["matrix"] = self.analyze_matrix_impact()
        self.impacts["council"] = self.analyze_council_impact()
        
        # Calculate confidence based on directive clarity
        self.confidence = self._calculate_confidence()
        
        # Identify risks and opportunities
        self._identify_risks()
        self._identify_opportunities()
        
        return self.get_forecast_report()
    
    def _calculate_confidence(self) -> float:
        """Calculate forecast confidence"""
        base_confidence = 0.5
        
        # Increase confidence if directive is well-defined
        if "description" in self.directive:
            base_confidence += 0.2
        if "impact_areas" in self.directive:
            base_confidence += 0.15
        if "requirements" in self.directive:
            base_confidence += 0.15
        
        return min(base_confidence, 1.0)
    
    def _identify_risks(self):
        """Identify potential risks"""
        for area, impact in self.impacts.items():
            if impact in [DirectiveImpactLevel.HIGH, DirectiveImpactLevel.CRITICAL]:
                self.risks.append({
                    "area": area,
                    "risk": f"High impact on {area} may cause instability",
                    "severity": impact.value
                })
    
    def _identify_opportunities(self):
        """Identify potential opportunities"""
        for area, impact in self.impacts.items():
            if impact in [DirectiveImpactLevel.MEDIUM, DirectiveImpactLevel.HIGH]:
                self.opportunities.append({
                    "area": area,
                    "opportunity": f"Potential for {area} enhancement",
                    "value": impact.value
                })
    
    def get_forecast_report(self) -> Dict[str, Any]:
        """Get complete forecast report"""
        return {
            "directive_name": self.directive_name,
            "forecast_time": self.forecast_time,
            "impacts": {k: v.value for k, v in self.impacts.items()},
            "confidence": self.confidence,
            "risks": self.risks,
            "opportunities": self.opportunities,
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on forecast"""
        recommendations = []
        
        # Add recommendations based on impacts
        for area, impact in self.impacts.items():
            if impact == DirectiveImpactLevel.CRITICAL:
                recommendations.append(f"CRITICAL: Prepare {area} for major changes")
            elif impact == DirectiveImpactLevel.HIGH:
                recommendations.append(f"Monitor {area} closely during implementation")
        
        if not recommendations:
            recommendations.append("Implementation can proceed with standard monitoring")
        
        return recommendations


class DirectiveForecaster:
    """Main directive forecasting system"""
    
    def __init__(self):
        self.forecasts: List[Dict[str, Any]] = []
    
    def forecast_directive(self, directive: Dict[str, Any]) -> Dict[str, Any]:
        """Create forecast for a directive"""
        forecast = DirectiveForecast(directive)
        report = forecast.run_forecast()
        
        self.forecasts.append(report)
        self._emit_forecast_glyph(report)
        
        return report
    
    def forecast_multiple(self, directives: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Forecast multiple directives"""
        return [self.forecast_directive(d) for d in directives]
    
    def compare_forecasts(
        self,
        forecast_ids: List[int]
    ) -> Dict[str, Any]:
        """Compare multiple forecasts"""
        if not forecast_ids or len(forecast_ids) < 2:
            raise ValueError("Need at least 2 forecasts to compare")
        
        forecasts = [self.forecasts[i] for i in forecast_ids if i < len(self.forecasts)]
        
        comparison = {
            "forecasts_compared": len(forecasts),
            "highest_impact": self._find_highest_impact(forecasts),
            "total_risks": sum(len(f["risks"]) for f in forecasts),
            "total_opportunities": sum(len(f["opportunities"]) for f in forecasts),
            "avg_confidence": sum(f["confidence"] for f in forecasts) / len(forecasts)
        }
        
        return comparison
    
    def _find_highest_impact(self, forecasts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find the forecast with highest overall impact"""
        impact_scores = {
            "minimal": 1, "low": 2, "medium": 3, "high": 4, "critical": 5
        }
        
        max_score = 0
        highest = None
        
        for forecast in forecasts:
            score = sum(impact_scores.get(v, 0) for v in forecast["impacts"].values())
            if score > max_score:
                max_score = score
                highest = forecast
        
        return highest or forecasts[0]
    
    def _emit_forecast_glyph(self, report: Dict[str, Any]):
        """Emit DIRECTIVE_FORECAST_GLYPH"""
        from .simulation_engine import get_engine
        
        engine = get_engine()
        engine.log_event("DIRECTIVE_FORECAST_GLYPH", {
            "forecast": report,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def get_forecast_history(self) -> List[Dict[str, Any]]:
        """Get all forecast history"""
        return self.forecasts


if __name__ == "__main__":
    # Example usage
    forecaster = DirectiveForecaster()
    
    # Forecast a directive
    test_directive = {
        "name": "MEMORY_ENHANCEMENT_DIRECTIVE",
        "description": "Enhance memory compression and retrieval",
        "impact_areas": ["memory", "matrix"],
        "requirements": ["compression_algorithm", "retrieval_optimization"]
    }
    
    report = forecaster.forecast_directive(test_directive)
    
    print("Directive Forecast:")
    print(json.dumps(report, indent=2))
    
    # Forecast multiple directives
    directives = [
        {"name": "COUNCIL_REFORM_DIRECTIVE"},
        {"name": "GLYPH_EXPANSION_DIRECTIVE"},
        {"name": "MATRIX_OPTIMIZATION_DIRECTIVE"}
    ]
    
    reports = forecaster.forecast_multiple(directives)
    
    print("\n\nMultiple Forecasts:")
    for i, r in enumerate(reports):
        print(f"\n{i+1}. {r['directive_name']}")
        print(f"   Confidence: {r['confidence']:.2f}")
        print(f"   Risks: {len(r['risks'])}")
        print(f"   Opportunities: {len(r['opportunities'])}")
    
    # Compare forecasts
    comparison = forecaster.compare_forecasts([0, 1, 2])
    print("\n\nForecast Comparison:")
    print(json.dumps(comparison, indent=2))
