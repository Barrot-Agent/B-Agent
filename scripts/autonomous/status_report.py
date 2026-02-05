#!/usr/bin/env python3
"""
Status Report Generator
Creates comprehensive status reports for autonomous operations
Part of B-Agent's autonomous system
"""

import os
import json
from datetime import datetime
from pathlib import Path
import sys

def main():
    """Generate comprehensive status report"""
    print("📊 Generating status report...")
    
    report = {
        'timestamp': datetime.utcnow().isoformat(),
        'sections': {}
    }
    
    # Collect data from all subsystems
    report['sections']['health_check'] = load_latest_report('health-check')
    report['sections']['pr_cleanup'] = load_latest_report('pr-cleanup')
    report['sections']['issue_triage'] = load_latest_report('issue-triage')
    report['sections']['agi_puzzle'] = load_latest_report('agi-puzzle')
    report['sections']['memory_sync'] = load_sync_log()
    
    # Generate markdown report
    markdown_report = generate_markdown_report(report)
    
    # Save reports
    timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    
    json_path = f"reports/status-{timestamp}.json"
    md_path = f"reports/status-{timestamp}.md"
    latest_path = "reports/status-latest.md"
    
    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    with open(md_path, 'w') as f:
        f.write(markdown_report)
    
    with open(latest_path, 'w') as f:
        f.write(markdown_report)
    
    print(f"  ✅ Reports saved:")
    print(f"     - {json_path}")
    print(f"     - {md_path}")
    print(f"     - {latest_path}")
    
    return 0

def load_latest_report(report_type):
    """Load the latest report of a given type"""
    reports_dir = Path('reports')
    if not reports_dir.exists():
        return None
    
    # Find latest report
    pattern = f"{report_type}-*.json"
    reports = sorted(reports_dir.glob(pattern), reverse=True)
    
    if not reports:
        return None
    
    try:
        with open(reports[0], 'r') as f:
            return json.load(f)
    except:
        return None

def load_sync_log():
    """Load memory bundle sync log"""
    sync_log_path = 'reports/memory-bundle-sync.json'
    if not os.path.exists(sync_log_path):
        return None
    
    try:
        with open(sync_log_path, 'r') as f:
            data = json.load(f)
            # Return only the latest sync
            if data.get('syncs'):
                return data['syncs'][-1]
    except:
        pass
    
    return None

