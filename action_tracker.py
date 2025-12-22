#!/usr/bin/env python3
"""
Barrot Action Tracker
Simple wrapper to track actions in Barrot workflows
"""

import json
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path


class ActionTracker:
    """Track actions with automatic snapshot generation"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.generator_path = self.base_dir / "snapshot_generator.py"
        
        # Validate generator path exists and is a file
        if not self.generator_path.exists() or not self.generator_path.is_file():
            raise FileNotFoundError(f"Snapshot generator not found at {self.generator_path}")
    
    def track_action(self, action_type, details, status="executing"):
        """
        Track an action with automatic snapshot generation
        
        Args:
            action_type: Type of action (e.g., "build", "test", "deploy")
            details: Dictionary with action details
            status: Status of the action ("executing", "completed", "failed")
        """
        try:
            cmd = [
                "python3",
                str(self.generator_path),
                "action",
                action_type,
                json.dumps(details)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse output to get snapshot ID
            output_lines = result.stdout.strip().split('\n')
            if output_lines:
                first_line = output_lines[0]
                if 'Generated action snapshot:' in first_line:
                    snapshot_id = first_line.split(':')[1].strip()
                    return snapshot_id
            
            return None
            
        except subprocess.CalledProcessError as e:
            print(f"Error generating snapshot: {e}", file=sys.stderr)
            return None
    
    def track_start(self, action_type, details=None):
        """Track the start of an action"""
        details = details or {}
        details["timestamp"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        return self.track_action(action_type, details, status="executing")
    
    def track_complete(self, action_type, details=None):
        """Track the completion of an action"""
        details = details or {}
        details["timestamp"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        details["status"] = "completed"
        return self.track_action(action_type, details, status="completed")
    
    def track_failure(self, action_type, error, details=None):
        """Track a failed action"""
        details = details or {}
        details["timestamp"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        details["error"] = str(error)
        details["status"] = "failed"
        return self.track_action(action_type, details, status="failed")


class TrackedAction:
    """Context manager for tracking actions"""
    
    def __init__(self, tracker, action_type, details=None):
        self.tracker = tracker
        self.action_type = action_type
        self.details = details or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now(timezone.utc)
        self.tracker.track_start(self.action_type, self.details)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        self.details["duration_seconds"] = duration
        
        if exc_type is None:
            # Success
            self.tracker.track_complete(self.action_type, self.details)
        else:
            # Failure
            self.tracker.track_failure(self.action_type, exc_val, self.details)
        
        # Don't suppress exceptions
        return False


def main():
    """CLI interface for action tracking"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python action_tracker.py track <type> <details_json>")
        print("  python action_tracker.py start <type> <details_json>")
        print("  python action_tracker.py complete <type> <details_json>")
        print("  python action_tracker.py fail <type> <error> <details_json>")
        print("\nExamples:")
        print('  python action_tracker.py track "build" \'{"module": "core"}\'')
        print('  python action_tracker.py start "deployment" \'{"env": "prod"}\'')
        sys.exit(1)
    
    tracker = ActionTracker()
    command = sys.argv[1]
    
    if command == "track":
        if len(sys.argv) < 4:
            print("Error: track requires action type and details")
            sys.exit(1)
        
        action_type = sys.argv[2]
        try:
            details = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in details: {e}", file=sys.stderr)
            sys.exit(1)
        snapshot_id = tracker.track_action(action_type, details)
        print(f"Tracked action: {snapshot_id}")
    
    elif command == "start":
        if len(sys.argv) < 3:
            print("Error: start requires action type")
            sys.exit(1)
        
        action_type = sys.argv[2]
        try:
            details = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in details: {e}", file=sys.stderr)
            sys.exit(1)
        snapshot_id = tracker.track_start(action_type, details)
        print(f"Started tracking: {snapshot_id}")
    
    elif command == "complete":
        if len(sys.argv) < 3:
            print("Error: complete requires action type")
            sys.exit(1)
        
        action_type = sys.argv[2]
        try:
            details = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in details: {e}", file=sys.stderr)
            sys.exit(1)
        snapshot_id = tracker.track_complete(action_type, details)
        print(f"Completed tracking: {snapshot_id}")
    
    elif command == "fail":
        if len(sys.argv) < 4:
            print("Error: fail requires action type and error")
            sys.exit(1)
        
        action_type = sys.argv[2]
        error = sys.argv[3]
        try:
            details = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in details: {e}", file=sys.stderr)
            sys.exit(1)
        snapshot_id = tracker.track_failure(action_type, error, details)
        print(f"Failed tracking: {snapshot_id}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
