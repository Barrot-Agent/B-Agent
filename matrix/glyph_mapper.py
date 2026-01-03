#!/usr/bin/env python3
"""
Glyph Mapper
Maps emitted glyphs to follow-up actions and tracks dependencies.
Supports user-defined glyphs with extended metadata.
"""

import json
import yaml
from pathlib import Path
from datetime import datetime, timezone

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
GLYPHS_PATH = REPO_ROOT / "glyphs"
BUNDLES_PATH = REPO_ROOT / "memory-bundles"
TRACE_LOG_PATH = BUNDLES_PATH / "TRACE_LOG.md"
GLYPH_MAPPING_PATH = BUNDLES_PATH / "glyph_mappings.json"
USER_GLYPHS_PATH = GLYPHS_PATH / "user_defined"

# Predefined glyph action mappings
GLYPH_ACTION_MAPPINGS = {
    "SELF_ALIGNMENT_GLYPH": {
        "actions": [
            "Review MANIFEST_PATCH.md for suggested changes",
            "Verify cognition node execution patterns",
            "Check for drift in last 3 runs"
        ],
        "priority": "high",
        "auto_trigger": ["node_self_reflect"]
    },
    "COUNCIL_ALIGNMENT_GLYPH": {
        "actions": [
            "Record consensus decision in decision log",
            "Update agent weight history",
            "Evaluate perspective coverage"
        ],
        "priority": "medium",
        "auto_trigger": ["council_vote"]
    },
    "MEMORY_COMPRESSION_GLYPH": {
        "actions": [
            "Verify compressed archives integrity",
            "Update memory metrics dashboard",
            "Schedule next compression cycle"
        ],
        "priority": "low",
        "auto_trigger": ["node_memory_compressor"]
    },
    "GLYPH_MISALIGNMENT_RECOVERY": {
        "actions": [
            "Document root cause of misalignment",
            "Apply corrective measures",
            "Verify alignment restoration",
            "Log recovery procedures"
        ],
        "priority": "critical",
        "auto_trigger": ["misalignment_detector"]
    },
    "SESSION_TRACE_GLYPH": {
        "actions": [
            "Archive session transcript",
            "Extract key cognition events",
            "Update session history"
        ],
        "priority": "medium",
        "auto_trigger": ["node_session_ingestor"]
    },
    "OVERLAP_RESOLUTION_GLYPH": {
        "actions": [
            "Scan memory bundles for semantic overlap",
            "Detect restated directives",
            "Collapse redundant cognition into unified threads",
            "Update overlap resolution metrics"
        ],
        "priority": "high",
        "auto_trigger": ["node_overlap_resolver"]
    },
    "SYNCHRONIZATION_GLYPH": {
        "actions": [
            "Identify asynchronous proximities",
            "Align temporally distant data",
            "Synchronize cognition clusters",
            "Update synchronization status"
        ],
        "priority": "high",
        "auto_trigger": ["node_async_proximity_aligner"]
    },
    "COGNITION_ALIGNMENT_GLYPH": {
        "actions": [
            "Align cognition fragments with latent alignment",
            "Synchronize symbolic patterns across domains",
            "Update cognition alignment metrics",
            "Verify alignment integrity"
        ],
        "priority": "high",
        "auto_trigger": ["node_async_proximity_aligner"]
    },
    "CONTINUOUS_SYNCHRONIZATION_GLYPH": {
        "actions": [
            "Maintain real-time synchronization loop",
            "Reconcile new inputs with existing structures",
            "Monitor memory-bundles, matrix, tool_profiles, and manifest",
            "Update continuous synchronization status"
        ],
        "priority": "critical",
        "auto_trigger": ["node_continuous_sync_engine"]
    }
}

def load_glyph_mappings():
    """Load existing glyph mappings"""
    if GLYPH_MAPPING_PATH.exists():
        with open(GLYPH_MAPPING_PATH, 'r') as f:
            return json.load(f)
    return {"mappings": {}, "user_defined": {}, "history": []}

