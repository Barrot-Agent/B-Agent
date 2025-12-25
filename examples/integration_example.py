#!/usr/bin/env python3
"""
Example: Basic Snapshot Integration
Demonstrates how to integrate snapshots into your workflows
"""

import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from snapshot_generator import BarrotSnapshotGenerator
from action_tracker import ActionTracker, TrackedAction


def example_basic_snapshot():
    """Example 1: Generate a basic snapshot"""
    print("=== Example 1: Basic Snapshot ===\n")
    
    generator = BarrotSnapshotGenerator()
    
    # Generate a periodic snapshot
    snapshot_id, snapshot = generator.generate_periodic_snapshot()
    print(f"Generated periodic snapshot: {snapshot_id}")
    print(f"System health: {snapshot['system_state']['health']}")
    print()


def example_action_tracking():
    """Example 2: Track individual actions"""
    print("=== Example 2: Action Tracking ===\n")
    
    tracker = ActionTracker()
    
    # Track a build action
    snapshot_id = tracker.track_action(
        "build",
        {
            "module": "core",
            "compiler": "gcc",
            "result": "success"
        }
    )
    print(f"Tracked build action: {snapshot_id}")
    
    # Track a test action
    snapshot_id = tracker.track_action(
        "test",
        {
            "suite": "unit",
            "passed": 42,
            "failed": 0,
            "coverage": "95%"
        }
    )
    print(f"Tracked test action: {snapshot_id}")
    print()


def example_context_manager():
    """Example 3: Use context manager for automatic tracking"""
    print("=== Example 3: Context Manager ===\n")
    
    tracker = ActionTracker()
    
    # Automatically track start and completion
    try:
        with TrackedAction(tracker, "deployment", {"environment": "staging"}):
            print("Performing deployment...")
            # Simulated deployment work
            import time
            time.sleep(0.5)
            print("Deployment completed!")
    except Exception as e:
        print(f"Deployment failed: {e}")
    
    print()


def example_failure_tracking():
    """Example 4: Track failures"""
    print("=== Example 4: Failure Tracking ===\n")
    
    tracker = ActionTracker()
    
    try:
        with TrackedAction(tracker, "data_processing", {"dataset": "users"}):
            print("Processing data...")
            # Simulate a failure
            raise ValueError("Invalid data format")
    except ValueError as e:
        print(f"Error caught: {e}")
    
    print("Failure was tracked in snapshot\n")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("Barrot Snapshot Integration Examples")
    print("="*60 + "\n")
    
    example_basic_snapshot()
    example_action_tracking()
    example_context_manager()
    example_failure_tracking()
    
    print("="*60)
    print("All examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
