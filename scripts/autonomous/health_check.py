#!/usr/bin/env python3
"""
Repository Health Check
Comprehensive health monitoring for B-Agent repository
Part of autonomous operations system
"""

import os
import json
from datetime import datetime, timedelta
from github import Github
import subprocess
import sys

REPO_NAME = os.environ.get('REPO', 'Barrot-Agent/B-Agent')
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

def main():
    """Main health check logic"""
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    print(f"🏥 Running health check for {REPO_NAME}...")
    
    health_report = {
        'timestamp': datetime.utcnow().isoformat(),
        'overall_status': 'healthy',
        'checks': {}
    }
    
    # Run all health checks
    checks = [
        ('repository_basics', check_repository_basics),
        ('branch_health', check_branch_health),
        ('pr_health', check_pr_health),
        ('issue_health', check_issue_health),
        ('workflow_health', check_workflow_health),
        ('documentation_health', check_documentation_health),
        ('file_system_health', check_file_system_health),
    ]
    
    for check_name, check_func in checks:
        try:
            result = check_func(repo)
            health_report['checks'][check_name] = result
            
            status_emoji = '✅' if result['status'] == 'pass' else '⚠️' if result['status'] == 'warning' else '❌'
            print(f"  {status_emoji} {check_name}: {result['status']}")
            
            if result['status'] == 'fail':
                health_report['overall_status'] = 'unhealthy'
            elif result['status'] == 'warning' and health_report['overall_status'] == 'healthy':
                health_report['overall_status'] = 'degraded'
                
        except Exception as e:
            print(f"  ❌ {check_name}: error - {e}")
            health_report['checks'][check_name] = {
                'status': 'error',
                'message': str(e)
            }
            health_report['overall_status'] = 'unhealthy'
    
    # Save report
    report_path = f"reports/health-check-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
    os.makedirs('reports', exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(health_report, f, indent=2)
    
    # Print summary
    print(f"\n🏥 Health Check Summary:")
    print(f"  Overall Status: {health_report['overall_status'].upper()}")
    print(f"  Report saved: {report_path}")
    
    return 0

def check_repository_basics(repo):
    """Check basic repository health"""
    issues = []
    
    # Check default branch
    if repo.default_branch != 'main':
        issues.append(f"Default branch is '{repo.default_branch}', expected 'main'")
    
    # Check if repo is archived
    if repo.archived:
        issues.append("Repository is archived")
    
    # Check if repo is private
    if repo.private:
        issues.append("Repository is private (may be intentional)")
    
    return {
        'status': 'pass' if not issues else 'warning',
        'message': '; '.join(issues) if issues else 'Repository basics healthy',
        'details': {
            'default_branch': repo.default_branch,
            'archived': repo.archived,
            'private': repo.private,
            'size': repo.size
        }
    }

def check_branch_health(repo):
    """Check branch health"""
    branches = list(repo.get_branches())
    issues = []
    
    # Check for old Main branch
    branch_names = [b.name for b in branches]
    if 'Main' in branch_names and 'main' in branch_names:
        issues.append("Both 'Main' and 'main' branches exist")
    
    # Check for too many branches
    if len(branches) > 100:
        issues.append(f"Too many branches: {len(branches)}")
    
    return {
        'status': 'warning' if issues else 'pass',
        'message': '; '.join(issues) if issues else 'Branches healthy',
        'details': {
            'total_branches': len(branches),
            'branch_names': branch_names[:10]  # First 10
        }
    }

def check_pr_health(repo):
    """Check pull request health"""
    open_prs = list(repo.get_pulls(state='open'))
    
    conflicting = sum(1 for pr in open_prs if pr.mergeable_state == 'dirty')
    stale = sum(1 for pr in open_prs if (datetime.utcnow() - pr.updated_at).days > 30)
    
    issues = []
    if conflicting > 10:
        issues.append(f"{conflicting} PRs with conflicts")
    if stale > 5:
        issues.append(f"{stale} stale PRs (30+ days)")
    if len(open_prs) > 50:
        issues.append(f"Too many open PRs: {len(open_prs)}")
    
    return {
        'status': 'warning' if issues else 'pass',
        'message': '; '.join(issues) if issues else 'PRs healthy',
        'details': {
            'total_open': len(open_prs),
            'conflicting': conflicting,
            'stale': stale
        }
    }

def check_issue_health(repo):
    """Check issue health"""
    open_issues = list(repo.get_issues(state='open'))
    # Filter out PRs
    open_issues = [i for i in open_issues if not i.pull_request]
    
    unlabeled = sum(1 for issue in open_issues if not issue.labels)
    stale = sum(1 for issue in open_issues if (datetime.utcnow() - issue.updated_at).days > 30)
    
    issues = []
    if unlabeled > 5:
        issues.append(f"{unlabeled} unlabeled issues")
    if stale > 10:
        issues.append(f"{stale} stale issues")
    
    return {
        'status': 'warning' if issues else 'pass',
        'message': '; '.join(issues) if issues else 'Issues healthy',
        'details': {
            'total_open': len(open_issues),
            'unlabeled': unlabeled,
            'stale': stale
        }
    }

def check_workflow_health(repo):
    """Check GitHub Actions workflow health"""
    workflows = list(repo.get_workflows())
    
    # Get recent workflow runs
    runs = list(repo.get_workflow_runs()[:20])
    failed_runs = [r for r in runs if r.conclusion == 'failure']
    
    issues = []
    if len(failed_runs) > 5:
        issues.append(f"{len(failed_runs)} failed workflow runs in last 20")
    
    return {
        'status': 'warning' if issues else 'pass',
        'message': '; '.join(issues) if issues else 'Workflows healthy',
        'details': {
            'total_workflows': len(workflows),
            'recent_runs': len(runs),
            'failed_runs': len(failed_runs)
        }
    }

def check_documentation_health(repo):
    """Check documentation health"""
    required_docs = [
        'README.md',
        'GITHUB_INTEGRATION.md',
        'AGI_PUZZLE_PROTOCOL.md',
        'MAXIMUM_RECURSION_DIRECTIVE.md'
    ]
    
    missing = []
    for doc in required_docs:
        try:
            repo.get_contents(doc)
        except:
            missing.append(doc)
    
    return {
        'status': 'warning' if missing else 'pass',
        'message': f"Missing: {', '.join(missing)}" if missing else 'Documentation complete',
        'details': {
            'required_docs': required_docs,
            'missing_docs': missing
        }
    }

def check_file_system_health(repo):
    """Check for file system issues"""
    issues = []
    
    # Check for files with problematic names
    try:
        contents = repo.get_contents("")
        for content in contents:
            if len(content.name) > 200:
                issues.append(f"File name too long: {content.name[:50]}...")
    except Exception as e:
        issues.append(f"Error checking files: {e}")
    
    return {
        'status': 'warning' if issues else 'pass',
        'message': '; '.join(issues) if issues else 'File system healthy',
        'details': {
            'issues_found': len(issues)
        }
    }

if __name__ == '__main__':
    sys.exit(main())
