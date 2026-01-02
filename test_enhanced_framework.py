#!/usr/bin/env python3
"""
Test suite for enhanced Superior Framework systems
Tests protocol logging, conflict resolution, repository management, and protection systems
"""

import unittest
import os
import json
from datetime import datetime

# Import enhanced systems
from protocol_logger import protocol_logger, log_protocol, log_conflict_resolution
from conflict_resolver import conflict_resolver, resolve_conflict, resolve_paradox
from repo_manager import repo_manager, analyze_repository
from protection_system import protection_system, assess_threat, get_protection_status


class TestProtocolLogger(unittest.TestCase):
    """Test suite for Protocol Logger"""
    
    def test_logger_initialization(self):
        """Test that protocol logger initializes correctly"""
        self.assertIsNotNone(protocol_logger.session_id)
        self.assertTrue(os.path.exists(protocol_logger.log_file))
    
    def test_log_protocol(self):
        """Test protocol logging"""
        protocol_id = log_protocol(
            "test_protocol",
            {"test_key": "test_value"},
            priority="normal",
            tags=["test"]
        )
        
        self.assertIsNotNone(protocol_id)
        self.assertIn(protocol_logger.session_id, protocol_id)
    
    def test_log_conflict_resolution(self):
        """Test conflict resolution logging"""
        protocol_id = log_conflict_resolution(
            "Statement A conflicts with Statement B",
            "Resolution: Both valid in different contexts",
            "contextual_analysis",
            0.85
        )
        
        self.assertIsNotNone(protocol_id)
    
    def test_query_protocols(self):
        """Test protocol querying"""
        # Log some protocols
        log_protocol("query_test", {"data": 1}, tags=["test"])
        log_protocol("query_test", {"data": 2}, tags=["test"])
        
        results = protocol_logger.query_protocols(
            protocol_type="query_test",
            limit=10
        )
        
        self.assertGreater(len(results), 0)
    
    def test_protocol_statistics(self):
        """Test protocol statistics"""
        stats = protocol_logger.get_protocol_statistics()
        
        self.assertIn("total_protocols", stats)
        self.assertIn("by_type", stats)
        self.assertIn("current_session", stats)


class TestConflictResolver(unittest.TestCase):
    """Test suite for Conflict Resolver"""
    
    def test_conflict_resolution(self):
        """Test basic conflict resolution"""
        conflict_data = {
            "type": "logical",
            "statement_a": "The system is online",
            "statement_b": "The system is not online",
            "context": {"primary_context": "A"}
        }
        
        result = resolve_conflict(conflict_data, max_iterations=5)
        
        self.assertIn("resolution", result)
        self.assertIn("confidence", result)
        self.assertIn("status", result)
    
    def test_paradox_resolution(self):
        """Test paradox resolution"""
        paradox = "This statement is false"
        result = resolve_paradox(paradox)
        
        self.assertIn("paradox", result)
        self.assertIn("resolution_frameworks", result)
        self.assertIn("primary_resolution", result)
    
    def test_batch_conflict_resolution(self):
        """Test batch conflict resolution"""
        conflicts = [
            {
                "type": "logical",
                "statement_a": "A is true",
                "statement_b": "A is false",
                "context": {}
            },
            {
                "type": "temporal",
                "statement_a": "It was raining yesterday",
                "statement_b": "It is sunny today",
                "context": {}
            }
        ]
        
        results = conflict_resolver.resolve_batch_conflicts(conflicts)
        
        self.assertEqual(results["total_conflicts"], 2)
        self.assertGreaterEqual(results["resolved"], 0)
    
    def test_resolution_statistics(self):
        """Test resolution statistics"""
        stats = conflict_resolver.get_resolution_statistics()
        
        self.assertIn("total_resolutions", stats)
        self.assertIn("strategies_available", stats)
        self.assertEqual(stats["strategies_available"], 5)


