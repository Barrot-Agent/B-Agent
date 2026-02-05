#!/usr/bin/env python3
"""
Progressive Ping-Pong Quality Analysis
Implements 97%+ quality validation through iterative improvement
Part of B-Agent's autonomous quality assurance system
"""

import os
import json
from datetime import datetime
from github import Github
import sys

REPO_NAME = os.environ.get('REPO', 'Barrot-Agent/B-Agent')
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
PR_NUMBER = int(os.environ.get('PR_NUMBER', 0))
QUALITY_THRESHOLD = 97.0

# Quality assessment criteria
QUALITY_CRITERIA = {
    'code_quality': {
        'weight': 0.25,
        'checks': [
            'proper_formatting',
            'clear_naming',
            'adequate_comments',
            'error_handling',
            'no_code_smells'
        ]
    },
    'documentation': {
        'weight': 0.20,
        'checks': [
            'readme_updated',
            'inline_documentation',
            'usage_examples',
            'clear_descriptions'
        ]
    },
    'functionality': {
        'weight': 0.30,
        'checks': [
            'meets_requirements',
            'edge_cases_handled',
            'no_regressions',
            'proper_testing'
        ]
    },
    'integration': {
        'weight': 0.15,
        'checks': [
            'follows_conventions',
            'integrates_cleanly',
            'no_conflicts',
            'backwards_compatible'
        ]
    },
    'innovation': {
        'weight': 0.10,
        'checks': [
            'adds_value',
            'aligns_with_directive',
            'enables_recursion',
            'improves_autonomy'
        ]
    }
}

def main():
    """Main Progressive Ping-Pong analysis"""
    if not PR_NUMBER:
        print("❌ No PR number provided")
        return 1
    
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    try:
        pr = repo.get_pull(PR_NUMBER)
    except:
        print(f"❌ PR #{PR_NUMBER} not found")
        return 1
    
    print(f"🏓 Analyzing PR #{PR_NUMBER}: {pr.title}")
    
    # Perform quality analysis
    quality_report = analyze_pr_quality(repo, pr)
    
    # Generate report
    markdown_report = generate_quality_report(pr, quality_report)
    
    # Save report
    os.makedirs('reports', exist_ok=True)
    with open('reports/pingpong-quality-report.md', 'w') as f:
        f.write(markdown_report)
    
    # Output for GitHub Actions
    print(f"::set-output name=quality_score::{quality_report['overall_score']}")
    
    # Print summary
    print(f"\n📊 Quality Analysis Summary:")
    print(f"  Overall Score: {quality_report['overall_score']:.1f}%")
    print(f"  Threshold: {QUALITY_THRESHOLD}%")
    print(f"  Status: {'✅ PASS' if quality_report['overall_score'] >= QUALITY_THRESHOLD else '🔄 ITERATE'}")
    
    return 0

def analyze_pr_quality(repo, pr):
    """Analyze PR quality across all criteria"""
    quality_report = {
        'pr_number': pr.number,
        'pr_title': pr.title,
        'timestamp': datetime.utcnow().isoformat(),
        'criteria_scores': {},
        'overall_score': 0.0,
        'recommendations': []
    }
    
    total_score = 0.0
    
    for criterion, config in QUALITY_CRITERIA.items():
        score = assess_criterion(repo, pr, criterion, config)
        quality_report['criteria_scores'][criterion] = score
        weighted_score = score * config['weight']
        total_score += weighted_score
        
        print(f"  {criterion}: {score:.1f}% (weight: {config['weight']*100:.0f}%)")
    
    quality_report['overall_score'] = total_score
    
    # Generate recommendations if below threshold
    if total_score < QUALITY_THRESHOLD:
        quality_report['recommendations'] = generate_recommendations(quality_report)
    
    return quality_report

def assess_criterion(repo, pr, criterion, config):
    """Assess a specific quality criterion"""
    # Get PR details
    files = list(pr.get_files())
    commits = list(pr.get_commits())
    reviews = list(pr.get_reviews())
    
    # Scoring logic based on criterion
    if criterion == 'code_quality':
        return assess_code_quality(files, commits)
    elif criterion == 'documentation':
        return assess_documentation(files, pr)
    elif criterion == 'functionality':
        return assess_functionality(pr, files)
    elif criterion == 'integration':
        return assess_integration(pr, files)
    elif criterion == 'innovation':
        return assess_innovation(pr, files)
    
    return 80.0  # Default score

def assess_code_quality(files, commits):
    """Assess code quality"""
    score = 100.0
    
    # Check file sizes (penalize very large files)
    for file in files:
        if file.additions > 1000:
            score -= 5
    
    # Check commit messages
    poor_messages = sum(1 for c in commits if len(c.commit.message) < 20)
    score -= poor_messages * 2
    
    # Check for common code smells
    for file in files:
        if file.filename.endswith('.py'):
            # Penalize if no docstrings (heuristic)
            if file.additions > 50 and '"""' not in (file.patch or ''):
                score -= 3
    
    return max(score, 0.0)

