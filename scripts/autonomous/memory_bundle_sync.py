#!/usr/bin/env python3
"""
Memory Bundle Synchronization
Automatically commits and syncs memory bundles to repository
Part of B-Agent's autonomous operations
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
import json
import sys

MEMORY_BUNDLES_DIR = 'memory-bundles'
SYNC_LOG_FILE = 'reports/memory-bundle-sync.json'

def main():
    """Main memory bundle sync logic"""
    print(f"📦 Synchronizing memory bundles...")
    
    stats = {
        'files_changed': 0,
        'files_added': 0,
        'files_modified': 0,
        'files_deleted': 0,
        'commit_created': False,
        'sync_successful': False
    }
    
    # Check if memory bundles directory exists
    if not os.path.exists(MEMORY_BUNDLES_DIR):
        print(f"  ⚠️  Memory bundles directory not found: {MEMORY_BUNDLES_DIR}")
        return 0
    
    # Get git status for memory bundles
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain', MEMORY_BUNDLES_DIR],
            capture_output=True,
            text=True,
            check=True
        )
        
        changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        if not changes or changes == ['']:
            print("  ✅ No changes to sync")
            stats['sync_successful'] = True
            save_sync_log(stats)
            return 0
        
        # Analyze changes
        for change in changes:
            if not change:
                continue
            
            status = change[:2].strip()
            file_path = change[3:]
            
            stats['files_changed'] += 1
            
            if status == 'A' or status == '??':
                stats['files_added'] += 1
                print(f"  ➕ Added: {file_path}")
            elif status == 'M':
                stats['files_modified'] += 1
                print(f"  ✏️  Modified: {file_path}")
            elif status == 'D':
                stats['files_deleted'] += 1
                print(f"  ➖ Deleted: {file_path}")
        
        # Stage changes
        subprocess.run(
            ['git', 'add', MEMORY_BUNDLES_DIR],
            check=True
        )
        
        # Create commit
        commit_message = generate_commit_message(stats)
        subprocess.run(
            ['git', 'commit', '-m', commit_message],
            check=True
        )
        
        stats['commit_created'] = True
        print(f"  ✅ Commit created")
        
        # Note: Push is handled by the workflow
        stats['sync_successful'] = True
        
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Git operation failed: {e}")
        stats['sync_successful'] = False
    except Exception as e:
        print(f"  ❌ Sync failed: {e}")
        stats['sync_successful'] = False
    
    # Save sync log
    save_sync_log(stats)
    
    print(f"\n📊 Memory Bundle Sync Summary:")
    print(f"  Files changed: {stats['files_changed']}")
    print(f"  Added: {stats['files_added']}")
    print(f"  Modified: {stats['files_modified']}")
    print(f"  Deleted: {stats['files_deleted']}")
    print(f"  Commit created: {stats['commit_created']}")
    print(f"  Sync successful: {stats['sync_successful']}")
    
    return 0 if stats['sync_successful'] else 1

def generate_commit_message(stats):
    """Generate descriptive commit message"""
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    message = f"📦 Memory Bundle Sync: {timestamp}\n\n"
    message += f"Automated synchronization of memory bundles\n\n"
    message += f"Changes:\n"
    message += f"- Added: {stats['files_added']} files\n"
    message += f"- Modified: {stats['files_modified']} files\n"
    message += f"- Deleted: {stats['files_deleted']} files\n"
    message += f"- Total: {stats['files_changed']} files changed\n\n"
    message += "Synchronized by B-Agent autonomous system\n"
    message += "Part of Maximum Recursion Directive continuous operation"
    
    return message

def save_sync_log(stats):
    """Save sync log for tracking"""
    os.makedirs('reports', exist_ok=True)
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'stats': stats
    }
    
    # Load existing log
    log_data = {'syncs': []}
    if os.path.exists(SYNC_LOG_FILE):
        try:
            with open(SYNC_LOG_FILE, 'r') as f:
                log_data = json.load(f)
        except:
            pass
    
    # Append new entry
    log_data['syncs'].append(log_entry)
    
    # Keep only last 100 entries
    log_data['syncs'] = log_data['syncs'][-100:]
    
    # Save
    with open(SYNC_LOG_FILE, 'w') as f:
        json.dump(log_data, f, indent=2)

if __name__ == '__main__':
    sys.exit(main())
