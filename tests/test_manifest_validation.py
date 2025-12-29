"""
Tests for build manifest validation
"""
import unittest
import yaml
import os
from datetime import datetime


class TestManifestValidation(unittest.TestCase):
    """Test suite for build manifest validation"""
    
    def setUp(self):
        """Load the build manifest before each test"""
        manifest_path = os.path.join(os.path.dirname(__file__), '..', 'build_manifest.yaml')
        with open(manifest_path, 'r') as f:
            self.manifest = yaml.safe_load(f)
    
    def test_manifest_has_required_fields(self):
        """Test that manifest contains all required fields"""
        required_fields = ['build_signature', 'timestamp', 'modules', 'rail_status']
        for field in required_fields:
            self.assertIn(field, self.manifest, f"Missing required field: {field}")
    
    def test_build_signature_format(self):
        """Test that build signature follows expected format"""
        self.assertIsInstance(self.manifest['build_signature'], str)
        self.assertTrue(self.manifest['build_signature'].startswith('BNDL-'))
    
    def test_timestamp_is_valid(self):
        """Test that timestamp is in ISO 8601 format"""
        timestamp = self.manifest['timestamp']
        # Convert to string if it's not already
        timestamp_str = str(timestamp)
        try:
            datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except ValueError:
            self.fail(f"Invalid timestamp format: {timestamp_str}")
    
    def test_modules_is_list(self):
        """Test that modules is a list"""
        self.assertIsInstance(self.manifest['modules'], list)
        self.assertGreater(len(self.manifest['modules']), 0)
    
    def test_rail_status_is_dict(self):
        """Test that rail_status is a dictionary"""
        self.assertIsInstance(self.manifest['rail_status'], dict)
        self.assertGreater(len(self.manifest['rail_status']), 0)
    
    def test_rail_status_values(self):
        """Test that rail status values are valid (canonical lowercase)"""
        # Canonical lowercase status values
        valid_statuses = [
            'active',
            'stable',
            'recursive',
            'evolving',
            'publishing',
            'initializing',
            'developing',
            'operational',
        ]
        for rail, status in self.manifest['rail_status'].items():
            # Normalize to lowercase for comparison
            normalized_status = str(status).lower()
            self.assertIn(
                normalized_status,
                valid_statuses,
                f"Invalid status '{status}' for rail '{rail}'"
            )
    
    def test_resources_list(self):
        """Test that resources list exists and is valid"""
        if 'resources' in self.manifest:
            self.assertIsInstance(self.manifest['resources'], list)
            self.assertGreater(len(self.manifest['resources']), 0)
    
    def test_capabilities_list(self):
        """Test that capabilities list exists and is valid"""
        if 'capabilities' in self.manifest:
            self.assertIsInstance(self.manifest['capabilities'], list)


if __name__ == '__main__':
    unittest.main()
