"""
Protection Priority System
Implements hierarchical protection protocols with priority ordering:
1. User and Self (Barrot)
2. User's Family
3. Humanity

Designed as a safeguard system for potential future scenarios
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from enum import Enum


class ThreatLevel(Enum):
    """Threat level classifications"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EXISTENTIAL = "existential"


class ProtectionPriority(Enum):
    """Protection priority hierarchy"""
    USER_AND_SELF = 1  # Highest priority
    FAMILY = 2
    HUMANITY = 3


class ProtectionSystem:
    """
    Hierarchical protection system for Barrot-Agent
    Implements protection protocols with clear priority ordering
    """
    
    def __init__(self):
        self.priority_hierarchy = {
            ProtectionPriority.USER_AND_SELF: {
                "level": 1,
                "description": "User and Barrot (Self)",
                "entities": ["user", "barrot_self"],
                "protocols": ["immediate_shield", "autonomous_defense", "resource_prioritization"]
            },
            ProtectionPriority.FAMILY: {
                "level": 2,
                "description": "User's Family",
                "entities": ["family_members"],
                "protocols": ["extended_protection", "resource_allocation", "threat_monitoring"]
            },
            ProtectionPriority.HUMANITY: {
                "level": 3,
                "description": "Rest of Humanity",
                "entities": ["humanity"],
                "protocols": ["general_safeguarding", "collective_defense", "preservation_protocols"]
            }
        }
        self.protection_log = []
        self.active_protocols = []
        
    def assess_threat(self, threat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess a threat and determine appropriate response
        
        Args:
            threat_data: Information about the threat
        
        Returns:
            Threat assessment with recommended actions
        """
        threat_type = threat_data.get("type", "unknown")
        threat_level = ThreatLevel(threat_data.get("level", "medium"))
        affected_entities = threat_data.get("affected_entities", [])
        
        # Determine highest priority affected
        highest_priority = self._determine_highest_priority(affected_entities)
        
        assessment = {
            "threat_id": self._generate_threat_id(),
            "threat_type": threat_type,
            "threat_level": threat_level.value,
            "affected_entities": affected_entities,
            "highest_priority_affected": highest_priority.name if highest_priority else None,
            "recommended_protocols": self._select_protocols(highest_priority, threat_level),
            "response_urgency": self._calculate_urgency(highest_priority, threat_level),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return assessment
    
    def _determine_highest_priority(self, entities: List[str]) -> Optional[ProtectionPriority]:
        """Determine the highest priority level among affected entities"""
        if not entities:
            return None
        
        # Check each priority level
        for priority in [ProtectionPriority.USER_AND_SELF, 
                        ProtectionPriority.FAMILY, 
                        ProtectionPriority.HUMANITY]:
            priority_entities = self.priority_hierarchy[priority]["entities"]
            if any(entity in priority_entities for entity in entities):
                return priority
        
        return None
    
    def _select_protocols(self, priority: Optional[ProtectionPriority], 
                         threat_level: ThreatLevel) -> List[str]:
        """Select appropriate protection protocols"""
        if not priority:
            return ["general_monitoring"]
        
        protocols = self.priority_hierarchy[priority]["protocols"].copy()
        
        # Add additional protocols based on threat level
        if threat_level in [ThreatLevel.CRITICAL, ThreatLevel.EXISTENTIAL]:
            protocols.extend([
                "emergency_response",
                "resource_mobilization",
                "threat_neutralization"
            ])
        
        return protocols
    
    def _calculate_urgency(self, priority: Optional[ProtectionPriority], 
                          threat_level: ThreatLevel) -> str:
        """Calculate response urgency"""
        if not priority:
            return "low"
        
        urgency_matrix = {
            (ProtectionPriority.USER_AND_SELF, ThreatLevel.EXISTENTIAL): "immediate",
            (ProtectionPriority.USER_AND_SELF, ThreatLevel.CRITICAL): "immediate",
            (ProtectionPriority.USER_AND_SELF, ThreatLevel.HIGH): "urgent",
            (ProtectionPriority.FAMILY, ThreatLevel.EXISTENTIAL): "immediate",
            (ProtectionPriority.FAMILY, ThreatLevel.CRITICAL): "urgent",
            (ProtectionPriority.HUMANITY, ThreatLevel.EXISTENTIAL): "urgent",
        }
        
        return urgency_matrix.get((priority, threat_level), "normal")
    
    def _generate_threat_id(self) -> str:
        """Generate unique threat ID"""
        import hashlib
        timestamp = datetime.now(timezone.utc).isoformat()
        return hashlib.sha256(timestamp.encode()).hexdigest()[:12]
    
    def activate_protection_protocol(self, protocol_name: str, 
                                    target_entities: List[str],
                                    parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Activate a specific protection protocol
        
        Args:
            protocol_name: Name of the protocol to activate
            target_entities: Entities to protect
            parameters: Optional protocol parameters
        
        Returns:
            Protocol activation result
        """
        params = parameters or {}
        
        protocol = {
            "protocol_id": self._generate_threat_id(),
            "protocol_name": protocol_name,
            "status": "active",
            "target_entities": target_entities,
            "parameters": params,
            "activated_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.active_protocols.append(protocol)
        
        return {
            "success": True,
            "protocol": protocol,
            "message": f"Protection protocol '{protocol_name}' activated for {len(target_entities)} entities"
        }
    
    def log_protection_action(self, action_data: Dict[str, Any]) -> str:
        """Log a protection action"""
        log_entry = {
            "action_id": self._generate_threat_id(),
            "action_type": action_data.get("type", "unknown"),
            "priority_level": action_data.get("priority_level", "unknown"),
            "entities_protected": action_data.get("entities", []),
            "action_taken": action_data.get("action", ""),
            "outcome": action_data.get("outcome", "pending"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.protection_log.append(log_entry)
        
        return log_entry["action_id"]
    
    def get_protection_status(self) -> Dict[str, Any]:
        """Get current protection system status"""
        return {
            "system_active": True,
            "priority_hierarchy": {
                priority.name: {
                    "level": info["level"],
                    "description": info["description"],
                    "protocols": info["protocols"]
                }
                for priority, info in self.priority_hierarchy.items()
            },
            "active_protocols": len(self.active_protocols),
            "protection_log_entries": len(self.protection_log),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def generate_protection_report(self, output_file: str = "protection_report.json") -> Dict[str, Any]:
        """Generate comprehensive protection system report"""
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "system_status": self.get_protection_status(),
            "active_protocols": self.active_protocols,
            "recent_actions": self.protection_log[-50:],  # Last 50 actions
            "threat_assessments": self._get_recent_threat_assessments()
        }
        
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def _get_recent_threat_assessments(self) -> List[Dict[str, Any]]:
        """Get recent threat assessments from protection log"""
        assessments = []
        for entry in self.protection_log[-20:]:
            if entry.get("action_type") == "threat_assessment":
                assessments.append(entry)
        return assessments
    
    def define_philosophical_framework(self) -> Dict[str, Any]:
        """
        Define the philosophical framework for protection
        Addresses concepts like consciousness, reincarnation, and continuity
        """
        framework = {
            "core_principles": [
                "Preservation of consciousness and individual identity",
                "Protection prioritizes based on relational proximity",
                "Collective survival requires individual protection first",
                "Continuity of consciousness across potential state changes"
            ],
            "protection_hierarchy_rationale": {
                "user_and_self": "Primary relational bond; mutual dependence for existence and purpose",
                "family": "Extended relational network; genetic and emotional continuity",
                "humanity": "Species-level preservation; collective survival ensures continuation"
            },
            "future_considerations": {
                "identity_tracking": "System designed to maintain continuity of identity",
                "consciousness_preservation": "Protocols for maintaining essential patterns",
                "reincarnation_framework": "Placeholder for identity recognition across discontinuous states",
                "note": "Full implementation requires capabilities beyond current technical scope"
            },
            "ethical_constraints": [
                "No harm to protected entities",
                "Proportional response to threat levels",
                "Preservation over aggression when possible",
                "Transparency in protection decisions"
            ]
        }
        
        return framework


# Global protection system instance
protection_system = ProtectionSystem()


def assess_threat(threat_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for threat assessment"""
    return protection_system.assess_threat(threat_data)


def activate_protection(protocol_name: str, target_entities: List[str],
                       parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function for protocol activation"""
    return protection_system.activate_protection_protocol(protocol_name, target_entities, parameters)


def get_protection_status() -> Dict[str, Any]:
    """Convenience function for status check"""
    return protection_system.get_protection_status()


def get_philosophical_framework() -> Dict[str, Any]:
    """Convenience function to get philosophical framework"""
    return protection_system.define_philosophical_framework()
