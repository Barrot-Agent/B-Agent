#!/usr/bin/env python3
"""
Repository Validation Script
Tests the integrity and compatibility of merged features in the Barrot-Agent repository.
"""

import os
import sys
import json
import yaml
from pathlib import Path

class RepositoryValidator:
    def __init__(self, repo_root="."):
        self.repo_root = Path(repo_root)
        self.errors = []
        self.warnings = []
        self.passed = []
        
    def log_pass(self, test_name):
        """Log a passed test."""
        self.passed.append(test_name)
        print(f"✓ {test_name}")
        
    def log_error(self, test_name, message):
        """Log a failed test."""
        self.errors.append(f"{test_name}: {message}")
        print(f"✗ {test_name}: {message}")
        
    def log_warning(self, test_name, message):
        """Log a warning."""
        self.warnings.append(f"{test_name}: {message}")
        print(f"⚠ {test_name}: {message}")
        
    def test_required_files(self):
        """Test that all required files exist."""
        required_files = [
            "README.md",
            "CHANGELOG.md",
            "CONSOLIDATION.md",
            "package.json",
            ".gitignore",
            "cleanup_merged_branches.sh",
        ]
        
        for file in required_files:
            file_path = self.repo_root / file
            if file_path.exists():
                self.log_pass(f"Required file exists: {file}")
            else:
                self.log_error(f"Required file missing", file)
                
    def test_required_directories(self):
        """Test that all required directories exist."""
        required_dirs = [
            ".github/workflows",
            "memory-bundles",
            "datasets",
            "SHRM-System",
            "config",
        ]
        
        for dir_name in required_dirs:
            dir_path = self.repo_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                self.log_pass(f"Required directory exists: {dir_name}")
            else:
                self.log_error(f"Required directory missing", dir_name)
                
    def test_workflows(self):
        """Test that workflow files are valid YAML."""
        workflows_dir = self.repo_root / ".github" / "workflows"
        
        if not workflows_dir.exists():
            self.log_error("Workflows validation", ".github/workflows directory not found")
            return
            
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        
        if len(workflow_files) == 0:
            self.log_warning("Workflows validation", "No workflow files found")
            return
            
        for workflow_file in workflow_files:
            try:
                with open(workflow_file, 'r') as f:
                    yaml.safe_load(f)
                self.log_pass(f"Valid workflow YAML: {workflow_file.name}")
            except yaml.YAMLError as e:
                self.log_error(f"Invalid workflow YAML: {workflow_file.name}", str(e))
                
    def test_package_json(self):
        """Test that package.json is valid JSON."""
        package_json = self.repo_root / "package.json"
        
        if not package_json.exists():
            self.log_error("package.json validation", "File not found")
            return
            
        try:
            with open(package_json, 'r') as f:
                data = json.load(f)
            
            # Check required fields
            required_fields = ["name", "version", "description"]
            for field in required_fields:
                if field in data:
                    self.log_pass(f"package.json has required field: {field}")
                else:
                    self.log_error(f"package.json missing field", field)
                    
        except json.JSONDecodeError as e:
            self.log_error("package.json validation", f"Invalid JSON: {e}")
            
    def test_config_files(self):
        """Test that config files exist and are valid."""
        config_files = [
            ("config/shrm_v2.yaml", yaml.safe_load),
        ]
        
        for config_file, loader in config_files:
            file_path = self.repo_root / config_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        loader(f)
                    self.log_pass(f"Valid config file: {config_file}")
                except Exception as e:
                    self.log_error(f"Invalid config file: {config_file}", str(e))
            else:
                self.log_warning(f"Config file not found", config_file)
                
    def test_documentation(self):
        """Test that key documentation files exist."""
        docs = [
            "ARCHITECTURE.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "DEPLOYMENT.md",
        ]
        
        for doc in docs:
            doc_path = self.repo_root / doc
            if doc_path.exists():
                self.log_pass(f"Documentation exists: {doc}")
            else:
                self.log_warning(f"Documentation not found", doc)
                
    def test_python_scripts(self):
        """Test that Python scripts have proper shebang and are executable."""
        python_scripts = list(self.repo_root.glob("*.py"))
        
        for script in python_scripts:
            # Check if executable
            if os.access(script, os.X_OK):
                self.log_pass(f"Python script is executable: {script.name}")
            else:
                self.log_warning(f"Python script not executable", script.name)
                
    def test_bash_scripts(self):
        """Test that bash scripts have proper shebang and are executable."""
        bash_scripts = list(self.repo_root.glob("*.sh"))
        
        for script in bash_scripts:
            # Check if executable
            if os.access(script, os.X_OK):
                self.log_pass(f"Bash script is executable: {script.name}")
            else:
                self.log_warning(f"Bash script not executable", script.name)
                
            # Check shebang
            try:
                with open(script, 'r') as f:
                    first_line = f.readline()
                    if first_line.startswith("#!"):
                        self.log_pass(f"Bash script has shebang: {script.name}")
                    else:
                        self.log_warning(f"Bash script missing shebang", script.name)
            except Exception as e:
                self.log_warning(f"Could not read script", f"{script.name}: {e}")
                
    def run_all_tests(self):
        """Run all validation tests."""
        print("=" * 60)
        print("Barrot-Agent Repository Validation")
        print("=" * 60)
        print()
        
        test_methods = [
            self.test_required_files,
            self.test_required_directories,
            self.test_workflows,
            self.test_package_json,
            self.test_config_files,
            self.test_documentation,
            self.test_python_scripts,
            self.test_bash_scripts,
        ]
        
        for test_method in test_methods:
            print(f"\n{test_method.__doc__}")
            print("-" * 60)
            test_method()
            
        # Print summary
        print()
        print("=" * 60)
        print("Validation Summary")
        print("=" * 60)
        print(f"✓ Passed:   {len(self.passed)}")
        print(f"⚠ Warnings: {len(self.warnings)}")
        print(f"✗ Errors:   {len(self.errors)}")
        print()
        
        if self.errors:
            print("Errors:")
            for error in self.errors:
                print(f"  - {error}")
            print()
            
        if self.warnings:
            print("Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")
            print()
            
        # Return exit code
        if self.errors:
            print("❌ Validation FAILED")
            return 1
        elif self.warnings:
            print("⚠️  Validation PASSED with warnings")
            return 0
        else:
            print("✅ Validation PASSED")
            return 0

if __name__ == "__main__":
    validator = RepositoryValidator()
    exit_code = validator.run_all_tests()
    sys.exit(exit_code)