def save_glyph_mappings(mappings):
    """Save glyph mappings"""
    with open(GLYPH_MAPPING_PATH, 'w') as f:
        json.dump(mappings, f, indent=2)

def register_glyph_emission(glyph_name, emitter_node, context=None):
    """Register a glyph emission and map to follow-up actions"""
    mappings = load_glyph_mappings()
    
    timestamp = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
    
    # Get action mapping
    action_map = GLYPH_ACTION_MAPPINGS.get(glyph_name, {})
    if not action_map and glyph_name in mappings.get("user_defined", {}):
        action_map = mappings["user_defined"][glyph_name]
    
    # Create emission record
    emission_record = {
        "timestamp": timestamp,
        "glyph_name": glyph_name,
        "emitter_node": emitter_node,
        "context": context or {},
        "actions": action_map.get("actions", []),
        "priority": action_map.get("priority", "medium"),
        "status": "pending"
    }
    
    # Add to history
    if "history" not in mappings:
        mappings["history"] = []
    mappings["history"].append(emission_record)
    
    # Keep only last 200 emissions
    if len(mappings["history"]) > 200:
        mappings["history"] = mappings["history"][-200:]
    
    save_glyph_mappings(mappings)
    
    # Log to TRACE_LOG
    log_glyph_mapping(emission_record)
    
    print(f"[GLYPH_MAPPER] Registered {glyph_name} from {emitter_node}")
    print(f"[GLYPH_MAPPER] Follow-up actions: {len(emission_record['actions'])}")
    
    return emission_record

def log_glyph_mapping(emission_record):
    """Log glyph mapping to TRACE_LOG.md"""
    log_entry = f"""
### Glyph Mapping: {emission_record['glyph_name']}
**Timestamp:** {emission_record['timestamp']}  
**Emitter:** {emission_record['emitter_node']}  
**Priority:** {emission_record['priority']}

**Follow-up Actions:**
"""
    
    for i, action in enumerate(emission_record['actions'], 1):
        log_entry += f"{i}. {action}\n"
    
    if emission_record.get('context'):
        log_entry += f"\n**Context:** {emission_record['context']}\n"
    
    with open(TRACE_LOG_PATH, 'a') as f:
        f.write(log_entry)

def define_user_glyph(glyph_name, description, actions, priority="medium", metadata=None):
    """Define a user-defined glyph with extended metadata"""
    USER_GLYPHS_PATH.mkdir(exist_ok=True)
    
    mappings = load_glyph_mappings()
    
    # Create user glyph definition
    user_glyph = {
        "name": glyph_name,
        "description": description,
        "actions": actions,
        "priority": priority,
        "metadata": metadata or {},
        "created_at": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
        "version": "1.0.0"
    }
    
    # Save to user_defined mappings
    if "user_defined" not in mappings:
        mappings["user_defined"] = {}
    mappings["user_defined"][glyph_name] = user_glyph
    save_glyph_mappings(mappings)
    
    # Create YAML file for the glyph
    glyph_file = USER_GLYPHS_PATH / f"{glyph_name.lower()}.yml"
    glyph_content = f"""glyph_name: {glyph_name}
glyph_id: USER-{len(mappings['user_defined']):03d}
version: 1.0.0
timestamp: {user_glyph['created_at']}Z
user_defined: true

description: >
  {description}

symbolic_representation: "✨ 👤 ⚡"

properties:
  dimension: user_defined
  mutability: configurable
  trigger: custom
  
attributes:
  - user_defined
  - custom_logic
  - extended_metadata

follow_up_actions:
{chr(10).join([f"  - {action}" for action in actions])}

priority: {priority}

metadata:
{chr(10).join([f"  {k}: {v}" for k, v in (metadata or {}).items()])}

integration_points:
  - user_workflows
  - custom_automation
  - extended_cognition

usage_context: >
  User-defined glyph for custom workflows and automation.
  Supports extended metadata for future scalability.
"""
    
    with open(glyph_file, 'w') as f:
        f.write(glyph_content)
    
    print(f"[GLYPH_MAPPER] Created user-defined glyph: {glyph_name}")
    print(f"[GLYPH_MAPPER] File: {glyph_file}")
    
    return user_glyph

