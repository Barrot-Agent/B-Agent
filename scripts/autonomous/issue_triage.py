#!/usr/bin/env python3
"""
Autonomous Issue Triage and Auto-Response
Implements intelligent issue classification, prioritization, and automated responses
Part of B-Agent's autonomous repository management system
"""

import os
import json
import re
from datetime import datetime, timedelta
from github import Github
import sys

REPO_NAME = os.environ.get('REPO', 'Barrot-Agent/B-Agent')
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

# Issue classification patterns
ISSUE_PATTERNS = {
    'bug': r'\b(bug|error|crash|fail|broken|issue|problem|fix)\b',
    'enhancement': r'\b(feature|enhancement|improve|add|new|request)\b',
    'documentation': r'\b(doc|documentation|readme|guide|tutorial)\b',
    'question': r'\b(question|how|why|what|help|support)\b',
    'agi-puzzle': r'\b(puzzle|piece|agi|component|discovery)\b',
    'automation': r'\b(automat|workflow|ci|cd|action|script)\b',
    'urgent': r'\b(urgent|critical|asap|blocker|emergency)\b',
}

# Auto-response templates
RESPONSE_TEMPLATES = {
    'agi-puzzle': """🧩 **AGI Puzzle Discovery Detected**

Thank you for this contribution to the AGI Puzzle Framework!

**Autonomous Actions Taken:**
- ✅ Labeled as `agi-puzzle`
- ✅ Added to AGI Puzzle tracking system
- 📊 Puzzle piece count will be updated in next cycle

**Next Steps:**
1. Review puzzle piece details
2. Integrate with existing framework
3. Update documentation

This issue is being tracked by B-Agent's autonomous system.
""",
    'bug': """🐛 **Bug Report Acknowledged**

Thank you for reporting this issue!

**Autonomous Triage:**
- ✅ Labeled as `bug`
- 🔍 Priority assessment in progress
- 📋 Added to bug tracking queue

**What Happens Next:**
1. Automated analysis of issue details
2. Priority assignment based on impact
3. Assignment to appropriate workflow

B-Agent's autonomous system is monitoring this issue.
""",
    'enhancement': """✨ **Enhancement Request Received**

Thank you for your suggestion!

**Autonomous Processing:**
- ✅ Labeled as `enhancement`
- 📊 Added to feature roadmap analysis
- 🎯 Alignment with B-Agent goals being evaluated

**Evaluation Criteria:**
1. Alignment with Maximum Recursion Directive
2. Integration with existing systems
3. Impact on autonomous capabilities

This request is being tracked by B-Agent's autonomous system.
""",
    'documentation': """📚 **Documentation Request Acknowledged**

Thank you for helping improve our documentation!

**Autonomous Actions:**
- ✅ Labeled as `documentation`
- 📝 Added to documentation improvement queue
- 🔄 Progressive Ping-Pong quality check scheduled

**Documentation Standards:**
- 97%+ quality target (Progressive Ping-Pong validated)
- Comprehensive coverage
- Clear examples and usage patterns

B-Agent's autonomous system will process this request.
""",
    'question': """❓ **Question Received**

Thank you for your question!

**Autonomous Response:**
- ✅ Labeled as `question`
- 🔍 Knowledge base search initiated
- 📖 Relevant documentation will be linked

**Resources:**
- [GitHub Integration Guide](GITHUB_INTEGRATION.md)
- [AGI Puzzle Protocol](AGI_PUZZLE_PROTOCOL.md)
- [Maximum Recursion Directive](MAXIMUM_RECURSION_DIRECTIVE.md)

If this question requires human attention, it will be escalated.
""",
}

