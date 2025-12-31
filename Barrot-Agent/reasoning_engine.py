"""
Barrot Enhanced Reasoning Engine

Implements advanced reasoning strategies including:
- ReAct (Reasoning + Acting)
- Tree-of-Thoughts (ToT)
- Self-Reflection
- Enhanced Chain-of-Thought

Adapted from analysis of LangChain, CrewAI, AutoGPT, and latest AI research.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, field


class ReasoningStrategy(Enum):
    """Available reasoning strategies"""
    REACT = "react"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    SELF_REFLECTION = "self_reflection"


@dataclass
class ReasoningTrace:
    """Record of a reasoning step"""
    timestamp: str
    strategy: str
    thought: str
    action: Optional[str] = None
    observation: Optional[str] = None
    evaluation: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThoughtNode:
    """Node in Tree-of-Thoughts exploration"""
    thought: str
    depth: int
    parent: Optional['ThoughtNode'] = None
    children: List['ThoughtNode'] = field(default_factory=list)
    evaluation_score: float = 0.0
    is_terminal: bool = False
    solution: Optional[str] = None


class ReActReasoner:
    """
    ReAct: Reasoning + Acting framework
    
    Implements the thought-action-observation cycle for grounded reasoning
    that integrates with external tools and reduces hallucination.
    
    Based on the ReAct paper and implementations in LangChain/CrewAI.
    """
    
    def __init__(self, max_iterations: int = 10, trace_log_path: str = "memory-bundles/reasoning-traces.json"):
        self.max_iterations = max_iterations
        self.trace_log_path = trace_log_path
        self.traces: List[ReasoningTrace] = []
    
    def reason_and_act(
        self,
        task: str,
        thought_generator: Callable[[str, List[ReasoningTrace]], str],
        action_executor: Callable[[str], Tuple[str, str]],
        termination_checker: Callable[[str, str], bool]
    ) -> Dict[str, Any]:
        """
        Execute ReAct reasoning loop
        
        Args:
            task: The task to accomplish
            thought_generator: Function that generates next thought given task and history
            action_executor: Function that executes action and returns (action, observation)
            termination_checker: Function that determines if task is complete
            
        Returns:
            Dictionary with result, traces, and metadata
        """
        iteration = 0
        context = f"Task: {task}"
        
        while iteration < self.max_iterations:
            # Reasoning step
            thought = thought_generator(context, self.traces)
            
            # Acting step
            action, observation = action_executor(thought)
            
            # Record trace
            trace = ReasoningTrace(
                timestamp=datetime.utcnow().isoformat(),
                strategy="react",
                thought=thought,
                action=action,
                observation=observation,
                metadata={"iteration": iteration}
            )
            self.traces.append(trace)
            
            # Check termination
            if termination_checker(action, observation):
                self._save_traces()
                return {
                    "success": True,
                    "result": observation,
                    "iterations": iteration + 1,
                    "traces": self.traces
                }
            
            # Update context for next iteration
            context = f"{context}\nThought: {thought}\nAction: {action}\nObservation: {observation}"
            iteration += 1
        
        self._save_traces()
        return {
            "success": False,
            "result": "Max iterations reached",
            "iterations": iteration,
            "traces": self.traces
        }
    
    def _save_traces(self):
        """Save reasoning traces to log file"""
        try:
            with open(self.trace_log_path, 'a') as f:
                for trace in self.traces:
                    f.write(json.dumps({
                        "timestamp": trace.timestamp,
                        "strategy": trace.strategy,
                        "thought": trace.thought,
                        "action": trace.action,
                        "observation": trace.observation,
                        "metadata": trace.metadata
                    }) + "\n")
        except Exception as e:
            print(f"Warning: Could not save reasoning traces: {e}")


class TreeOfThoughtsExplorer:
    """
    Tree-of-Thoughts reasoning framework
    
    Explores multiple reasoning paths simultaneously, evaluates alternatives,
    and can backtrack from suboptimal paths.
    
    Inspired by ToT paper and implementations in modern agent frameworks.
    """
    
    def __init__(self, max_depth: int = 5, branch_factor: int = 3, trace_log_path: str = "memory-bundles/tot-traces.json"):
        self.max_depth = max_depth
        self.branch_factor = branch_factor
        self.trace_log_path = trace_log_path
        self.exploration_log: List[Dict] = []
    
    def explore(
        self,
        task: str,
        thought_generator: Callable[[str, int], List[str]],
        evaluator: Callable[[str, str], float],
        solution_checker: Callable[[str], Tuple[bool, Optional[str]]]
    ) -> Dict[str, Any]:
        """
        Explore multiple reasoning paths
        
        Args:
            task: The task to solve
            thought_generator: Generates multiple thoughts for given context and depth
            evaluator: Evaluates quality of a thought (0.0-1.0)
            solution_checker: Checks if thought leads to solution
            
        Returns:
            Best solution found with exploration metadata
        """
        root = ThoughtNode(thought=f"Task: {task}", depth=0)
        best_solution = None
        best_score = -1.0
        
        # BFS exploration
        queue = [root]
        nodes_explored = 0
        
        while queue and nodes_explored < 100:  # Safety limit
            node = queue.pop(0)
            nodes_explored += 1
            
            # Check if current node is a solution
            is_solution, solution = solution_checker(node.thought)
            if is_solution and solution:
                node.is_terminal = True
                node.solution = solution
                score = evaluator(task, solution)
                node.evaluation_score = score
                
                if score > best_score:
                    best_score = score
                    best_solution = solution
                
                self._log_exploration(node, "SOLUTION_FOUND")
                continue
            
            # Expand node if not at max depth
            if node.depth < self.max_depth:
                children_thoughts = thought_generator(node.thought, node.depth + 1)
                
                for thought in children_thoughts[:self.branch_factor]:
                    child = ThoughtNode(
                        thought=thought,
                        depth=node.depth + 1,
                        parent=node
                    )
                    child.evaluation_score = evaluator(task, thought)
                    node.children.append(child)
                    queue.append(child)
                    
                    self._log_exploration(child, "EXPANDED")
                
                # Sort queue by evaluation score (best-first)
                queue.sort(key=lambda n: n.evaluation_score, reverse=True)
        
        self._save_exploration_log()
        
        return {
            "success": best_solution is not None,
            "solution": best_solution,
            "best_score": best_score,
            "nodes_explored": nodes_explored,
            "exploration_log": self.exploration_log
        }
    
    def _log_exploration(self, node: ThoughtNode, event: str):
        """Log exploration event"""
        self.exploration_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "depth": node.depth,
            "thought": node.thought,
            "score": node.evaluation_score,
            "is_terminal": node.is_terminal
        })
    
    def _save_exploration_log(self):
        """Save exploration log to file"""
        try:
            with open(self.trace_log_path, 'w') as f:
                json.dump(self.exploration_log, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save ToT exploration log: {e}")


class SelfReflectionEvaluator:
    """
    Self-Reflection framework for agent improvement
    
    Implements evaluation and self-critique mechanisms that allow
    the agent to learn from past executions and improve over time.
    
    Based on Reflexion and similar self-improvement frameworks.
    """
    
    def __init__(self, reflection_log_path: str = "memory-bundles/self-reflections.json"):
        self.reflection_log_path = reflection_log_path
        self.reflections: List[Dict] = []
    
    def reflect_on_execution(
        self,
        task: str,
        execution_trace: List[ReasoningTrace],
        outcome: str,
        success: bool,
        reflection_generator: Callable[[str, List[ReasoningTrace], str, bool], Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform self-reflection on task execution
        
        Args:
            task: Original task
            execution_trace: Sequence of reasoning steps
            outcome: Final outcome
            success: Whether task succeeded
            reflection_generator: Function to generate reflection insights
            
        Returns:
            Reflection with insights and improvement suggestions
        """
        reflection = reflection_generator(task, execution_trace, outcome, success)
        
        reflection_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "task": task,
            "success": success,
            "steps_taken": len(execution_trace),
            "insights": reflection.get("insights", []),
            "mistakes": reflection.get("mistakes", []),
            "improvements": reflection.get("improvements", []),
            "learned_patterns": reflection.get("learned_patterns", [])
        }
        
        self.reflections.append(reflection_record)
        self._save_reflections()
        
        return reflection_record
    
    def get_relevant_reflections(self, task: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant past reflections for a new task
        
        Simple keyword-based matching for now; can be enhanced with embeddings
        """
        # Simple keyword overlap scoring
        task_keywords = set(task.lower().split())
        
        scored_reflections = []
        for reflection in self.reflections:
            reflection_keywords = set(reflection['task'].lower().split())
            overlap = len(task_keywords & reflection_keywords)
            if overlap > 0:
                scored_reflections.append((overlap, reflection))
        
        scored_reflections.sort(reverse=True, key=lambda x: x[0])
        return [r[1] for r in scored_reflections[:top_k]]
    
    def _save_reflections(self):
        """Save reflections to file"""
        try:
            with open(self.reflection_log_path, 'w') as f:
                json.dump(self.reflections, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save reflections: {e}")


class ChainOfThoughtProcessor:
    """
    Enhanced Chain-of-Thought reasoning
    
    Provides structured step-by-step reasoning with improved tracking
    and integration with other reasoning strategies.
    """
    
    def __init__(self, trace_log_path: str = "memory-bundles/cot-traces.json"):
        self.trace_log_path = trace_log_path
        self.reasoning_steps: List[Dict] = []
    
    def process_with_cot(
        self,
        task: str,
        step_generator: Callable[[str, List[str]], str],
        max_steps: int = 10
    ) -> Dict[str, Any]:
        """
        Process task with chain-of-thought reasoning
        
        Args:
            task: Task to solve
            step_generator: Function that generates next reasoning step
            max_steps: Maximum reasoning steps
            
        Returns:
            Result with reasoning chain
        """
        context = task
        reasoning_chain = []
        
        for step_num in range(max_steps):
            step = step_generator(context, reasoning_chain)
            
            reasoning_step = {
                "step_number": step_num + 1,
                "timestamp": datetime.utcnow().isoformat(),
                "thought": step,
                "context_length": len(context)
            }
            
            reasoning_chain.append(step)
            self.reasoning_steps.append(reasoning_step)
            
            # Check if reasoning is complete
            if "therefore" in step.lower() or "conclusion" in step.lower():
                break
            
            context = f"{context}\n{step}"
        
        self._save_steps()
        
        return {
            "reasoning_chain": reasoning_chain,
            "steps_taken": len(reasoning_chain),
            "final_thought": reasoning_chain[-1] if reasoning_chain else None
        }
    
    def _save_steps(self):
        """Save reasoning steps to file"""
        try:
            with open(self.trace_log_path, 'w') as f:
                json.dump(self.reasoning_steps, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save CoT steps: {e}")


class ReasoningEngine:
    """
    Unified reasoning engine for Barrot
    
    Orchestrates different reasoning strategies and provides a unified
    interface for complex reasoning tasks.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.react = ReActReasoner()
        self.tot = TreeOfThoughtsExplorer()
        self.reflector = SelfReflectionEvaluator()
        self.cot = ChainOfThoughtProcessor()
    
    def reason(
        self,
        task: str,
        strategy: ReasoningStrategy = ReasoningStrategy.REACT,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute reasoning with specified strategy
        
        Args:
            task: Task to reason about
            strategy: Reasoning strategy to use
            **kwargs: Strategy-specific parameters
            
        Returns:
            Reasoning result
        """
        timestamp = datetime.utcnow().isoformat()
        
        result = {
            "task": task,
            "strategy": strategy.value,
            "timestamp": timestamp,
            "success": False
        }
        
        if strategy == ReasoningStrategy.REACT:
            result.update(self._execute_react(task, **kwargs))
        elif strategy == ReasoningStrategy.TREE_OF_THOUGHTS:
            result.update(self._execute_tot(task, **kwargs))
        elif strategy == ReasoningStrategy.CHAIN_OF_THOUGHT:
            result.update(self._execute_cot(task, **kwargs))
        elif strategy == ReasoningStrategy.SELF_REFLECTION:
            result.update(self._execute_reflection(task, **kwargs))
        
        return result
    
    def _execute_react(self, task: str, **kwargs) -> Dict:
        """Execute ReAct strategy"""
        # Default implementations for required callbacks
        def default_thought_generator(context, traces):
            return f"Analyzing: {context}"
        
        def default_action_executor(thought):
            return ("think", thought)
        
        def default_termination_checker(action, observation):
            return action == "complete"
        
        return self.react.reason_and_act(
            task,
            kwargs.get('thought_generator', default_thought_generator),
            kwargs.get('action_executor', default_action_executor),
            kwargs.get('termination_checker', default_termination_checker)
        )
    
    def _execute_tot(self, task: str, **kwargs) -> Dict:
        """Execute Tree-of-Thoughts strategy"""
        def default_thought_generator(context, depth):
            return [f"Branch {i} at depth {depth}: {context}" for i in range(3)]
        
        def default_evaluator(task, thought):
            return 0.5  # Neutral score
        
        def default_solution_checker(thought):
            return (False, None)
        
        return self.tot.explore(
            task,
            kwargs.get('thought_generator', default_thought_generator),
            kwargs.get('evaluator', default_evaluator),
            kwargs.get('solution_checker', default_solution_checker)
        )
    
    def _execute_cot(self, task: str, **kwargs) -> Dict:
        """Execute Chain-of-Thought strategy"""
        def default_step_generator(context, chain):
            return f"Step {len(chain) + 1}: Processing {context}"
        
        return self.cot.process_with_cot(
            task,
            kwargs.get('step_generator', default_step_generator),
            kwargs.get('max_steps', 10)
        )
    
    def _execute_reflection(self, task: str, **kwargs) -> Dict:
        """Execute Self-Reflection"""
        def default_reflection_generator(task, trace, outcome, success):
            return {
                "insights": ["Reflection generated"],
                "mistakes": [],
                "improvements": [],
                "learned_patterns": []
            }
        
        execution_trace = kwargs.get('execution_trace', [])
        outcome = kwargs.get('outcome', 'unknown')
        success = kwargs.get('success', False)
        
        return self.reflector.reflect_on_execution(
            task,
            execution_trace,
            outcome,
            success,
            kwargs.get('reflection_generator', default_reflection_generator)
        )


# Example usage and testing
if __name__ == "__main__":
    print("Barrot Enhanced Reasoning Engine")
    print("=" * 50)
    
    engine = ReasoningEngine()
    
    # Test ReAct reasoning
    print("\n1. Testing ReAct Reasoning:")
    result = engine.reason(
        task="Analyze AI agent frameworks",
        strategy=ReasoningStrategy.REACT
    )
    print(f"Success: {result.get('success')}")
    print(f"Iterations: {result.get('iterations', 0)}")
    
    # Test Chain-of-Thought
    print("\n2. Testing Chain-of-Thought:")
    result = engine.reason(
        task="Compare LangChain and CrewAI",
        strategy=ReasoningStrategy.CHAIN_OF_THOUGHT
    )
    print(f"Steps taken: {result.get('steps_taken', 0)}")
    
    print("\n" + "=" * 50)
    print("Reasoning engine initialized successfully!")
