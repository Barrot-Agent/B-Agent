"""
Tests for workflow integrity
"""
import unittest
import os
import yaml


class TestWorkflowIntegrity(unittest.TestCase):
    """Test suite for GitHub workflow validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.workflows_dir = os.path.join(os.path.dirname(__file__), '..', '.github', 'workflows')
    
    def test_workflows_directory_exists(self):
        """Test that workflows directory exists"""
        self.assertTrue(os.path.isdir(self.workflows_dir))
    
    def test_all_workflows_valid_yaml(self):
        """Test that all workflow files are valid YAML"""
        for filename in os.listdir(self.workflows_dir):
            if filename.endswith('.yml') or filename.endswith('.yaml'):
                filepath = os.path.join(self.workflows_dir, filename)
                with self.subTest(workflow=filename):
                    with open(filepath, 'r') as f:
                        try:
                            workflow = yaml.safe_load(f)
                            self.assertIsNotNone(workflow)
                        except yaml.YAMLError as e:
                            self.fail(f"Invalid YAML in {filename}: {e}")
    
    def test_workflows_have_required_fields(self):
        """Test that workflows have required fields"""
        for filename in os.listdir(self.workflows_dir):
            if filename.endswith('.yml') or filename.endswith('.yaml'):
                filepath = os.path.join(self.workflows_dir, filename)
                with self.subTest(workflow=filename):
                    with open(filepath, 'r') as f:
                        workflow = yaml.safe_load(f)
                        self.assertIn('name', workflow)
                        # YAML parser may convert 'on' to True; check keys explicitly
                        self.assertTrue(
                            any(k == 'on' or k is True for k in workflow.keys()),
                            "Workflow missing trigger configuration"
                        )
                        self.assertIn('jobs', workflow)
    
    def test_bbr_workflow_structure(self):
        """Test BBR workflow has correct structure"""
        bbr_path = os.path.join(self.workflows_dir, 'BBR.yml')
        self.assertTrue(os.path.exists(bbr_path), "BBR.yml workflow file is missing")
        
        with open(bbr_path, 'r') as f:
            workflow = yaml.safe_load(f)
            self.assertIn('update-manifest', workflow['jobs'])
            self.assertIn('publish-dashboard', workflow['jobs'])


if __name__ == '__main__':
    unittest.main()
