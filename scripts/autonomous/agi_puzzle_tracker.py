#!/usr/bin/env python3
"""
AGI Puzzle Tracker - Autonomous Discovery and Documentation
Monitors memory bundles for new puzzle piece discoveries and creates GitHub issues
Part of B-Agent's AGI Puzzle Framework integration
"""

import os
import json
import re
from datetime import datetime
from github import Github
from pathlib import Path
import sys

REPO_NAME = os.environ.get('REPO', 'Barrot-Agent/B-Agent')
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
MEMORY_BUNDLES_DIR = 'memory-bundles'
PUZZLE_TRACKING_FILE = 'reports/agi-puzzle-tracking.json'

def main():
    """Main AGI puzzle tracking logic"""
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    print(f"🧩 Tracking AGI puzzle pieces in {REPO_NAME}...")
    
    # Load existing tracking data
    tracking_data = load_tracking_data()
    
    stats = {
        'total_pieces': 0,
        'new_pieces': 0,
        'issues_created': 0,
        'documentation_updated': 0
    }
    
    # Scan memory bundles for puzzle pieces
    puzzle_pieces = scan_memory_bundles()
    stats['total_pieces'] = len(puzzle_pieces)
    
    # Process each puzzle piece
    for piece in puzzle_pieces:
        if not is_tracked(piece, tracking_data):
            # New puzzle piece discovered!
            print(f"  ✨ New puzzle piece discovered: {piece['name']}")
            
            # Create GitHub issue
            issue = create_puzzle_issue(repo, piece)
            
            # Update tracking
            tracking_data['pieces'].append({
                'number': piece['number'],
                'name': piece['name'],
                'issue_number': issue.number,
                'discovered_at': datetime.utcnow().isoformat(),
                'status': 'discovered'
            })
            
            stats['new_pieces'] += 1
            stats['issues_created'] += 1
    
    # Update puzzle progress documentation
    update_puzzle_progress(puzzle_pieces, stats)
    stats['documentation_updated'] += 1
    
    # Save tracking data
    save_tracking_data(tracking_data)
    
    # Generate report
    report_path = f"reports/agi-puzzle-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
    os.makedirs('reports', exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump({
            'timestamp': datetime.utcnow().isoformat(),
            'stats': stats,
            'puzzle_pieces': puzzle_pieces
        }, f, indent=2)
    
    print(f"\n📊 AGI Puzzle Tracking Summary:")
    print(f"  Total pieces: {stats['total_pieces']}")
    print(f"  New pieces: {stats['new_pieces']}")
    print(f"  Issues created: {stats['issues_created']}")
    print(f"  Documentation updated: {stats['documentation_updated']}")
    
    return 0

def scan_memory_bundles():
    """Scan memory bundles directory for puzzle pieces"""
    puzzle_pieces = []
    
    if not os.path.exists(MEMORY_BUNDLES_DIR):
        print(f"  ⚠️  Memory bundles directory not found: {MEMORY_BUNDLES_DIR}")
        return puzzle_pieces
    
    # Pattern to match puzzle piece files
    puzzle_pattern = re.compile(r'puzzle-piece-(\d+)\.md')
    
    for file_path in Path(MEMORY_BUNDLES_DIR).rglob('*.md'):
        match = puzzle_pattern.search(file_path.name)
        if match:
            piece_number = int(match.group(1))
            piece_data = parse_puzzle_piece(file_path, piece_number)
            if piece_data:
                puzzle_pieces.append(piece_data)
    
    # Also check for puzzle references in other files
    for file_path in Path(MEMORY_BUNDLES_DIR).rglob('*.md'):
        if 'puzzle' in file_path.name.lower():
            additional_pieces = extract_puzzle_references(file_path)
            puzzle_pieces.extend(additional_pieces)
    
    # Deduplicate by number
    seen = set()
    unique_pieces = []
    for piece in puzzle_pieces:
        if piece['number'] not in seen:
            seen.add(piece['number'])
            unique_pieces.append(piece)
    
    return sorted(unique_pieces, key=lambda x: x['number'])

def parse_puzzle_piece(file_path, piece_number):
    """Parse puzzle piece markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract name from title
        name_match = re.search(r'#\s+(.+)', content)
        name = name_match.group(1) if name_match else f"Puzzle Piece {piece_number}"
        
        # Extract function/description
        function_match = re.search(r'\*\*Function\*\*:(.+?)(?:\n\n|\Z)', content, re.DOTALL)
        function = function_match.group(1).strip() if function_match else "No description available"
        
        return {
            'number': piece_number,
            'name': name,
            'function': function,
            'file_path': str(file_path),
            'discovered_at': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
    except Exception as e:
        print(f"  ⚠️  Error parsing {file_path}: {e}")
        return None

def extract_puzzle_references(file_path):
    """Extract puzzle piece references from markdown files"""
    pieces = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for puzzle piece mentions
        pattern = r'Puzzle\s+Piece\s+#?(\d+):\s*([^\n]+)'
        matches = re.finditer(pattern, content, re.IGNORECASE)
        
        for match in matches:
            pieces.append({
                'number': int(match.group(1)),
                'name': match.group(2).strip(),
                'function': "Referenced in memory bundles",
                'file_path': str(file_path),
                'discovered_at': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })
    except Exception as e:
        print(f"  ⚠️  Error extracting from {file_path}: {e}")
    
    return pieces

def create_puzzle_issue(repo, piece):
    """Create GitHub issue for puzzle piece"""
    title = f"🧩 Puzzle Piece #{piece['number']}: {piece['name']}"
    
    body = f"""## AGI Puzzle Piece Discovery

**Piece Number**: {piece['number']}  
**Name**: {piece['name']}  
**Discovery Date**: {piece['discovered_at']}

### Function
{piece['function']}

### Details
- **Source**: `{piece['file_path']}`
- **Status**: Discovered
- **Integration**: Pending

### Documentation
See `{piece['file_path']}` for complete details.

### Next Steps
1. ✅ Issue created (automated)
2. ⏳ Review puzzle piece details
3. ⏳ Integrate with existing framework
4. ⏳ Update AGI Puzzle progress documentation
5. ⏳ Validate integration through Progressive Ping-Pong

---

**Automated Discovery**: This issue was automatically created by B-Agent's AGI Puzzle Tracker.  
**Framework**: Part of the 56-piece AGI Puzzle Framework  
**Quality**: 97%+ target (Progressive Ping-Pong validated)

*Discovered: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}*
"""
    
    issue = repo.create_issue(
        title=title,
        body=body,
        labels=['agi-puzzle', 'enhancement', 'autonomous-discovery']
    )
    
    print(f"    ✅ Created issue #{issue.number} for puzzle piece #{piece['number']}")
    return issue

def update_puzzle_progress(puzzle_pieces, stats):
    """Update AGI puzzle progress documentation"""
    progress_file = 'AGI_PUZZLE_PROGRESS.md'
    
    content = f"""# 🧩 AGI Puzzle Progress

