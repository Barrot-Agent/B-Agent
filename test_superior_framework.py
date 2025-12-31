#!/usr/bin/env python3
"""
Integration tests for the Superior Framework
Validates the integration of Ping Ponging, UPATSTAR, and MMI
"""

import unittest
import json
import os
from datetime import datetime

# Import framework components
from superior_framework import (
    superior_framework,
    process_superior,
    check_integration,
    get_framework_status
)
from upatstar import upatstar_orchestrator, process_adaptive
from mmi_integration import mmi_orchestrator, ingest_multi_modal


class TestSuperiorFrameworkIntegration(unittest.TestCase):
    """Test suite for Superior Framework integration"""
    
    def test_framework_initialization(self):
        """Test that the framework initializes correctly"""
        self.assertTrue(superior_framework.active)
        self.assertIsNotNone(superior_framework.initialization_time)
        self.assertEqual(superior_framework.vantage_analyzer.vantage_points, 
                        ["technical", "strategic", "operational", "innovative", "systematic", "holistic"])
    
    def test_integration_check(self):
        """Test seamless integration check"""
        status = check_integration()
        self.assertTrue(status["framework_active"])
        self.assertEqual(status["backward_compatibility"], "maintained")
        self.assertEqual(status["infrastructure_impact"], "seamless_frictionless")
        self.assertEqual(status["integration_quality"], "superior")
    
    def test_framework_status(self):
        """Test framework status retrieval"""
        status = get_framework_status()
        self.assertIn("framework", status)
        self.assertIn("version", status)
        self.assertIn("components", status)
        self.assertEqual(status["version"], "1.0.0")
        self.assertTrue(status["active"])
    
    def test_vantage_point_analysis(self):
        """Test multi-vantage point analysis"""
        result = superior_framework.vantage_analyzer.analyze_from_all_vantage_points(
            "Test problem for analysis"
        )
        self.assertIn("vantage_points_analyzed", result)
        self.assertEqual(len(result["vantage_points_analyzed"]), 6)
        self.assertIn("synthesis", result)
    
    def test_upatstar_adaptive_reasoning(self):
        """Test UPATSTAR adaptive reasoning"""
        result = process_adaptive(
            problem="Optimize system performance",
            context={"complexity": "medium", "constraints": ["efficiency"]}
        )
        self.assertIn("selected_strategy", result)
        self.assertIn("reasoning_result", result)
        self.assertIn("upatstar_metadata", result)
    
    def test_mmi_multi_modal_integration(self):
        """Test MMI multi-modal integration"""
        result = ingest_multi_modal({
            "text_data": "Sample text",
            "structured_data": {"key": "value"},
            "timestamp": "2025-12-31T00:00:00Z"
        })
        self.assertIn("ingestion_id", result)
        self.assertIn("modalities_processed", result)
        self.assertIn("integration_result", result)
    
    def test_superior_framework_processing(self):
        """Test complete Superior Framework processing"""
        result = process_superior(
            task="Test task for superior framework",
            data={"test_key": "test_value"},
            enable_pingpong=False
        )
        self.assertIn("task", result)
        self.assertIn("vantage_analysis", result)
        self.assertIn("upatstar_processing", result)
        self.assertIn("superior_framework_metadata", result)
        self.assertFalse(result["pingpong_emitted"])
    
    def test_pingpong_emission(self):
        """Test ping pong emission functionality"""
        # Clear any existing pingpong_request.json
        if os.path.exists("pingpong_request.json"):
            os.remove("pingpong_request.json")
        
        result = process_superior(
            task="Test task requiring pingpong",
            data={},
            enable_pingpong=True
        )
        
        self.assertTrue(result["pingpong_emitted"])
        self.assertTrue(os.path.exists("pingpong_request.json"))
        
        # Verify the pingpong request file structure
        with open("pingpong_request.json", "r") as f:
            pingpong_data = json.load(f)
        
        self.assertIn("timestamp", pingpong_data)
        self.assertIn("payload", pingpong_data)
        self.assertEqual(pingpong_data["origin"], "barrot")
        self.assertEqual(pingpong_data["directive"], "offload_pingpong")
    
    def test_component_availability(self):
        """Test that all framework components are available"""
        status = get_framework_status()
        components = status["components"]
        
        self.assertIn("vantage_point_analyzer", components)
        self.assertIn("upatstar", components)
        self.assertIn("mmi", components)
        self.assertIn("pingpong", components)
    
    def test_upatstar_reasoning_strategies(self):
        """Test all UPATSTAR reasoning strategies"""
        strategies = ["analytical", "creative", "systematic", "intuitive", "hybrid"]
        
        for strategy in strategies:
            result = upatstar_orchestrator.reasoning_engine.apply_reasoning(
                "Test problem", strategy, {}
            )
            self.assertEqual(result["strategy"], strategy)
            self.assertIn("confidence", result)
            self.assertIn("approach", result)
    
    def test_mmi_modality_processing(self):
        """Test MMI processing for different modalities"""
        modalities = ["text", "structured", "temporal", "spatial", "hybrid"]
        
        for modality in modalities:
            result = mmi_orchestrator.modality_processor.process_modality(
                "test_data", modality
            )
            self.assertEqual(result["modality"], modality)
            self.assertTrue(result["processed"])
            self.assertTrue(result["success"])
    
    def test_framework_metrics_tracking(self):
        """Test that framework tracks metrics correctly"""
        # Get initial metrics
        initial_status = get_framework_status()
        initial_ops = initial_status["operations_count"]
        
        # Perform an operation
        process_superior("Test task", {}, False)
        
        # Check metrics updated
        final_status = get_framework_status()
        final_ops = final_status["operations_count"]
        
        self.assertGreater(final_ops, initial_ops)
    
    def test_backward_compatibility(self):
        """Test backward compatibility with existing Barrot systems"""
        # Import existing modules to ensure they still work
        try:
            from barrot_integration import barrot_system
            self.assertTrue(barrot_system.integration_active)
            
            # Verify Superior Framework integration doesn't break existing functionality
            if hasattr(barrot_system, 'superior_framework_enabled'):
                self.assertTrue(barrot_system.superior_framework_enabled)
        except ImportError:
            self.skipTest("barrot_integration dependencies not available")