def generate_markdown_report(report):
    """Generate markdown status report"""
    md = f"""# 🤖 B-Agent Autonomous System Status Report

**Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

---

## 🏥 Repository Health

"""
    
    # Health Check Section
    health = report['sections'].get('health_check')
    if health:
        overall = health.get('overall_status', 'unknown').upper()
        status_emoji = '✅' if overall == 'HEALTHY' else '⚠️' if overall == 'DEGRADED' else '❌'
        
        md += f"**Overall Status**: {status_emoji} {overall}\n\n"
        md += "### Health Checks\n\n"
        md += "| Check | Status | Details |\n"
        md += "|-------|--------|----------|\n"
        
        for check_name, check_data in health.get('checks', {}).items():
            status = check_data.get('status', 'unknown')
            status_emoji = '✅' if status == 'pass' else '⚠️' if status == 'warning' else '❌'
            message = check_data.get('message', 'No details')
            md += f"| {check_name.replace('_', ' ').title()} | {status_emoji} {status} | {message} |\n"
    else:
        md += "⚠️ No health check data available\n"
    
    md += "\n---\n\n## 🧹 PR Cleanup\n\n"
    
    # PR Cleanup Section
    pr_cleanup = report['sections'].get('pr_cleanup')
    if pr_cleanup:
        stats = pr_cleanup.get('stats', {})
        md += f"- **Total PRs**: {stats.get('total_prs', 0)}\n"
        md += f"- **Conflicting**: {stats.get('conflicting_prs', 0)}\n"
        md += f"- **Stale PRs Closed**: {stats.get('stale_prs_closed', 0)}\n"
        md += f"- **Branch Mismatches Closed**: {stats.get('branch_mismatches_closed', 0)}\n"
        md += f"- **Auto-Resolved**: {stats.get('auto_resolved', 0)}\n"
        md += f"- **Needs Attention**: {len(stats.get('needs_attention', []))}\n"
    else:
        md += "⚠️ No PR cleanup data available\n"
    
    md += "\n---\n\n## 🎯 Issue Triage\n\n"
    
    # Issue Triage Section
    issue_triage = report['sections'].get('issue_triage')
    if issue_triage:
        stats = issue_triage.get('stats', {})
        md += f"- **Total Issues**: {stats.get('total_issues', 0)}\n"
        md += f"- **New Issues Triaged**: {stats.get('new_issues_triaged', 0)}\n"
        md += f"- **Labels Added**: {stats.get('labels_added', 0)}\n"
        md += f"- **Auto-Responses**: {stats.get('auto_responses', 0)}\n"
        md += f"- **Escalations**: {stats.get('escalations', 0)}\n"
        md += f"- **Closed (Resolved)**: {stats.get('closed_resolved', 0)}\n"
    else:
        md += "⚠️ No issue triage data available\n"
    
    md += "\n---\n\n## 🧩 AGI Puzzle Framework\n\n"
    
    # AGI Puzzle Section
    agi_puzzle = report['sections'].get('agi_puzzle')
    if agi_puzzle:
        stats = agi_puzzle.get('stats', {})
        total = stats.get('total_pieces', 0)
        progress = (total / 56 * 100) if total > 0 else 0
        
        md += f"- **Total Pieces Discovered**: {total} / 56\n"
        md += f"- **Progress**: {progress:.1f}%\n"
        md += f"- **New Pieces This Cycle**: {stats.get('new_pieces', 0)}\n"
        md += f"- **Issues Created**: {stats.get('issues_created', 0)}\n"
        md += f"- **Documentation Updated**: {stats.get('documentation_updated', 0)}\n"
        
        # Progress bar
        filled = int(progress / 2)  # 50 chars max
        bar = '█' * filled + '░' * (50 - filled)
        md += f"\n**Progress Bar**: `{bar}` {progress:.1f}%\n"
    else:
        md += "⚠️ No AGI puzzle data available\n"
    
    md += "\n---\n\n## 📦 Memory Bundle Sync\n\n"
    
    # Memory Sync Section
    memory_sync = report['sections'].get('memory_sync')
    if memory_sync:
        stats = memory_sync.get('stats', {})
        md += f"- **Files Changed**: {stats.get('files_changed', 0)}\n"
        md += f"- **Added**: {stats.get('files_added', 0)}\n"
        md += f"- **Modified**: {stats.get('files_modified', 0)}\n"
        md += f"- **Deleted**: {stats.get('files_deleted', 0)}\n"
        md += f"- **Commit Created**: {'✅ Yes' if stats.get('commit_created') else '❌ No'}\n"
        md += f"- **Sync Successful**: {'✅ Yes' if stats.get('sync_successful') else '❌ No'}\n"
    else:
        md += "⚠️ No memory sync data available\n"
    
    md += "\n---\n\n## 🎯 System Overview\n\n"
    md += "### Autonomous Operations\n\n"
    md += "B-Agent's autonomous system runs every 30 minutes and performs:\n\n"
    md += "1. **Repository Health Check** - Monitors overall repository health\n"
    md += "2. **PR Cleanup & Conflict Resolution** - Manages pull requests automatically\n"
    md += "3. **Issue Triage & Auto-Response** - Classifies and responds to issues\n"
    md += "4. **AGI Puzzle Tracking** - Discovers and documents puzzle pieces\n"
    md += "5. **Memory Bundle Sync** - Synchronizes memory bundles to repository\n\n"
    
    md += "### Integration Points\n\n"
    md += "- **AGI Puzzle Framework** - 56-piece systematic AGI discovery\n"
    md += "- **Progressive Ping-Pong** - 97%+ quality validation\n"
    md += "- **22-Agent Council** - Distributed development coordination\n"
    md += "- **Maximum Recursion Directive** - Continuous self-improvement\n\n"
    
    md += "### Documentation\n\n"
    md += "- [GitHub Integration Guide](GITHUB_INTEGRATION.md)\n"
    md += "- [AGI Puzzle Progress](AGI_PUZZLE_PROGRESS.md)\n"
    md += "- [Autonomous System Documentation](AUTONOMOUS_SYSTEM.md)\n\n"
    
    md += "---\n\n"
    md += "*This report is automatically generated by B-Agent's autonomous system.*\n"
    md += f"*Next update: {(datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S UTC')} (every 30 minutes)*\n"
    
    return md

if __name__ == '__main__':
    sys.exit(main())
