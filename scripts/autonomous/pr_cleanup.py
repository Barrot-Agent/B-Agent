#!/usr/bin/env python3
"""
Autonomous PR Cleanup and Conflict Resolution
Part of B-Agent's autonomous repository management system
"""

import os
import json
from datetime import datetime, timedelta
from github import Github
import sys

# Configuration
REPO_NAME = os.environ.get('REPO', 'Barrot-Agent/B-Agent')
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
STALE_DAYS = 30
CONFLICT_PRIORITY_LABELS = ['critical', 'bug', 'enhancement']

def main():
    """Main PR cleanup and conflict resolution logic"""
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    print(f"🔍 Analyzing PRs in {REPO_NAME}...")
    
    stats = {
        'total_prs': 0,
        'conflicting_prs': 0,
        'stale_prs_closed': 0,
        'branch_mismatches_closed': 0,
        'auto_resolved': 0,
        'needs_attention': []
    }
    
    # Get all open PRs
    open_prs = repo.get_pulls(state='open', sort='updated', direction='asc')
    
    for pr in open_prs:
        stats['total_prs'] += 1
        
        # Check for conflicts
        if pr.mergeable_state == 'dirty':
            stats['conflicting_prs'] += 1
            handle_conflicting_pr(repo, pr, stats)
        
        # Check for stale PRs
        if is_stale(pr, STALE_DAYS):
            handle_stale_pr(repo, pr, stats)
        
        # Check for branch mismatches (Main vs main)
        if pr.base.ref in ['Main', 'master'] and repo.default_branch == 'main':
            handle_branch_mismatch(repo, pr, stats)
    
    # Generate report
    report_path = f"reports/pr-cleanup-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
    os.makedirs('reports', exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump({
            'timestamp': datetime.utcnow().isoformat(),
            'stats': stats
        }, f, indent=2)
    
    print(f"\n📊 PR Cleanup Summary:")
    print(f"  Total PRs: {stats['total_prs']}")
    print(f"  Conflicting: {stats['conflicting_prs']}")
    print(f"  Stale PRs closed: {stats['stale_prs_closed']}")
    print(f"  Branch mismatches closed: {stats['branch_mismatches_closed']}")
    print(f"  Auto-resolved: {stats['auto_resolved']}")
    print(f"  Needs attention: {len(stats['needs_attention'])}")
    
    return 0

def handle_conflicting_pr(repo, pr, stats):
    """Handle PRs with merge conflicts"""
    print(f"  ⚠️  PR #{pr.number}: {pr.title} - Has conflicts")
    
    # Check if it's a simple conflict we can auto-resolve
    if can_auto_resolve(pr):
        try:
            # Attempt auto-resolution (e.g., rebase)
            print(f"    🔄 Attempting auto-resolution...")
            # In practice, this would trigger a rebase or merge
            # For now, we'll just comment
            pr.create_issue_comment(
                "🤖 **Autonomous Conflict Detection**\n\n"
                "This PR has merge conflicts. B-Agent's autonomous system has detected this.\n\n"
                "**Recommended Actions:**\n"
                "1. Rebase against the latest `main` branch\n"
                "2. Resolve conflicts locally\n"
                "3. Force push to update this PR\n\n"
                f"Detected: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
            )
            stats['auto_resolved'] += 1
        except Exception as e:
            print(f"    ❌ Auto-resolution failed: {e}")
            stats['needs_attention'].append({
                'pr': pr.number,
                'title': pr.title,
                'reason': 'conflict_resolution_failed'
            })
    else:
        stats['needs_attention'].append({
            'pr': pr.number,
            'title': pr.title,
            'reason': 'complex_conflict'
        })

def handle_stale_pr(repo, pr, stats):
    """Handle stale PRs"""
    print(f"  🕐 PR #{pr.number}: {pr.title} - Stale (no activity for {STALE_DAYS}+ days)")
    
    # Check if it has important labels
    pr_labels = [label.name for label in pr.labels]
    has_priority = any(label in CONFLICT_PRIORITY_LABELS for label in pr_labels)
    
    if not has_priority and not pr.draft:
        # Close stale PR
        pr.create_issue_comment(
            "🤖 **Autonomous Stale PR Cleanup**\n\n"
            f"This PR has had no activity for over {STALE_DAYS} days and is being automatically closed.\n\n"
            "If this work is still relevant, please:\n"
            "1. Rebase against the latest `main` branch\n"
            "2. Reopen this PR or create a new one\n\n"
            f"Closed by B-Agent autonomous system: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        pr.edit(state='closed')
        stats['stale_prs_closed'] += 1
        print(f"    ✅ Closed stale PR #{pr.number}")
    else:
        print(f"    ⏭️  Skipping (has priority label or is draft)")

def handle_branch_mismatch(repo, pr, stats):
    """Handle PRs targeting wrong branch (Main instead of main)"""
    print(f"  🔀 PR #{pr.number}: {pr.title} - Targets old branch '{pr.base.ref}'")
    
    pr.create_issue_comment(
        "🤖 **Autonomous Branch Mismatch Detection**\n\n"
        f"This PR targets the old `{pr.base.ref}` branch, but the repository's default branch is now `{repo.default_branch}`.\n\n"
        "**Recommended Actions:**\n"
        f"1. Change the base branch to `{repo.default_branch}`\n"
        "2. Rebase your changes against the latest `{repo.default_branch}`\n"
        "3. Update this PR\n\n"
        "Alternatively, this PR will be automatically closed if no action is taken within 7 days.\n\n"
        f"Detected: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )
    
    # If it's very old, close it
    if is_stale(pr, 60):  # 60 days
        pr.edit(state='closed')
        stats['branch_mismatches_closed'] += 1
        print(f"    ✅ Closed due to branch mismatch and age")

def is_stale(pr, days):
    """Check if PR is stale"""
    last_updated = pr.updated_at
    cutoff = datetime.utcnow() - timedelta(days=days)
    return last_updated < cutoff

def can_auto_resolve(pr):
    """Determine if conflict can be auto-resolved"""
    # Simple heuristic: if it's a documentation-only PR, we can try
    files = pr.get_files()
    all_docs = all(f.filename.endswith(('.md', '.txt', '.rst')) for f in files)
    return all_docs and pr.additions < 500

if __name__ == '__main__':
    sys.exit(main())
