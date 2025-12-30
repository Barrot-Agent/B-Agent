#!/usr/bin/env python3
"""
Example usage of the pingpong request emission system.

This script demonstrates how to use the emit_pingpong_request function
to generate requests that will be handled by Sean's 22-agent entanglement system.
"""

from pingpong import emit_pingpong_request

# Example 1: Simple health check
print("Example 1: Health check request")
emit_pingpong_request({
    "type": "health_check",
    "priority": "normal",
    "source": "barrot-agent"
})
print()

# Example 2: Data synchronization request
print("\nExample 2: Data sync request")
emit_pingpong_request({
    "type": "data_sync",
    "data_source": "memory-bundles",
    "priority": "high",
    "target_agents": [1, 2, 3, 4, 5]
})
print()

# Example 3: System monitoring request
print("\nExample 3: System monitoring request")
emit_pingpong_request({
    "type": "system_monitor",
    "metrics": ["cpu", "memory", "disk", "network"],
    "interval_seconds": 300,
    "alert_threshold": 80
})
