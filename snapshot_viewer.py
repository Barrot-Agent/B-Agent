#!/usr/bin/env python3
"""
Barrot Snapshot Viewer
View and monitor snapshots in real-time
"""

import json
import os
from datetime import datetime
from pathlib import Path
import sys
import html


class SnapshotViewer:
    """View and analyze Barrot snapshots"""
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.snapshots_dir = self.base_dir / "snapshots"
    
    def view_latest_periodic(self):
        """View the latest periodic snapshot"""
        latest_file = self.snapshots_dir / "latest_periodic.json"
        
        if not latest_file.exists():
            print("No periodic snapshot found yet.")
            return
        
        with open(latest_file, 'r') as f:
            snapshot = json.load(f)
        
        self._display_snapshot(snapshot)
    
    def view_latest_actions(self, count=10):
        """View the latest action snapshots"""
        action_log_file = self.snapshots_dir / "action_log.jsonl"
        
        if not action_log_file.exists():
            print("No action log found yet.")
            return
        
        with open(action_log_file, 'r') as f:
            lines = f.readlines()
        
        # Get last N lines
        recent_lines = lines[-count:] if len(lines) > count else lines
        
        print(f"\n{'='*80}")
        print(f"LATEST {len(recent_lines)} ACTIONS")
        print(f"{'='*80}\n")
        
        for line in reversed(recent_lines):
            try:
                action = json.loads(line)
                self._display_action_summary(action)
            except json.JSONDecodeError:
                pass
    
    def view_all_snapshots(self):
        """View all available snapshots"""
        snapshot_files = sorted(
            self.snapshots_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        print(f"\n{'='*80}")
        print(f"ALL SNAPSHOTS ({len(snapshot_files)} total)")
        print(f"{'='*80}\n")
        
        for snapshot_file in snapshot_files:
            if snapshot_file.name == "latest_periodic.json":
                continue
            
            print(f"📄 {snapshot_file.name}")
            print(f"   Modified: {datetime.fromtimestamp(snapshot_file.stat().st_mtime)}")
            print(f"   Size: {snapshot_file.stat().st_size} bytes")
            print()
    
    def view_snapshot_by_id(self, snapshot_id):
        """View a specific snapshot by ID"""
        snapshot_file = self.snapshots_dir / f"{snapshot_id}.json"
        
        if not snapshot_file.exists():
            print(f"Snapshot not found: {snapshot_id}")
            return
        
        with open(snapshot_file, 'r') as f:
            snapshot = json.load(f)
        
        self._display_snapshot(snapshot)
    
    def _display_snapshot(self, snapshot):
        """Display a snapshot in a readable format"""
        print(f"\n{'='*80}")
        print(f"SNAPSHOT: {snapshot.get('snapshot_id', 'UNKNOWN')}")
        print(f"{'='*80}")
        print(f"Type: {snapshot.get('snapshot_type', 'UNKNOWN')}")
        print(f"Timestamp: {snapshot.get('timestamp', 'UNKNOWN')}")
        print()
        
        if snapshot.get('snapshot_type') == 'action':
            action = snapshot.get('action', {})
            print(f"ACTION DETAILS:")
            print(f"  Type: {action.get('type', 'UNKNOWN')}")
            print(f"  Status: {action.get('status', 'UNKNOWN')}")
            print(f"  Started: {action.get('started_at', 'UNKNOWN')}")
            print(f"  Details:")
            for key, value in action.get('details', {}).items():
                print(f"    {key}: {value}")
        
        elif snapshot.get('snapshot_type') == 'periodic':
            print(f"SYSTEM STATE:")
            system_state = snapshot.get('system_state', {})
            for key, value in system_state.items():
                print(f"  {key}: {value}")
            
            print(f"\nBUILD STATE:")
            build_state = snapshot.get('build_state', {})
            for key, value in build_state.items():
                if isinstance(value, list):
                    print(f"  {key}: {', '.join(value)}")
                else:
                    print(f"  {key}: {value}")
            
            print(f"\nRAIL STATUS:")
            rail_status = snapshot.get('rail_status', {})
            for key, value in rail_status.items():
                print(f"  {key}: {value}")
            
            print(f"\nCOGNITIVE STATE:")
            cognitive_state = snapshot.get('cognitive_state', {})
            for key, value in cognitive_state.items():
                if isinstance(value, list):
                    print(f"  {key}: {', '.join(value)}")
                else:
                    print(f"  {key}: {value}")
            
            print(f"\nTASK PROGRESS:")
            task_progress = snapshot.get('task_progress', {})
            if 'recent_activities' in task_progress:
                print(f"  Recent activities ({len(task_progress['recent_activities'])}):")
                for activity in task_progress['recent_activities'][:5]:
                    print(f"    - {activity}")
        
        print(f"\n{'='*80}\n")
    
    def _display_action_summary(self, action):
        """Display a brief summary of an action"""
        action_data = action.get('action', {})
        timestamp = action.get('timestamp', 'UNKNOWN')
        
        status_icon = {
            'executing': '⏳',
            'completed': '✅',
            'failed': '❌'
        }.get(action_data.get('status', 'unknown'), '❓')
        
        print(f"{status_icon} {timestamp}")
        print(f"   Type: {action_data.get('type', 'UNKNOWN')}")
        print(f"   Status: {action_data.get('status', 'UNKNOWN')}")
        
        details = action_data.get('details', {})
        if details:
            key_details = list(details.items())[:2]  # Show first 2 details
            for key, value in key_details:
                print(f"   {key}: {value}")
        print()
    
    def generate_dashboard_html(self, output_file="snapshot_dashboard.html"):
        """Generate an HTML dashboard for viewing snapshots"""
        latest_periodic = self.snapshots_dir / "latest_periodic.json"
        
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Barrot Snapshot Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        h2 {
            color: #764ba2;
            margin-top: 30px;
        }
        .snapshot-card {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }
        .status-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 0.9em;
            font-weight: bold;
        }
        .status-active {
            background: #28a745;
            color: white;
        }
        .status-stable {
            background: #17a2b8;
            color: white;
        }
        .timestamp {
            color: #6c757d;
            font-size: 0.9em;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric {
            background: #e9ecef;
            padding: 20px;
            border-radius: 5px;
            text-align: center;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .metric-label {
            color: #6c757d;
            margin-top: 5px;
        }
        pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        .refresh-info {
            text-align: right;
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Barrot Agent Snapshot Dashboard</h1>
        <div class="refresh-info">Last Updated: <span id="lastUpdate"></span></div>
"""
        
        if latest_periodic.exists():
            with open(latest_periodic, 'r') as f:
                snapshot = json.load(f)
            
            html_content += f"""
        <h2>Latest Periodic Snapshot</h2>
        <div class="snapshot-card">
            <div class="timestamp">📅 {snapshot.get('timestamp', 'UNKNOWN')}</div>
            <p><strong>Snapshot ID:</strong> {snapshot.get('snapshot_id', 'UNKNOWN')}</p>
        </div>
        
        <h2>System Overview</h2>
        <div class="grid">
"""
            
            # Add metrics
            build_state = snapshot.get('build_state', {})
            rail_status = snapshot.get('rail_status', {})
            
            html_content += f"""
            <div class="metric">
                <div class="metric-value">✅</div>
                <div class="metric-label">System Health</div>
            </div>
            <div class="metric">
                <div class="metric-value">{build_state.get('build_signature', 'N/A')}</div>
                <div class="metric-label">Build Signature</div>
            </div>
            <div class="metric">
                <div class="metric-value">{len(build_state.get('modules', []))}</div>
                <div class="metric-label">Active Modules</div>
            </div>
"""
            
            html_content += """
        </div>
        
        <h2>Rail Status</h2>
"""
            
            for rail, status in rail_status.items():
                # Escape HTML to prevent XSS
                rail_escaped = html.escape(str(rail))
                status_escaped = html.escape(str(status))
                status_lower = status_escaped.lower()
                
                html_content += f"""
        <div class="snapshot-card">
            <strong>{rail_escaped}:</strong> <span class="status-badge status-{status_lower}">{status_escaped}</span>
        </div>
"""
            
            # Add build state
            html_content += """
        <h2>Build State</h2>
        <pre>"""
            html_content += json.dumps(build_state, indent=2)
            html_content += """</pre>
        
        <h2>Cognitive State</h2>
        <pre>"""
            html_content += json.dumps(snapshot.get('cognitive_state', {}), indent=2)
            html_content += """</pre>
"""
        
        else:
            html_content += """
        <div class="snapshot-card">
            <p>⚠️ No periodic snapshot available yet. Snapshots are generated every 30 minutes.</p>
        </div>
"""
        
        html_content += """
        <script>
            document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
        </script>
    </div>
</body>
</html>
"""
        
        output_path = self.base_dir / output_file
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        print(f"Dashboard generated: {output_path}")
        return output_path


def main():
    """Main entry point for CLI usage"""
    viewer = SnapshotViewer()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python snapshot_viewer.py latest       - View latest periodic snapshot")
        print("  python snapshot_viewer.py actions [N]  - View latest N actions (default 10)")
        print("  python snapshot_viewer.py all          - List all snapshots")
        print("  python snapshot_viewer.py view <id>    - View specific snapshot")
        print("  python snapshot_viewer.py dashboard    - Generate HTML dashboard")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "latest":
        viewer.view_latest_periodic()
    elif command == "actions":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        viewer.view_latest_actions(count)
    elif command == "all":
        viewer.view_all_snapshots()
    elif command == "view":
        if len(sys.argv) < 3:
            print("Error: view command requires snapshot ID")
            sys.exit(1)
        viewer.view_snapshot_by_id(sys.argv[2])
    elif command == "dashboard":
        viewer.generate_dashboard_html()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