def track_node_dependency(source_node, target_node, dependency_type="data_flow", context=None):
    """Track interdependencies between cognition nodes"""
    mappings = load_glyph_mappings()
    
    if "dependencies" not in mappings:
        mappings["dependencies"] = []
    
    dependency_record = {
        "timestamp": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
        "source_node": source_node,
        "target_node": target_node,
        "dependency_type": dependency_type,
        "context": context or {}
    }
    
    mappings["dependencies"].append(dependency_record)
    
    # Keep only last 100 dependencies
    if len(mappings["dependencies"]) > 100:
        mappings["dependencies"] = mappings["dependencies"][-100:]
    
    save_glyph_mappings(mappings)
    
    # Log to TRACE_LOG
    log_dependency(dependency_record)
    
    return dependency_record

def log_dependency(dependency_record):
    """Log node dependency to TRACE_LOG.md"""
    log_entry = f"""
### Node Dependency: {dependency_record['source_node']} → {dependency_record['target_node']}
**Timestamp:** {dependency_record['timestamp']}  
**Type:** {dependency_record['dependency_type']}  
**Context:** {dependency_record.get('context', 'N/A')}

"""
    
    with open(TRACE_LOG_PATH, 'a') as f:
        f.write(log_entry)

def log_corrective_action(glyph_name, issue_detected, corrective_actions, outcome):
    """Automate logging of corrective actions for GLYPH_MISALIGNMENT_RECOVERY"""
    timestamp = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
    
    log_entry = f"""
## GLYPH_MISALIGNMENT_RECOVERY Event: {timestamp}Z

**Issue Detected:** {issue_detected}

### Corrective Actions Taken:
"""
    
    for i, action in enumerate(corrective_actions, 1):
        log_entry += f"{i}. {action}\n"
    
    log_entry += f"""
**Outcome:** {outcome}
**Recovery Status:** {'Success' if 'success' in outcome.lower() else 'In Progress'}

---
"""
    
    with open(TRACE_LOG_PATH, 'a') as f:
        f.write(log_entry)
    
    print(f"[GLYPH_MAPPER] Logged corrective action for {glyph_name}")

def main():
    """Demonstration of glyph mapping capabilities"""
    print("[GLYPH_MAPPER] Initializing glyph mapping system...")
    
    # Example: Register a glyph emission
    register_glyph_emission(
        "COUNCIL_ALIGNMENT_GLYPH",
        "council_vote",
        {"consensus_reached": True, "avg_agreement": 0.72}
    )
    
    # Example: Define a user glyph
    define_user_glyph(
        "CUSTOM_WORKFLOW_GLYPH",
        "Custom glyph for specialized workflow automation",
        [
            "Trigger custom workflow A",
            "Update workflow metrics",
            "Notify stakeholders"
        ],
        priority="medium",
        metadata={
            "owner": "system",
            "workflow_id": "WF-001",
            "version": "1.0.0"
        }
    )
    
    # Example: Track node dependency
    track_node_dependency(
        "council_vote",
        "node_self_reflect",
        "consensus_influence",
        {"influence_score": 0.8}
    )
    
    # Example: Log corrective action
    log_corrective_action(
        "GLYPH_MISALIGNMENT_RECOVERY",
        "Drift detected in cognition pattern execution",
        [
            "Analyzed last 5 execution cycles",
            "Identified inconsistent node firing",
            "Applied weight normalization",
            "Verified pattern alignment"
        ],
        "Successfully restored alignment. All nodes firing consistently."
    )
    
    print("[GLYPH_MAPPER] Demonstration complete")

if __name__ == "__main__":
    main()
