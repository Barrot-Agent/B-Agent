"""
Advanced Algorithmic Logic Module for Barrot-Agent
Implements advanced algorithmic optimizations for maximum computational efficiency
"""

import time
import functools
from typing import Dict, List, Any, Callable, Optional, Tuple
from datetime import datetime, timezone
from collections import defaultdict


class AlgorithmicOptimizer:
    """
    Advanced algorithmic optimization engine
    Provides computational efficiency analysis and optimization
    """
    
    def __init__(self):
        self.performance_metrics = defaultdict(list)
        self.optimization_cache = {}
        self.algorithm_registry = {}
    
    def register_algorithm(self, name: str, func: Callable, 
                          complexity: str = "O(n)"):
        """Register an algorithm for optimization tracking"""
        self.algorithm_registry[name] = {
            "function": func,
            "complexity": complexity,
            "executions": 0,
            "total_time": 0.0,
            "optimizations_applied": 0
        }
    
    def optimize_execution(self, algorithm_name: str) -> Callable:
        """
        Decorator to optimize algorithm execution
        Applies memoization, lazy evaluation, and performance tracking
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(algorithm_name, args, kwargs)
                
                # Check cache
                if cache_key in self.optimization_cache:
                    return self.optimization_cache[cache_key]
                
                # Execute and time
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Record metrics
                self._record_performance(algorithm_name, execution_time)
                
                # Cache result
                self.optimization_cache[cache_key] = result
                
                return result
            return wrapper
        return decorator
    
    def parallel_optimization(self, tasks: List[Callable], 
                             max_workers: int = 4) -> List[Any]:
        """
        Execute tasks in parallel for optimal performance
        Simulated parallel execution for demonstration
        """
        results = []
        
        # In a real implementation, use threading or multiprocessing
        # For minimal changes, we'll execute sequentially but track optimization potential
        for task in tasks:
            result = task()
            results.append(result)
        
        self._record_parallel_execution(len(tasks), max_workers)
        
        return results
    
    def adaptive_complexity_analysis(self, algorithm: Callable, 
                                    input_sizes: List[int]) -> Dict[str, Any]:
        """
        Analyze algorithm complexity by testing with different input sizes
        """
        timings = []
        
        for size in input_sizes:
            # Generate test input of given size
            test_input = list(range(size))
            
            # Measure execution time
            start_time = time.time()
            try:
                algorithm(test_input)
                execution_time = time.time() - start_time
                timings.append({"size": size, "time": execution_time})
            except Exception as e:
                timings.append({"size": size, "time": None, "error": str(e)})
        
        # Analyze complexity pattern
        complexity_class = self._infer_complexity(timings)
        
        return {
            "timings": timings,
            "inferred_complexity": complexity_class,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def dynamic_algorithm_selection(self, problem_type: str, 
                                   data_characteristics: Dict[str, Any]) -> str:
        """
        Dynamically select the optimal algorithm based on data characteristics
        """
        # Analyze data characteristics
        size = data_characteristics.get("size", 0)
        sorted_data = data_characteristics.get("sorted", False)
        data_type = data_characteristics.get("type", "general")
        
        # Select optimal algorithm
        if problem_type == "sorting":
            if size < 50:
                return "insertion_sort"  # O(n²) but fast for small n
            elif sorted_data:
                return "timsort"  # O(n) for already sorted
            else:
                return "quicksort"  # O(n log n) average
        
        elif problem_type == "searching":
            if sorted_data:
                return "binary_search"  # O(log n)
            else:
                return "linear_search"  # O(n)
        
        return "default_algorithm"
    
    def computational_efficiency_score(self, algorithm_name: str) -> float:
        """
        Calculate computational efficiency score for an algorithm
        """
        if algorithm_name not in self.algorithm_registry:
            return 0.0
        
        algo_data = self.algorithm_registry[algorithm_name]
        executions = algo_data["executions"]
        
        if executions == 0:
            return 0.0
        
        avg_time = algo_data["total_time"] / executions
        optimizations = algo_data["optimizations_applied"]
        
        # Higher score = better efficiency
        # Factor in execution time, optimization count, and complexity
        base_score = 1.0 / (avg_time + 0.001)  # Avoid division by zero
        optimization_bonus = optimizations * 0.1
        
        return min(base_score + optimization_bonus, 100.0)
    
    def resource_allocation_optimizer(self, tasks: List[Dict[str, Any]], 
                                     available_resources: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Optimize resource allocation across multiple tasks
        """
        # Sort tasks by priority and resource requirements
        prioritized_tasks = sorted(
            tasks, 
            key=lambda t: t.get("priority", 0) / (t.get("resources_required", 1) + 0.1),
            reverse=True
        )
        
        allocated_tasks = []
        remaining_resources = available_resources.copy()
        
        for task in prioritized_tasks:
            required = task.get("resources_required", 0)
            resource_type = task.get("resource_type", "compute")
            
            if remaining_resources.get(resource_type, 0) >= required:
                allocated_tasks.append({
                    **task,
                    "allocated": True,
                    "allocation_timestamp": datetime.now(timezone.utc).isoformat()
                })
                remaining_resources[resource_type] -= required
            else:
                allocated_tasks.append({
                    **task,
                    "allocated": False,
                    "reason": "insufficient_resources"
                })
        
        return allocated_tasks
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        total_optimizations = sum(
            algo["optimizations_applied"] 
            for algo in self.algorithm_registry.values()
        )
        
        total_executions = sum(
            algo["executions"] 
            for algo in self.algorithm_registry.values()
        )
        
        return {
            "registered_algorithms": len(self.algorithm_registry),
            "total_executions": total_executions,
            "total_optimizations_applied": total_optimizations,
            "cache_size": len(self.optimization_cache),
            "efficiency_scores": {
                name: self.computational_efficiency_score(name)
                for name in self.algorithm_registry
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    # Helper methods
    
    def _generate_cache_key(self, algorithm_name: str, 
                           args: tuple, kwargs: dict) -> str:
        """Generate a cache key for memoization"""
        return f"{algorithm_name}_{hash(str(args))}_{hash(str(kwargs))}"
    
    def _record_performance(self, algorithm_name: str, execution_time: float):
        """Record performance metrics"""
        self.performance_metrics[algorithm_name].append({
            "execution_time": execution_time,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        if algorithm_name in self.algorithm_registry:
            self.algorithm_registry[algorithm_name]["executions"] += 1
            self.algorithm_registry[algorithm_name]["total_time"] += execution_time
    
    def _record_parallel_execution(self, task_count: int, max_workers: int):
        """Record parallel execution metrics"""
        self.performance_metrics["parallel_executions"].append({
            "task_count": task_count,
            "max_workers": max_workers,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def _infer_complexity(self, timings: List[Dict[str, Any]]) -> str:
        """Infer algorithmic complexity from timing data"""
        if not timings or len(timings) < 2:
            return "Unknown"
        
        # Simple heuristic: check growth rate
        valid_timings = [t for t in timings if t.get("time") is not None]
        
        if len(valid_timings) < 2:
            return "Unknown"
        
        # Calculate growth ratio
        first = valid_timings[0]
        last = valid_timings[-1]
        
        if first["time"] == 0:
            return "O(1) or very efficient"
        
        time_ratio = last["time"] / first["time"]
        size_ratio = last["size"] / first["size"]
        
        if time_ratio < size_ratio * 0.5:
            return "Better than O(n)"
        elif time_ratio < size_ratio * 1.5:
            return "~O(n)"
        elif time_ratio < size_ratio * size_ratio * 0.5:
            return "~O(n log n)"
        else:
            return "O(n²) or worse"


class PerformanceMonitor:
    """Monitor and track computational performance in real-time"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.alerts = []
    
    def track_metric(self, metric_name: str, value: float):
        """Track a performance metric"""
        self.metrics[metric_name].append({
            "value": value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Check for performance degradation
        if len(self.metrics[metric_name]) > 10:
            recent_avg = sum(m["value"] for m in self.metrics[metric_name][-10:]) / 10
            overall_avg = sum(m["value"] for m in self.metrics[metric_name]) / len(self.metrics[metric_name])
            
            if recent_avg > overall_avg * 1.5:
                self.alerts.append({
                    "type": "performance_degradation",
                    "metric": metric_name,
                    "recent_avg": recent_avg,
                    "overall_avg": overall_avg,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of all tracked performance metrics"""
        summary = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                metric_values = [v["value"] for v in values]
                summary[metric_name] = {
                    "count": len(metric_values),
                    "average": sum(metric_values) / len(metric_values),
                    "min": min(metric_values),
                    "max": max(metric_values),
                    "latest": metric_values[-1]
                }
        
        return {
            "metrics": summary,
            "alerts": self.alerts,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# Global instances
algorithmic_optimizer = AlgorithmicOptimizer()
performance_monitor = PerformanceMonitor()


def optimize_algorithm(name: str, complexity: str = "O(n)"):
    """
    Decorator to register and optimize an algorithm
    
    Usage:
        @optimize_algorithm("my_algorithm", "O(n log n)")
        def my_function(data):
            # algorithm implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        algorithmic_optimizer.register_algorithm(name, func, complexity)
        return algorithmic_optimizer.optimize_execution(name)(func)
    return decorator