class TestUPATSTAR(unittest.TestCase):
    """Test suite for UPATSTAR component"""
    
    def test_strategy_selection(self):
        """Test intelligent strategy selection"""
        contexts = [
            {"type": "creative", "complexity": "medium"},
            {"complexity": "high", "constraints": ["time_critical"]},
            {"constraints": ["methodical"], "complexity": "high"}
        ]
        
        for ctx in contexts:
            strategy = upatstar_orchestrator.reasoning_engine.select_optimal_strategy(ctx)
            self.assertIn(strategy, ["analytical", "creative", "systematic", "intuitive", "hybrid"])
    
    def test_system_status(self):
        """Test UPATSTAR system status"""
        status = upatstar_orchestrator.get_system_status()
        self.assertTrue(status["active"])
        self.assertEqual(status["reasoning_strategies_available"], 5)


class TestMMI(unittest.TestCase):
    """Test suite for MMI component"""
    
    def test_modality_inference(self):
        """Test automatic modality inference"""
        test_data = {
            "text_field": "Some text",
            "structured_field": {"nested": "data"},
            "created_time": "2025-12-31",  # Key name contains 'time' for temporal inference
            "other": 123
        }
        
        modality_map = mmi_orchestrator._infer_modalities(test_data)
        self.assertEqual(modality_map["text_field"], "text")
        self.assertEqual(modality_map["structured_field"], "structured")
        self.assertEqual(modality_map["created_time"], "temporal")  # Inferred from key name pattern
    
    def test_self_ingestion(self):
        """Test MMI self-ingestion"""
        result = mmi_orchestrator.self_ingest(recursion_depth=2)
        self.assertEqual(result["operation"], "mmi_self_ingestion")
        self.assertEqual(result["recursion_depth"], 2)
        self.assertEqual(result["glyph"], "GLYPH_MMI")
    
    def test_system_status(self):
        """Test MMI system status"""
        status = mmi_orchestrator.get_system_status()
        self.assertTrue(status["active"])
        self.assertEqual(len(status["supported_modalities"]), 5)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSuperiorFrameworkIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestUPATSTAR))
    suite.addTests(loader.loadTestsFromTestCase(TestMMI))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit(run_tests())