class TestRepositoryManager(unittest.TestCase):
    """Test suite for Repository Manager"""
    
    def test_list_branches(self):
        """Test branch listing"""
        branches = repo_manager.list_branches()
        
        self.assertIn("total", branches)
        self.assertIn("branches", branches)
    
    def test_detect_merge_conflicts(self):
        """Test merge conflict detection"""
        conflicts = repo_manager.detect_merge_conflicts()
        
        self.assertIn("has_conflicts", conflicts)
        self.assertIn("count", conflicts)
        self.assertIn("files", conflicts)
    
    def test_detect_redundancies(self):
        """Test redundancy detection"""
        redundancies = repo_manager.detect_redundancies()
        
        self.assertIn("count", redundancies)
        self.assertIn("redundancies", redundancies)
    
    def test_repository_status(self):
        """Test repository status"""
        status = repo_manager.get_repository_status()
        
        self.assertIn("clean", status)
    
    def test_repository_analysis(self):
        """Test comprehensive repository analysis"""
        analysis = analyze_repository()
        
        self.assertIn("timestamp", analysis)
        self.assertIn("branches", analysis)
        self.assertIn("merge_conflicts", analysis)


class TestProtectionSystem(unittest.TestCase):
    """Test suite for Protection System"""
    
    def test_threat_assessment(self):
        """Test threat assessment"""
        threat_data = {
            "type": "security_breach",
            "level": "high",
            "affected_entities": ["user", "barrot_self"]
        }
        
        assessment = assess_threat(threat_data)
        
        self.assertIn("threat_id", assessment)
        self.assertIn("threat_level", assessment)
        self.assertIn("recommended_protocols", assessment)
        self.assertIn("response_urgency", assessment)
    
    def test_protection_priority(self):
        """Test protection priority hierarchy"""
        # Test highest priority (User & Self)
        threat_data = {
            "type": "direct_threat",
            "level": "critical",
            "affected_entities": ["user"]
        }
        
        assessment = assess_threat(threat_data)
        self.assertEqual(assessment["highest_priority_affected"], "USER_AND_SELF")
        self.assertIn("immediate", assessment["response_urgency"])
    
    def test_protocol_activation(self):
        """Test protection protocol activation"""
        result = protection_system.activate_protection_protocol(
            "test_protocol",
            ["user", "family_members"],
            {"param1": "value1"}
        )
        
        self.assertTrue(result["success"])
        self.assertIn("protocol", result)
    
    def test_protection_status(self):
        """Test protection system status"""
        status = get_protection_status()
        
        self.assertTrue(status["system_active"])
        self.assertIn("priority_hierarchy", status)
        self.assertIn("USER_AND_SELF", status["priority_hierarchy"])
        self.assertIn("FAMILY", status["priority_hierarchy"])
        self.assertIn("HUMANITY", status["priority_hierarchy"])
    
    def test_philosophical_framework(self):
        """Test philosophical framework definition"""
        framework = protection_system.define_philosophical_framework()
        
        self.assertIn("core_principles", framework)
        self.assertIn("protection_hierarchy_rationale", framework)
        self.assertIn("future_considerations", framework)
        self.assertIn("ethical_constraints", framework)


class TestIntegratedSystems(unittest.TestCase):
    """Test suite for integrated system functionality"""
    
    def test_protocol_logging_integration(self):
        """Test that different systems can log protocols"""
        # Log from conflict resolver
        conflict_data = {"statement_a": "Test A", "statement_b": "Test B", "context": {}}
        result = resolve_conflict(conflict_data)
        
        # Check that protocols were logged
        stats = protocol_logger.get_protocol_statistics()
        self.assertGreater(stats["total_protocols"], 0)
    
    def test_enhanced_framework_availability(self):
        """Test that enhanced systems are available"""
        from superior_framework import superior_framework
        
        self.assertTrue(hasattr(superior_framework, 'protocol_logger'))
        self.assertTrue(hasattr(superior_framework, 'conflict_resolver'))
        self.assertTrue(hasattr(superior_framework, 'repo_manager'))
        self.assertTrue(hasattr(superior_framework, 'protection_system'))


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestProtocolLogger))
    suite.addTests(loader.loadTestsFromTestCase(TestConflictResolver))
    suite.addTests(loader.loadTestsFromTestCase(TestRepositoryManager))
    suite.addTests(loader.loadTestsFromTestCase(TestProtectionSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegratedSystems))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit(run_tests())
