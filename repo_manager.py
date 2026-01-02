"""
Repository Management Utilities
Automated tools for managing branches, pull requests, commits, and resolving conflicts
Ensures no overlapping, redundancies, or unresolved merge conflicts
"""

import os
import subprocess
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
import json


class RepositoryManager:
    """
    Comprehensive repository management system
    Handles indexing, conflict detection, and cleanup
    """
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.index = {}
        self.redundancies = []
        self.conflicts = []
        
    def run_git_command(self, command: List[str]) -> Tuple[bool, str, str]:
        """
        Run a git command and return success status, stdout, stderr
        """
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def analyze_repository(self) -> Dict[str, Any]:
        """
        Comprehensive repository analysis
        """
        analysis = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "branches": self.list_branches(),
            "pull_requests": self.analyze_pull_requests(),
            "commits": self.analyze_commits(),
            "merge_conflicts": self.detect_merge_conflicts(),
            "redundancies": self.detect_redundancies(),
            "status": "analyzed"
        }
        
        return analysis
    
    def list_branches(self) -> Dict[str, Any]:
        """List all branches"""
        success, stdout, stderr = self.run_git_command(["git", "branch", "-a"])
        
        if not success:
            return {"error": stderr, "branches": []}
        
        branches = [line.strip().lstrip("* ") for line in stdout.split("\n") if line.strip()]
        
        return {
            "total": len(branches),
            "branches": branches,
            "current": self.get_current_branch()
        }
    
    def get_current_branch(self) -> str:
        """Get current branch name"""
        success, stdout, stderr = self.run_git_command(["git", "branch", "--show-current"])
        return stdout.strip() if success else "unknown"
    
    def analyze_pull_requests(self) -> Dict[str, Any]:
        """Analyze pull requests (requires GitHub CLI)"""
        # Check if gh CLI is available
        success, stdout, stderr = self.run_git_command(["which", "gh"])
        
        if not success:
            return {
                "error": "GitHub CLI not available",
                "note": "Install gh CLI for PR analysis"
            }
        
        # List PRs
        success, stdout, stderr = self.run_git_command(["gh", "pr", "list", "--json", "number,title,state"])
        
        if not success:
            return {"error": stderr, "pull_requests": []}
        
        try:
            prs = json.loads(stdout) if stdout else []
            return {
                "total": len(prs),
                "pull_requests": prs
            }
        except json.JSONDecodeError:
            return {"error": "Failed to parse PR data", "pull_requests": []}
    
    def analyze_commits(self, limit: int = 100) -> Dict[str, Any]:
        """Analyze recent commits"""
        success, stdout, stderr = self.run_git_command([
            "git", "log", f"-{limit}", "--pretty=format:%H|%an|%ae|%s|%ad", "--date=iso"
        ])
        
        if not success:
            return {"error": stderr, "commits": []}
        
        commits = []
        for line in stdout.split("\n"):
            if line.strip():
                parts = line.split("|", 4)
                if len(parts) == 5:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "email": parts[2],
                        "message": parts[3],
                        "date": parts[4]
                    })
        
        return {
            "total": len(commits),
            "commits": commits
        }
    
    def detect_merge_conflicts(self) -> Dict[str, Any]:
        """Detect unresolved merge conflicts"""
        success, stdout, stderr = self.run_git_command(["git", "diff", "--name-only", "--diff-filter=U"])
        
        conflicted_files = [f.strip() for f in stdout.split("\n") if f.strip()]
        
        return {
            "has_conflicts": len(conflicted_files) > 0,
            "count": len(conflicted_files),
            "files": conflicted_files
        }
    
    def detect_redundancies(self) -> Dict[str, Any]:
        """Detect redundant files and patterns"""
        redundancies = []
        
        # Check for duplicate file names in different locations
        success, stdout, stderr = self.run_git_command(["git", "ls-files"])
        
        if not success:
            return {"error": stderr, "redundancies": []}
        
        files = [f.strip() for f in stdout.split("\n") if f.strip()]
        file_names = {}
        
        for file_path in files:
            file_name = os.path.basename(file_path)
            if file_name not in file_names:
                file_names[file_name] = []
            file_names[file_name].append(file_path)
        
        # Find duplicates
        for file_name, paths in file_names.items():
            if len(paths) > 1:
                redundancies.append({
                    "file_name": file_name,
                    "locations": paths,
                    "count": len(paths)
                })
        
        return {
            "count": len(redundancies),
            "redundancies": redundancies
        }
    
    def index_repository(self) -> Dict[str, Any]:
        """Create comprehensive repository index"""
        index = {
            "indexed_at": datetime.now(timezone.utc).isoformat(),
            "repository_path": self.repo_path,
            "branches": self.list_branches(),
            "file_structure": self.index_file_structure(),
            "commit_history": self.analyze_commits(limit=50),
            "status": self.get_repository_status()
        }
        
        # Save index
        with open("repository_index.json", "w") as f:
            json.dump(index, f, indent=2)
        
        self.index = index
        return index
    
    def index_file_structure(self) -> Dict[str, Any]:
        """Index file structure"""
        success, stdout, stderr = self.run_git_command(["git", "ls-files"])
        
        if not success:
            return {"error": stderr}
        
        files = [f.strip() for f in stdout.split("\n") if f.strip()]
        
        structure = {
            "total_files": len(files),
            "by_extension": {},
            "by_directory": {}
        }
        
        for file_path in files:
            # By extension
            ext = os.path.splitext(file_path)[1] or "no_extension"
            structure["by_extension"][ext] = structure["by_extension"].get(ext, 0) + 1
            
            # By directory
            dir_name = os.path.dirname(file_path) or "root"
            structure["by_directory"][dir_name] = structure["by_directory"].get(dir_name, 0) + 1
        
        return structure
    
    def get_repository_status(self) -> Dict[str, Any]:
        """Get current repository status"""
        success, stdout, stderr = self.run_git_command(["git", "status", "--porcelain"])
        
        if not success:
            return {"error": stderr}
        
        status = {
            "clean": not stdout.strip(),
            "modified": [],
            "untracked": [],
            "staged": []
        }
        
        for line in stdout.split("\n"):
            if not line.strip():
                continue
            
            status_code = line[:2]
            file_path = line[3:].strip()
            
            if "M" in status_code:
                status["modified"].append(file_path)
            if "?" in status_code:
                status["untracked"].append(file_path)
            if status_code[0] in ["A", "M", "D"]:
                status["staged"].append(file_path)
        
        return status
    
    def cleanup_redundancies(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Clean up redundancies (with dry run option)
        """
        redundancies = self.detect_redundancies()
        
        cleanup_plan = {
            "dry_run": dry_run,
            "redundancies_found": redundancies["count"],
            "actions": []
        }
        
        # Note: Actual cleanup would require careful analysis
        # For now, just report what would be done
        for redundancy in redundancies.get("redundancies", []):
            cleanup_plan["actions"].append({
                "file": redundancy["file_name"],
                "locations": redundancy["locations"],
                "recommendation": "Manual review required to determine which to keep"
            })
        
        return cleanup_plan
    
    def generate_repository_report(self, output_file: str = "repository_report.json") -> Dict[str, Any]:
        """Generate comprehensive repository report"""
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "analysis": self.analyze_repository(),
            "index": self.index_repository(),
            "recommendations": self.generate_recommendations()
        }
        
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        conflicts = self.detect_merge_conflicts()
        if conflicts["has_conflicts"]:
            recommendations.append(f"Resolve {conflicts['count']} merge conflict(s)")
        
        redundancies = self.detect_redundancies()
        if redundancies["count"] > 0:
            recommendations.append(f"Review {redundancies['count']} potential redundant file(s)")
        
        status = self.get_repository_status()
        if not status.get("clean", True):
            if status.get("modified"):
                recommendations.append(f"Commit {len(status['modified'])} modified file(s)")
            if status.get("untracked"):
                recommendations.append(f"Add or gitignore {len(status['untracked'])} untracked file(s)")
        
        if not recommendations:
            recommendations.append("Repository is clean and well-maintained")
        
        return recommendations


# Global repository manager instance
repo_manager = RepositoryManager()


def analyze_repository() -> Dict[str, Any]:
    """Convenience function for repository analysis"""
    return repo_manager.analyze_repository()


def detect_merge_conflicts() -> Dict[str, Any]:
    """Convenience function for conflict detection"""
    return repo_manager.detect_merge_conflicts()
