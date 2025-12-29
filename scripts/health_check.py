#!/usr/bin/env python3
"""
Health Check Script for Barrot-Agent

This script performs comprehensive health checks on the Barrot-Agent system
including manifest validation, workflow validation, and system status checks.
"""
import sys
import yaml
from pathlib import Path
from datetime import datetime


class HealthChecker:
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = []
        
    def check(self, name, condition, error_msg=""):
        """Execute a health check"""
        if condition:
            print(f"✅ {name}")
            self.checks_passed += 1
            return True
        else:
            print(f"❌ {name}")
            if error_msg:
                print(f"   {error_msg}")
            self.checks_failed += 1
            return False
    
    def warn(self, name, condition, warning_msg=""):
        """Execute a warning check"""
        if condition:
            print(f"✅ {name}")
            return True
        else:
            print(f"⚠️  {name}")
            if warning_msg:
                print(f"   {warning_msg}")
            self.warnings.append(warning_msg if warning_msg else name)
            return False
    
    def check_manifest(self):
        """Check build manifest"""
        print("\n📋 Checking Build Manifest...")
        
        manifest_path = Path('build_manifest.yaml')
        if not self.check("Manifest file exists", manifest_path.exists()):
            return
        
        try:
            with open(manifest_path) as f:
                manifest = yaml.safe_load(f)
            self.check("Manifest is valid YAML", True)
        except Exception as e:
            self.check("Manifest is valid YAML", False, str(e))
            return
        
        self.check("Has build_signature", 'build_signature' in manifest)
        self.check("Has timestamp", 'timestamp' in manifest)
        self.check("Has modules", 'modules' in manifest)
        self.check("Has rail_status", 'rail_status' in manifest)
        
        if 'rail_status' in manifest:
            total_rails = len(manifest['rail_status'])
            active_rails = len(
                [r for r, s in manifest['rail_status'].items()
                 if isinstance(s, str) and s.lower() in ['active', 'operational']]
            )
            self.warn(
                f"Active rails: {active_rails}/{total_rails}",
                active_rails > 0,
                "No active rails detected in rail_status"
            )
    
    def check_workflows(self):
        """Check GitHub workflows"""
        print("\n⚙️  Checking Workflows...")
        
        workflows_dir = Path('.github/workflows')
        if not self.check("Workflows directory exists", workflows_dir.exists()):
            return
        
        workflow_files = list(workflows_dir.glob('*.yml')) + list(workflows_dir.glob('*.yaml'))
        self.check(f"Found {len(workflow_files)} workflow(s)", len(workflow_files) > 0)
        
        for workflow_file in workflow_files:
            try:
                with open(workflow_file) as f:
                    yaml.safe_load(f)
                self.check(f"{workflow_file.name} is valid", True)
            except Exception as e:
                self.check(f"{workflow_file.name} is valid", False, str(e))
    
    def check_documentation(self):
        """Check documentation"""
        print("\n📚 Checking Documentation...")
        
        required_docs = ['README.md', 'DEPLOYMENT.md', 'INGESTION_MANIFEST.md']
        for doc in required_docs:
            self.check(f"{doc} exists", Path(doc).exists())
        
        # Check if README has reasonable content
        readme_path = Path('README.md')
        if readme_path.exists():
            with open(readme_path) as f:
                content = f.read()
            self.check("README has content", len(content) > 100)
    
    def check_tests(self):
        """Check test infrastructure"""
        print("\n🧪 Checking Tests...")
        
        tests_dir = Path('tests')
        self.check("Tests directory exists", tests_dir.exists())
        
        if tests_dir.exists():
            test_files = list(tests_dir.glob('test_*.py'))
            self.check(f"Found {len(test_files)} test file(s)", len(test_files) > 0)
    
    def check_site(self):
        """Check site/dashboard"""
        print("\n🌐 Checking Site...")
        
        site_dir = Path('site')
        self.check("Site directory exists", site_dir.exists())
        
        if site_dir.exists():
            index_path = site_dir / 'index.html'
            self.check("index.html exists", index_path.exists())
            
            if index_path.exists():
                with open(index_path) as f:
                    content = f.read()
                self.check("index.html has content", len(content) > 100)
    
    def check_memory_bundles(self):
        """Check memory bundles"""
        print("\n🧠 Checking Memory Bundles...")
        
        bundles_dir = Path('memory-bundles')
        self.check("Memory bundles directory exists", bundles_dir.exists())
        
        if bundles_dir.exists():
            bundle_files = list(bundles_dir.glob('*.md')) + list(bundles_dir.glob('*.json'))
            self.warn(f"Found {len(bundle_files)} bundle file(s)", 
                     len(bundle_files) > 0,
                     "No bundle files found")
    
    def check_scripts(self):
        """Check utility scripts"""
        print("\n🔧 Checking Scripts...")
        
        scripts_dir = Path('scripts')
        self.warn("Scripts directory exists", scripts_dir.exists())
        
        if scripts_dir.exists():
            validate_script = scripts_dir / 'validate_manifest.py'
            self.check("validate_manifest.py exists", validate_script.exists())
    
    def print_summary(self):
        """Print health check summary"""
        print("\n" + "="*60)
        print("HEALTH CHECK SUMMARY")
        print("="*60)
        print(f"✅ Passed: {self.checks_passed}")
        print(f"❌ Failed: {self.checks_failed}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print("="*60)
        
        if self.checks_failed == 0:
            print("🎉 All critical health checks passed!")
            if len(self.warnings) > 0:
                print(f"⚠️  {len(self.warnings)} warning(s) - review recommended")
            return 0
        else:
            print(f"❌ {self.checks_failed} critical check(s) failed!")
            return 1


def main():
    """Main health check function"""
    print("="*60)
    print("🔍 BARROT-AGENT HEALTH CHECK")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    checker = HealthChecker()
    
    # Run all health checks
    checker.check_manifest()
    checker.check_workflows()
    checker.check_documentation()
    checker.check_tests()
    checker.check_site()
    checker.check_memory_bundles()
    checker.check_scripts()
    
    # Print summary and return status
    return checker.print_summary()


if __name__ == '__main__':
    sys.exit(main())
