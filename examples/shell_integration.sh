#!/bin/bash
# Example: Shell Script Integration
# Demonstrates how to use snapshots in shell scripts

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PARENT_DIR"

echo "=================================================="
echo "Barrot Snapshot - Shell Integration Example"
echo "=================================================="
echo ""

# Example 1: Track deployment start
echo "=== Example 1: Track Deployment Start ==="
python3 snapshot_generator.py action "deployment_start" \
  '{"environment": "production", "version": "2.0.0", "initiator": "deploy-script"}'
echo ""

# Example 2: Simulate build process
echo "=== Example 2: Track Build Process ==="
echo "Building application..."
sleep 1
python3 snapshot_generator.py action "build_complete" \
  '{"module": "main-app", "duration": "45s", "status": "success"}'
echo ""

# Example 3: Track tests
echo "=== Example 3: Track Test Execution ==="
echo "Running tests..."
sleep 1
python3 snapshot_generator.py action "test_execution" \
  '{"suite": "integration", "passed": 28, "failed": 0, "skipped": 2}'
echo ""

# Example 4: Generate periodic snapshot
echo "=== Example 4: Generate Periodic Snapshot ==="
python3 snapshot_generator.py periodic > /dev/null
echo "Periodic snapshot generated"
echo ""

# Example 5: View recent actions
echo "=== Example 5: View Recent Actions ==="
python3 snapshot_viewer.py actions 3
echo ""

# Example 6: Generate summary
echo "=== Example 6: Snapshot Summary ==="
python3 snapshot_generator.py summary
echo ""

echo "=================================================="
echo "Shell integration examples completed!"
echo "=================================================="
