#!/usr/bin/env python3
"""
Barrot Snapshot Generator
Generates snapshots detailing actions and system state for real-time monitoring
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import yaml


class BarrotSnapshotGenerator:
    """Main class for generating Barrot snapshots"""
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.snapshots_dir = self.base_dir / "snapshots"
        self.memory_bundles_dir = self.base_dir / "memory-bundles"
        
        # Ensure snapshots directory exists
        self.snapshots_dir.mkdir(exist_ok=True)
    
    def generate_action_snapshot(self, action_type, action_details, status="executing"):
        """
        Generate a snapshot for a specific action as soon as it's executed
        
        Args:
            action_type: Type of action (e.g., "build", "deploy", "test", "workflow")
            action_details: Dictionary with action details
            status: Status of the action ("executing", "completed", "failed")
        """
        timestamp = datetime.now(timezone.utc)
        snapshot_id = f"action_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"
        
        snapshot = {
            "snapshot_id": snapshot_id,
            "snapshot_type": "action",
            "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
            "action": {
                "type": action_type,
                "status": status,
                "details": action_details,
                "started_at": timestamp.isoformat().replace("+00:00", "Z")
            },
            "metadata": {
                "generated_by": "BarrotSnapshotGenerator",
                "version": "1.0.0"
            }
        }
        
        # Save snapshot to file
        snapshot_file = self.snapshots_dir / f"{snapshot_id}.json"
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        # Also append to action log
        self._append_to_action_log(snapshot)
        
        return snapshot_id, snapshot
    
    def generate_periodic_snapshot(self):
        """
        Generate a comprehensive snapshot of current build and state
        Called every 30 minutes to provide regular updates
        """
        timestamp = datetime.now(timezone.utc)
        snapshot_id = f"periodic_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        snapshot = {
            "snapshot_id": snapshot_id,
            "snapshot_type": "periodic",
            "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
            "interval": "30_minutes",
            "system_state": self._capture_system_state(),
            "build_state": self._capture_build_state(),
            "rail_status": self._capture_rail_status(),
            "active_processes": self._capture_active_processes(),
            "workflows": self._capture_workflows(),
            "cognitive_state": self._capture_cognitive_state(),
            "task_progress": self._capture_task_progress(),
            "metadata": {
                "generated_by": "BarrotSnapshotGenerator",
                "version": "1.0.0"
            }
        }
        
        # Save snapshot to file
        snapshot_file = self.snapshots_dir / f"{snapshot_id}.json"
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        # Update latest snapshot reference
        latest_file = self.snapshots_dir / "latest_periodic.json"
        with open(latest_file, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        return snapshot_id, snapshot
    
    def _capture_system_state(self):
        """Capture current system state"""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "uptime": "active",
            "health": "operational"
        }
    
    def _capture_build_state(self):
        """Capture current build state from build_manifest.yaml"""
        build_manifest_path = self.base_dir / "build_manifest.yaml"
        
        try:
            if build_manifest_path.exists():
                with open(build_manifest_path, 'r') as f:
                    manifest = yaml.safe_load(f)
                    
                    # Validate manifest structure
                    if not isinstance(manifest, dict):
                        return {"error": "Invalid manifest structure: not a dictionary"}
                    
                    timestamp = manifest.get("timestamp", "UNKNOWN")
                    # Convert datetime to string if needed
                    if isinstance(timestamp, datetime):
                        timestamp = timestamp.isoformat().replace("+00:00", "Z")
                    
                    return {
                        "build_signature": manifest.get("build_signature", "UNKNOWN"),
                        "timestamp": timestamp,
                        "modules": manifest.get("modules", []) if isinstance(manifest.get("modules"), list) else [],
                        "provenance_hash": manifest.get("provenance_hash", "UNKNOWN")
                    }
        except Exception as e:
            return {"error": f"Failed to read build manifest: {str(e)}"}
        
        return {"status": "no_build_manifest"}
    
    def _capture_rail_status(self):
        """Capture current rail status from build_manifest.yaml"""
        build_manifest_path = self.base_dir / "build_manifest.yaml"
        
        try:
            if build_manifest_path.exists():
                with open(build_manifest_path, 'r') as f:
                    manifest = yaml.safe_load(f)
                    
                    # Validate manifest structure
                    if not isinstance(manifest, dict):
                        return {"error": "Invalid manifest structure"}
                    
                    rail_status = manifest.get("rail_status", {})
                    # Validate rail_status is a dict
                    if isinstance(rail_status, dict):
                        return rail_status
                    return {}
        except Exception as e:
            return {"error": f"Failed to read rail status: {str(e)}"}
        
        return {}
    
    def _capture_active_processes(self):
        """Capture information about active processes"""
        # This would be expanded to track actual running processes
        return {
            "count": 0,
            "processes": []
        }
    
    def _capture_workflows(self):
        """Capture information about active workflows"""
        return {
            "active": [],
            "completed": [],
            "scheduled": []
        }
    
    def _capture_cognitive_state(self):
        """Capture cognitive enhancements and state"""
        # Read from memory bundles if available
        protocols_file = self.memory_bundles_dir / "protocols" / "registry.json"
        
        try:
            if protocols_file.exists():
                with open(protocols_file, 'r') as f:
                    protocols = json.load(f)
                    return {
                        "protocols": protocols.get("protocols", []),
                        "status": "active"
                    }
        except Exception as e:
            return {"error": f"Failed to read protocols: {str(e)}"}
        
        return {"status": "unknown"}
    
    def _capture_task_progress(self):
        """Capture current task progress"""
        # Read from outcome-relay.md if available
        outcome_relay_path = self.memory_bundles_dir / "outcome-relay.md"
        
        try:
            if outcome_relay_path.exists():
                with open(outcome_relay_path, 'r') as f:
                    lines = f.readlines()
                    # Get last 10 lines for recent progress
                    recent_lines = lines[-10:] if len(lines) > 10 else lines
                    return {
                        "recent_activities": [line.strip() for line in recent_lines if line.strip()],
                        "total_entries": len(lines)
                    }
        except Exception as e:
            return {"error": f"Failed to read outcome relay: {str(e)}"}
        
        return {"status": "no_tasks"}
    
    def _append_to_action_log(self, snapshot):
        """Append action snapshot to continuous action log"""
        action_log_file = self.snapshots_dir / "action_log.jsonl"
        
        with open(action_log_file, 'a') as f:
            f.write(json.dumps(snapshot) + '\n')
    
    def get_latest_snapshots(self, count=10):
        """Retrieve the latest snapshots"""
        snapshot_files = sorted(
            self.snapshots_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        snapshots = []
        for snapshot_file in snapshot_files[:count]:
            if snapshot_file.name in ["latest_periodic.json"]:
                continue
            try:
                with open(snapshot_file, 'r') as f:
                    snapshots.append(json.load(f))
            except Exception:
                pass
        
        return snapshots
    
    def generate_snapshot_summary(self):
        """Generate a summary of all snapshots"""
        all_snapshots = list(self.snapshots_dir.glob("*.json"))
        
        action_snapshots = [s for s in all_snapshots if s.name.startswith("action_")]
        periodic_snapshots = [s for s in all_snapshots if s.name.startswith("periodic_")]
        
        return {
            "total_snapshots": len(all_snapshots),
            "action_snapshots": len(action_snapshots),
            "periodic_snapshots": len(periodic_snapshots),
            "latest_action": max([s.stat().st_mtime for s in action_snapshots]) if action_snapshots else None,
            "latest_periodic": max([s.stat().st_mtime for s in periodic_snapshots]) if periodic_snapshots else None
        }


def main():
    """Main entry point for CLI usage"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python snapshot_generator.py action <type> <details_json>")
        print("  python snapshot_generator.py periodic")
        print("  python snapshot_generator.py summary")
        sys.exit(1)
    
    generator = BarrotSnapshotGenerator()
    command = sys.argv[1]
    
    if command == "action":
        if len(sys.argv) < 4:
            print("Error: action command requires type and details")
            sys.exit(1)
        
        action_type = sys.argv[2]
        try:
            action_details = json.loads(sys.argv[3])
        except json.JSONDecodeError:
            action_details = {"description": sys.argv[3]}
        
        snapshot_id, snapshot = generator.generate_action_snapshot(action_type, action_details)
        print(f"Generated action snapshot: {snapshot_id}")
        print(json.dumps(snapshot, indent=2))
    
    elif command == "periodic":
        snapshot_id, snapshot = generator.generate_periodic_snapshot()
        print(f"Generated periodic snapshot: {snapshot_id}")
        print(json.dumps(snapshot, indent=2))
    
    elif command == "summary":
        summary = generator.generate_snapshot_summary()
        print("Snapshot Summary:")
        print(json.dumps(summary, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