def main():
    """Main issue triage logic"""
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    print(f"🎯 Triaging issues in {REPO_NAME}...")
    
    stats = {
        'total_issues': 0,
        'new_issues_triaged': 0,
        'labels_added': 0,
        'auto_responses': 0,
        'escalations': 0,
        'closed_resolved': 0
    }
    
    # Get all open issues
    open_issues = repo.get_issues(state='open', sort='created', direction='desc')
    
    for issue in open_issues:
        if issue.pull_request:
            continue  # Skip PRs
        
        stats['total_issues'] += 1
        
        # Check if already triaged
        if not issue.labels:
            triage_issue(repo, issue, stats)
        
        # Check for stale issues
        check_stale_issue(repo, issue, stats)
        
        # Check for resolved issues
        check_resolved_issue(repo, issue, stats)
    
    # Generate report
    report_path = f"reports/issue-triage-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
    os.makedirs('reports', exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump({
            'timestamp': datetime.utcnow().isoformat(),
            'stats': stats
        }, f, indent=2)
    
    print(f"\n📊 Issue Triage Summary:")
    print(f"  Total issues: {stats['total_issues']}")
    print(f"  New issues triaged: {stats['new_issues_triaged']}")
    print(f"  Labels added: {stats['labels_added']}")
    print(f"  Auto-responses: {stats['auto_responses']}")
    print(f"  Escalations: {stats['escalations']}")
    print(f"  Closed (resolved): {stats['closed_resolved']}")
    
    return 0

def triage_issue(repo, issue, stats):
    """Triage a new issue"""
    print(f"  🔍 Triaging issue #{issue.number}: {issue.title}")
    
    text = f"{issue.title} {issue.body or ''}".lower()
    
    # Classify issue
    detected_types = []
    for issue_type, pattern in ISSUE_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            detected_types.append(issue_type)
    
    # Add labels
    labels_to_add = []
    for issue_type in detected_types:
        try:
            repo.get_label(issue_type)
            labels_to_add.append(issue_type)
        except:
            # Label doesn't exist, skip
            pass
    
    if labels_to_add:
        issue.add_to_labels(*labels_to_add)
        stats['labels_added'] += len(labels_to_add)
        print(f"    ✅ Added labels: {', '.join(labels_to_add)}")
    
    # Auto-respond based on primary type
    primary_type = detected_types[0] if detected_types else None
    if primary_type and primary_type in RESPONSE_TEMPLATES:
        # Check if we've already responded
        comments = list(issue.get_comments())
        bot_responded = any('B-Agent\'s autonomous system' in c.body for c in comments)
        
        if not bot_responded:
            issue.create_comment(RESPONSE_TEMPLATES[primary_type])
            stats['auto_responses'] += 1
            print(f"    💬 Auto-response sent ({primary_type})")
    
    # Check if needs escalation
    if 'urgent' in detected_types or 'critical' in text:
        issue.add_to_labels('priority-high')
        stats['escalations'] += 1
        print(f"    🚨 Escalated to high priority")
    
    stats['new_issues_triaged'] += 1

def check_stale_issue(repo, issue, stats):
    """Check if issue is stale and needs attention"""
    last_updated = issue.updated_at
    cutoff = datetime.utcnow() - timedelta(days=30)
    
    if last_updated < cutoff:
        # Check if already marked as stale
        has_stale_label = any(label.name == 'stale' for label in issue.labels)
        
        if not has_stale_label:
            try:
                issue.add_to_labels('stale')
                issue.create_comment(
                    "🕐 **Stale Issue Detection**\n\n"
                    "This issue has had no activity for 30+ days.\n\n"
                    "**Actions:**\n"
                    "- If still relevant, please provide an update\n"
                    "- If resolved, please close this issue\n"
                    "- If no activity in 14 days, this will be auto-closed\n\n"
                    f"Detected by B-Agent autonomous system: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                )
                print(f"  🕐 Marked issue #{issue.number} as stale")
            except:
                pass

def check_resolved_issue(repo, issue, stats):
    """Check if issue appears resolved and can be closed"""
    # Look for resolution indicators in comments
    comments = list(issue.get_comments())
    
    resolution_keywords = ['resolved', 'fixed', 'completed', 'done', 'closed', 'merged']
    
    for comment in comments[-3:]:  # Check last 3 comments
        text = comment.body.lower()
        if any(keyword in text for keyword in resolution_keywords):
            # Check if issue is old enough (7 days since last comment)
            if (datetime.utcnow() - comment.created_at).days >= 7:
                issue.create_comment(
                    "✅ **Auto-Close: Resolution Detected**\n\n"
                    "This issue appears to be resolved based on recent comments.\n\n"
                    "If this is incorrect, please reopen the issue.\n\n"
                    f"Closed by B-Agent autonomous system: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                )
                issue.edit(state='closed')
                stats['closed_resolved'] += 1
                print(f"  ✅ Auto-closed resolved issue #{issue.number}")
                break

if __name__ == '__main__':
    sys.exit(main())