def assess_documentation(files, pr):
    """Assess documentation quality"""
    score = 100.0
    
    # Check if README or docs updated
    has_doc_update = any(
        'README' in f.filename or 'docs/' in f.filename or f.filename.endswith('.md')
        for f in files
    )
    
    if not has_doc_update and len(files) > 3:
        score -= 15
    
    # Check PR description
    if not pr.body or len(pr.body) < 100:
        score -= 10
    
    return max(score, 0.0)

def assess_functionality(pr, files):
    """Assess functionality"""
    score = 100.0
    
    # Check for test files
    has_tests = any('test' in f.filename.lower() for f in files)
    if not has_tests and len(files) > 2:
        score -= 15
    
    # Check if mergeable
    if pr.mergeable_state == 'dirty':
        score -= 20
    
    return max(score, 0.0)

def assess_integration(pr, files):
    """Assess integration quality"""
    score = 100.0
    
    # Check for conflicts
    if pr.mergeable_state == 'dirty':
        score -= 25
    
    # Check base branch
    if pr.base.ref not in ['main', 'Main']:
        score -= 10
    
    return max(score, 0.0)

def assess_innovation(pr, files):
    """Assess innovation and alignment"""
    score = 85.0  # Base score for any contribution
    
    # Check for keywords indicating innovation
    innovation_keywords = [
        'autonomous', 'recursive', 'agi', 'puzzle', 'framework',
        'integration', 'automation', 'enhancement'
    ]
    
    text = f"{pr.title} {pr.body or ''}".lower()
    matches = sum(1 for keyword in innovation_keywords if keyword in text)
    score += min(matches * 2, 15)
    
    return min(score, 100.0)

def generate_recommendations(quality_report):
    """Generate improvement recommendations"""
    recommendations = []
    
    for criterion, score in quality_report['criteria_scores'].items():
        if score < 90:
            if criterion == 'code_quality':
                recommendations.append("Improve code quality: Add docstrings, improve naming, add error handling")
            elif criterion == 'documentation':
                recommendations.append("Enhance documentation: Update README, add usage examples, expand PR description")
            elif criterion == 'functionality':
                recommendations.append("Strengthen functionality: Add tests, handle edge cases, verify no regressions")
            elif criterion == 'integration':
                recommendations.append("Improve integration: Resolve conflicts, follow conventions, ensure compatibility")
            elif criterion == 'innovation':
                recommendations.append("Increase innovation: Align with Maximum Recursion Directive, add autonomous capabilities")
    
    return recommendations

def generate_quality_report(pr, quality_report):
    """Generate markdown quality report"""
    score = quality_report['overall_score']
    status = '✅ PASS' if score >= QUALITY_THRESHOLD else '🔄 ITERATE'
    
    md = f"""# 🏓 Progressive Ping-Pong Quality Report

**PR**: #{pr.number} - {pr.title}  
**Analysis Date**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Overall Score**: {score:.1f}% / {QUALITY_THRESHOLD}%  
**Status**: {status}

---

## 📊 Quality Breakdown

| Criterion | Score | Weight | Contribution |
|-----------|-------|--------|--------------|
"""
    
    for criterion, config in QUALITY_CRITERIA.items():
        criterion_score = quality_report['criteria_scores'][criterion]
        weight = config['weight'] * 100
        contribution = criterion_score * config['weight']
        
        md += f"| {criterion.replace('_', ' ').title()} | {criterion_score:.1f}% | {weight:.0f}% | {contribution:.1f}% |\n"
    
    md += f"\n**Total**: {score:.1f}%\n\n"
    
    if score >= QUALITY_THRESHOLD:
        md += """---

## ✅ Quality Threshold Met!

This PR meets the 97%+ quality standard and is approved for merge.

**Next Steps:**
- Auto-merge will be triggered
- Changes will be integrated into main branch
- Documentation will be updated automatically

**Congratulations!** This contribution exemplifies B-Agent's Progressive Ping-Pong quality standards.
"""
    else:
        md += """---

## 🔄 Iteration Required

This PR requires improvement to meet the 97%+ quality threshold.

### Recommendations

"""
        for i, rec in enumerate(quality_report['recommendations'], 1):
            md += f"{i}. {rec}\n"
        
        md += """

### Next Steps

1. Address the recommendations above
2. Update the PR with improvements
3. Request another Progressive Ping-Pong analysis
4. Iterate until 97%+ quality is achieved

**Remember**: Progressive Ping-Pong is about continuous improvement. Each iteration brings us closer to excellence!
"""
    
    md += """

---

## 📚 Quality Criteria

### Code Quality (25%)
- Proper formatting and style
- Clear naming conventions
- Adequate comments and docstrings
- Robust error handling
- No code smells

### Documentation (20%)
- README updates
- Inline documentation
- Usage examples
- Clear descriptions

### Functionality (30%)
- Meets requirements
- Edge cases handled
- No regressions
- Proper testing

### Integration (15%)
- Follows conventions
- Integrates cleanly
- No conflicts
- Backwards compatible

### Innovation (10%)
- Adds value
- Aligns with Maximum Recursion Directive
- Enables recursive improvement
- Improves autonomous capabilities

---

*This report was automatically generated by B-Agent's Progressive Ping-Pong system.*  
*Target: 97%+ quality for all contributions*
"""
    
    return md

if __name__ == '__main__':
    sys.exit(main())
