"""
Protocol Logger - Comprehensive logging system for Barrot-Agent
Continuously logs all protocols, operations, and decision-making processes
for future reference and analysis
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from collections import defaultdict
import hashlib


class ProtocolLogger:
    """
    Comprehensive protocol logging system that continuously grows
    Ensures all protocols are available for future usage
    """
    
    def __init__(self, log_file: str = "protocols_log.jsonl"):
        self.log_file = log_file
        self.session_id = self._generate_session_id()
        self.protocol_count = 0
        self.protocol_index = {}
        self.ensure_log_file_exists()
        
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now(timezone.utc).isoformat()
        return hashlib.sha256(timestamp.encode()).hexdigest()[:16]
    
    def ensure_log_file_exists(self):
        """Ensure log file exists"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write(json.dumps({
                    "type": "log_initialization",
                    "session_id": self.session_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }) + "\n")
    
    def log_protocol(self, protocol_type: str, protocol_data: Dict[str, Any],
                    priority: str = "normal", tags: Optional[List[str]] = None) -> str:
        """
        Log a protocol execution with full details
        
        Args:
            protocol_type: Type of protocol (e.g., "reasoning", "ingestion", "conflict_resolution")
            protocol_data: Full protocol data
            priority: Priority level (low, normal, high, critical)
            tags: Optional tags for categorization
        
        Returns:
            protocol_id for future reference
        """
        self.protocol_count += 1
        protocol_id = f"{self.session_id}_{self.protocol_count:06d}"
        
        log_entry = {
            "protocol_id": protocol_id,
            "session_id": self.session_id,
            "protocol_type": protocol_type,
            "priority": priority,
            "tags": tags or [],
            "data": protocol_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Write to log file (append mode)
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
        
        # Update index
        self.protocol_index[protocol_id] = {
            "protocol_type": protocol_type,
            "priority": priority,
            "timestamp": log_entry["timestamp"]
        }
        
        return protocol_id
    
    def log_conflict_resolution(self, conflict: str, resolution: str,
                                method: str, confidence: float) -> str:
        """Log conflict resolution protocol"""
        return self.log_protocol(
            "conflict_resolution",
            {
                "conflict": conflict,
                "resolution": resolution,
                "method": method,
                "confidence": confidence,
                "status": "resolved"
            },
            priority="high",
            tags=["conflict", "resolution", "paradox"]
        )
    
    def log_cognition_sprint(self, sprint_type: str, objective: str,
                            duration_seconds: float, outcome: Dict[str, Any]) -> str:
        """Log cognition sprint execution"""
        return self.log_protocol(
            "cognition_sprint",
            {
                "sprint_type": sprint_type,
                "objective": objective,
                "duration_seconds": duration_seconds,
                "outcome": outcome,
                "status": "completed"
            },
            priority="high",
            tags=["cognition", "sprint", "optimization"]
        )
    
    def log_data_integration(self, source: str, target: str,
                            integration_method: str, result: Dict[str, Any]) -> str:
        """Log data integration protocol"""
        return self.log_protocol(
            "data_integration",
            {
                "source": source,
                "target": target,
                "method": integration_method,
                "result": result,
                "status": "integrated"
            },
            priority="normal",
            tags=["data", "integration", "merge"]
        )
    
    def log_protection_action(self, threat_level: str, protected_entities: List[str],
                             action_taken: str, outcome: str) -> str:
        """Log protection protocol action"""
        return self.log_protocol(
            "protection_action",
            {
                "threat_level": threat_level,
                "protected_entities": protected_entities,
                "action": action_taken,
                "outcome": outcome,
                "priority_order": ["user_and_self", "family", "humanity"]
            },
            priority="critical",
            tags=["protection", "safety", "security"]
        )
    
    def query_protocols(self, protocol_type: Optional[str] = None,
                       tags: Optional[List[str]] = None,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """
        Query logged protocols with filters
        
        Args:
            protocol_type: Filter by protocol type
            tags: Filter by tags (any match)
            limit: Maximum number of results
        
        Returns:
            List of matching protocol entries
        """
        results = []
        
        if not os.path.exists(self.log_file):
            return results
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    # Apply filters
                    if protocol_type and entry.get("protocol_type") != protocol_type:
                        continue
                    
                    if tags:
                        entry_tags = set(entry.get("tags", []))
                        if not any(tag in entry_tags for tag in tags):
                            continue
                    
                    results.append(entry)
                    
                    if len(results) >= limit:
                        break
                        
                except json.JSONDecodeError:
                    continue
        
        return results
    
    def get_protocol_statistics(self) -> Dict[str, Any]:
        """Get statistics about logged protocols"""
        stats = {
            "total_protocols": 0,
            "by_type": defaultdict(int),
            "by_priority": defaultdict(int),
            "by_session": defaultdict(int)
        }
        
        if not os.path.exists(self.log_file):
            return dict(stats)
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    stats["total_protocols"] += 1
                    
                    protocol_type = entry.get("protocol_type", "unknown")
                    stats["by_type"][protocol_type] += 1
                    
                    priority = entry.get("priority", "normal")
                    stats["by_priority"][priority] += 1
                    
                    session = entry.get("session_id", "unknown")
                    stats["by_session"][session] += 1
                    
                except json.JSONDecodeError:
                    continue
        
        # Convert defaultdicts to regular dicts
        return {
            "total_protocols": stats["total_protocols"],
            "by_type": dict(stats["by_type"]),
            "by_priority": dict(stats["by_priority"]),
            "by_session": dict(stats["by_session"]),
            "current_session": self.session_id
        }
    
    def export_protocols_summary(self, output_file: str = "protocols_summary.json"):
        """Export comprehensive protocols summary"""
        summary = {
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "statistics": self.get_protocol_statistics(),
            "recent_protocols": self.query_protocols(limit=50),
            "protocol_index": self.protocol_index
        }
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary


# Global protocol logger instance
protocol_logger = ProtocolLogger()


def log_protocol(protocol_type: str, protocol_data: Dict[str, Any],
                priority: str = "normal", tags: Optional[List[str]] = None) -> str:
    """Convenience function for protocol logging"""
    return protocol_logger.log_protocol(protocol_type, protocol_data, priority, tags)


def log_conflict_resolution(conflict: str, resolution: str,
                           method: str, confidence: float) -> str:
    """Convenience function for conflict resolution logging"""
    return protocol_logger.log_conflict_resolution(conflict, resolution, method, confidence)


def log_protection_action(threat_level: str, protected_entities: List[str],
                         action_taken: str, outcome: str) -> str:
    """Convenience function for protection action logging"""
    return protocol_logger.log_protection_action(threat_level, protected_entities, action_taken, outcome)