**Last Updated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Total Pieces Discovered**: {len(puzzle_pieces)} / 56  
**Progress**: {len(puzzle_pieces) / 56 * 100:.1f}%

## Discovered Puzzle Pieces

| # | Name | Status | Discovered |
|---|---|---|---|
"""
    
    for piece in puzzle_pieces:
        content += f"| {piece['number']} | {piece['name']} | ✅ Discovered | {piece['discovered_at'][:10]} |\n"
    
    content += f"""

## Statistics

- **Total Pieces**: {stats['total_pieces']}
- **New This Cycle**: {stats['new_pieces']}
- **Completion**: {len(puzzle_pieces) / 56 * 100:.1f}%

## Framework

The AGI Puzzle Framework systematically discovers and assembles 56 core AGI components through:

1. **Autonomous Discovery** - Continuous monitoring of memory bundles
2. **Automatic Documentation** - GitHub issues for each piece
3. **Progress Tracking** - Real-time completion metrics
4. **Integration Validation** - Progressive Ping-Pong quality checks

## Related Documentation

- [AGI Puzzle Protocol](AGI_PUZZLE_PROTOCOL.md)
- [Maximum Recursion Directive](MAXIMUM_RECURSION_DIRECTIVE.md)
- [Memory Bundles](memory-bundles/)

---

*This document is automatically updated by B-Agent's autonomous system every 30 minutes.*
"""
    
    with open(progress_file, 'w') as f:
        f.write(content)
    
    print(f"  📝 Updated {progress_file}")

def load_tracking_data():
    """Load existing puzzle tracking data"""
    if os.path.exists(PUZZLE_TRACKING_FILE):
        with open(PUZZLE_TRACKING_FILE, 'r') as f:
            return json.load(f)
    return {'pieces': []}

def save_tracking_data(data):
    """Save puzzle tracking data"""
    os.makedirs(os.path.dirname(PUZZLE_TRACKING_FILE), exist_ok=True)
    with open(PUZZLE_TRACKING_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def is_tracked(piece, tracking_data):
    """Check if puzzle piece is already tracked"""
    return any(p['number'] == piece['number'] for p in tracking_data['pieces'])

if __name__ == '__main__':
    sys.exit(main())
