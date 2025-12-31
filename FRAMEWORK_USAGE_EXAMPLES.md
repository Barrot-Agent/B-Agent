# Barrot Enhanced Framework - Usage Examples

This document provides practical examples demonstrating how to use the enhanced Barrot AI agent framework.

---

## Example 1: Basic ReAct Reasoning for Research Task

```python
"""
Example: Using ReAct reasoning to research and analyze AI frameworks
"""

from Barrot_Agent.reasoning_engine import ReActReasoner
from Barrot_Agent.memory_system import MemoryManager

# Initialize components
reasoner = ReActReasoner()
memory = MemoryManager()

# Define thought generator
def research_thought_generator(context, traces):
    """Generate research-oriented thoughts"""
    if len(traces) == 0:
        return "I need to identify key AI agent frameworks to analyze"
    elif len(traces) == 1:
        return "I should focus on frameworks with advanced reasoning capabilities"
    elif len(traces) == 2:
        return "Let me compare their architectures and algorithms"
    else:
        return "I should synthesize findings and identify beneficial patterns"

# Define action executor
def research_action_executor(thought):
    """Execute research actions"""
    if "identify" in thought.lower():
        frameworks = ["LangChain", "CrewAI", "AutoGPT", "SuperAGI"]
        return ("research", f"Identified frameworks: {frameworks}")
    elif "focus" in thought.lower():
        return ("analyze", "ReAct, ToT, and Reflexion patterns identified")
    elif "compare" in thought.lower():
        return ("compare", "LangChain: modular chains, CrewAI: role-based agents")
    elif "synthesize" in thought.lower():
        return ("complete", "Findings: ReAct reduces hallucination, ToT enables exploration")
    return ("continue", "Processing...")

# Define termination checker
def research_termination_checker(action, observation):
    """Check if research is complete"""
    return action == "complete"

# Execute reasoning
result = reasoner.reason_and_act(
    task="Research AI agent frameworks and identify beneficial patterns",
    thought_generator=research_thought_generator,
    action_executor=research_action_executor,
    termination_checker=research_termination_checker
)

# Store findings in memory
if result.get("success"):
    memory.store_experience(
        event_type="research_task",
        description="AI framework research",
        context={"frameworks_analyzed": 4, "patterns_identified": ["ReAct", "ToT"]},
        outcome=result.get("result"),
        importance=0.9,
        tags=["research", "frameworks", "patterns"]
    )
    
    # Store key learnings as semantic knowledge
    memory.semantic.learn(
        concept="beneficial_framework_patterns",
        knowledge="ReAct pattern reduces hallucination through grounded reasoning. ToT enables multi-path exploration.",
        category="research_findings",
        confidence=0.9
    )

print(f"Research {'completed' if result['success'] else 'incomplete'}")
print(f"Result: {result.get('result')}")
print(f"Iterations: {result.get('iterations')}")
```

---

## Example 2: Tree-of-Thoughts for Problem Solving

```python
"""
Example: Using Tree-of-Thoughts to explore multiple solution approaches
"""

from Barrot_Agent.reasoning_engine import TreeOfThoughtsExplorer

explorer = TreeOfThoughtsExplorer(max_depth=3, branch_factor=3)

# Define thought generator for different solution branches
def solution_thought_generator(context, depth):
    """Generate multiple solution approaches"""
    if depth == 0:
        return [
            "Approach 1: Modular architecture with clear separation",
            "Approach 2: Integrated system with shared components",
            "Approach 3: Hybrid approach combining both"
        ]
    elif depth == 1:
        if "modular" in context.lower():
            return [
                "Use plugin system for extensibility",
                "Implement event-driven communication",
                "Create standardized interfaces"
            ]
        elif "integrated" in context.lower():
            return [
                "Centralized state management",
                "Shared memory pools",
                "Unified execution engine"
            ]
        else:  # hybrid
            return [
                "Core integrated, plugins modular",
                "Shared memory, isolated execution",
                "Unified API, flexible implementation"
            ]
    else:
        return [
            f"Refine: {context}",
            f"Optimize: {context}",
            f"Validate: {context}"
        ]

# Define evaluator to score approaches
def solution_evaluator(task, thought):
    """Evaluate quality of solution approach"""
    score = 0.5  # Base score
    
    # Favor modular approaches
    if "modular" in thought.lower():
        score += 0.2
    
    # Favor extensibility
    if "plugin" in thought.lower() or "extensibility" in thought.lower():
        score += 0.15
    
    # Favor proven patterns
    if "event-driven" in thought.lower() or "api" in thought.lower():
        score += 0.1
    
    # Favor validation
    if "validate" in thought.lower():
        score += 0.05
    
    return min(score, 1.0)

# Define solution checker
def solution_checker(thought):
    """Check if thought represents a complete solution"""
    if "validate" in thought.lower():
        return (True, thought)
    return (False, None)

# Explore solution space
result = explorer.explore(
    task="Design architecture for enhanced agent framework",
    thought_generator=solution_thought_generator,
    evaluator=solution_evaluator,
    solution_checker=solution_checker
)

print(f"Exploration {'successful' if result['success'] else 'incomplete'}")
print(f"Best solution: {result.get('solution')}")
print(f"Solution score: {result.get('best_score'):.2f}")
print(f"Nodes explored: {result.get('nodes_explored')}")
```

---

## Example 3: Multi-Agent Collaborative Workflow

```python
"""
Example: Coordinating multiple specialized agents for framework enhancement
"""

from Barrot_Agent.orchestrator import AgentCoordinator, AgentRole

# Initialize orchestrator
orchestrator = AgentCoordinator()

# Register specialized agents
print("Registering agents...")

# Researcher agent
orchestrator.register_agent(
    agent_id="researcher_alpha",
    role=AgentRole.RESEARCHER,
    capabilities=["literature_review", "framework_analysis", "documentation"]
)

# Analyst agent
orchestrator.register_agent(
    agent_id="analyst_beta",
    role=AgentRole.ANALYST,
    capabilities=["pattern_recognition", "comparison", "evaluation"]
)

# Developer agent
orchestrator.register_agent(
    agent_id="developer_gamma",
    role=AgentRole.DEVELOPER,
    capabilities=["architecture_design", "coding", "testing"]
)

# Evaluator agent
orchestrator.register_agent(
    agent_id="evaluator_delta",
    role=AgentRole.EVALUATOR,
    capabilities=["code_review", "quality_assessment", "optimization"]
)

# Define enhancement workflow
workflow = {
    "name": "framework_enhancement_pipeline",
    "steps": [
        {
            "name": "phase_1_research",
            "tasks": [
                {
                    "description": "Research LangChain framework architecture",
                    "capabilities": ["literature_review", "framework_analysis"],
                    "priority": 5
                },
                {
                    "description": "Research CrewAI multi-agent coordination",
                    "capabilities": ["literature_review", "framework_analysis"],
                    "priority": 5
                }
            ]
        },
        {
            "name": "phase_2_analysis",
            "tasks": [
                {
                    "description": "Compare framework architectures and identify patterns",
                    "capabilities": ["pattern_recognition", "comparison"],
                    "priority": 4
                },
                {
                    "description": "Evaluate adaptability of identified patterns",
                    "capabilities": ["evaluation"],
                    "priority": 4
                }
            ]
        },
        {
            "name": "phase_3_development",
            "tasks": [
                {
                    "description": "Design enhanced reasoning engine architecture",
                    "capabilities": ["architecture_design"],
                    "priority": 5
                },
                {
                    "description": "Implement ReAct reasoning module",
                    "capabilities": ["coding"],
                    "priority": 5
                },
                {
                    "description": "Implement Tree-of-Thoughts explorer",
                    "capabilities": ["coding"],
                    "priority": 4
                },
                {
                    "description": "Implement memory system",
                    "capabilities": ["coding"],
                    "priority": 5
                }
            ]
        },
        {
            "name": "phase_4_evaluation",
            "tasks": [
                {
                    "description": "Review code quality and architecture",
                    "capabilities": ["code_review", "quality_assessment"],
                    "priority": 4
                },
                {
                    "description": "Identify optimization opportunities",
                    "capabilities": ["optimization"],
                    "priority": 3
                }
            ]
        }
    ]
}

# Execute workflow
print(f"\nExecuting workflow: {workflow['name']}")
result = orchestrator.execute_collaborative_workflow(
    workflow_name=workflow["name"],
    workflow_steps=workflow["steps"]
)

# Display results
print("\nWorkflow Execution Results:")
for phase, phase_results in result.items():
    print(f"\n{phase}:")
    for task_result in phase_results:
        print(f"  - Task {task_result['task_id']}: {task_result['status']}")
        print(f"    Assigned to: {task_result['agent']}")

# Check final status
status = orchestrator.get_orchestration_status()
print(f"\nFinal Status:")
print(f"  Total agents: {status['agents']['total']}")
print(f"  Busy agents: {status['agents']['busy']}")
print(f"  Completed tasks: {status['tasks']['completed']}")
```

---

## Example 4: Integrated System with Memory and Tools

```python
"""
Example: Complete integrated system combining all components
"""

from Barrot_Agent.reasoning_engine import ReasoningEngine, ReasoningStrategy
from Barrot_Agent.memory_system import MemoryManager
from Barrot_Agent.tool_manager import ToolManager, ToolCategory, ToolParameter
from Barrot_Agent.orchestrator import AgentCoordinator, AgentRole

# Initialize all components
print("Initializing Barrot Enhanced Framework...")
reasoning_engine = ReasoningEngine()
memory_manager = MemoryManager()
tool_manager = ToolManager()
orchestrator = AgentCoordinator()

# Register custom tools
print("\nRegistering tools...")

def analyze_framework(framework_name: str) -> dict:
    """Analyze a framework and return key features"""
    frameworks = {
        "LangChain": {
            "features": ["modular_chains", "tool_integration", "memory_systems"],
            "strength": "flexibility"
        },
        "CrewAI": {
            "features": ["role_based_agents", "collaboration", "task_delegation"],
            "strength": "multi_agent_coordination"
        }
    }
    return frameworks.get(framework_name, {})

tool_manager.registry.register_tool(
    name="framework_analyzer",
    description="Analyze AI framework features",
    category=ToolCategory.ANALYSIS,
    parameters=[
        ToolParameter("framework_name", "str", "Name of framework to analyze", True)
    ],
    returns="dict",
    executor=analyze_framework,
    safety_level=1
)

# Register agents
print("\nRegistering agents...")
orchestrator.register_agent(
    "main_coordinator",
    AgentRole.COORDINATOR,
    ["planning", "coordination", "decision_making"]
)

# Example task: Analyze frameworks and store findings
print("\nExecuting integrated task...")

# Step 1: Use tool to gather data
success, langchain_data, error = tool_manager.executor.execute(
    list(tool_manager.registry.tools.keys())[0],  # Get first tool ID
    {"framework_name": "LangChain"}
)

if success:
    print(f"LangChain analysis: {langchain_data}")
    
    # Step 2: Store in memory
    memory_manager.semantic.learn(
        concept="LangChain_framework",
        knowledge=f"Features: {langchain_data.get('features')}. Strength: {langchain_data.get('strength')}",
        category="framework_knowledge",
        confidence=0.9
    )
    
    # Step 3: Store experience
    memory_manager.episodic.remember(
        event_type="framework_analysis",
        description="Analyzed LangChain framework using tool",
        context={"tool_used": "framework_analyzer", "framework": "LangChain"},
        outcome="Successfully identified key features and strengths",
        importance=0.8,
        tags=["analysis", "langchain", "tools"]
    )

# Step 4: Use reasoning to synthesize
print("\nSynthesizing findings...")

# Get relevant context from memory
context = memory_manager.get_relevant_context("framework patterns")
print(f"\nRelevant context from memory:\n{context[:300]}...")

# Step 5: Create task for agent
task, agent = orchestrator.create_and_delegate_task(
    description="Synthesize framework analysis findings into recommendations",
    required_capabilities=["decision_making"],
    priority=5
)

if agent:
    print(f"\nTask delegated to: {agent.agent_id}")
    
    # Simulate task completion
    orchestrator.task_delegator.complete_task(
        task.task_id,
        result="Recommendation: Adopt ReAct pattern from LangChain, multi-agent coordination from CrewAI",
        success=True
    )
    
    # Store final outcome
    memory_manager.store_experience(
        event_type="synthesis_task",
        description="Synthesized framework findings",
        context={
            "frameworks_analyzed": 1,
            "tools_used": 1,
            "agents_involved": 1
        },
        outcome="Generated actionable recommendations",
        extract_knowledge=True
    )

print("\n✅ Integrated task completed successfully!")
print(f"Total experiences stored: {len(memory_manager.episodic.entries)}")
print(f"Knowledge concepts stored: {len(memory_manager.semantic.knowledge_base)}")
```

---

## Example 5: Adaptive Strategy Selection

```python
"""
Example: Automatically selecting the best reasoning strategy for different tasks
"""

from Barrot_Agent.reasoning_engine import ReasoningEngine, ReasoningStrategy
from Barrot_Agent.memory_system import MemoryManager

engine = ReasoningEngine()
memory = MemoryManager()

def select_optimal_strategy(task_description: str, context: dict = None) -> ReasoningStrategy:
    """
    Intelligently select reasoning strategy based on task characteristics
    """
    task_lower = task_description.lower()
    
    # Tree-of-Thoughts for exploration tasks
    if any(keyword in task_lower for keyword in ["explore", "alternatives", "options", "multiple"]):
        return ReasoningStrategy.TREE_OF_THOUGHTS
    
    # ReAct for tasks requiring external actions/tools
    if any(keyword in task_lower for keyword in ["research", "find", "search", "execute", "tool"]):
        return ReasoningStrategy.REACT
    
    # Chain-of-Thought for step-by-step reasoning
    if any(keyword in task_lower for keyword in ["explain", "step", "process", "why", "how"]):
        return ReasoningStrategy.CHAIN_OF_THOUGHT
    
    # Self-Reflection for improvement tasks
    if any(keyword in task_lower for keyword in ["improve", "evaluate", "review", "optimize"]):
        return ReasoningStrategy.SELF_REFLECTION
    
    # Default to ReAct
    return ReasoningStrategy.REACT

# Example tasks with adaptive strategy selection
tasks = [
    "Explore different approaches to implement memory consolidation",
    "Research the latest developments in AI agent frameworks",
    "Explain step-by-step how ReAct reasoning works",
    "Review and improve the current implementation"
]

for task in tasks:
    strategy = select_optimal_strategy(task)
    print(f"\nTask: {task}")
    print(f"Selected strategy: {strategy.value}")
    
    # Execute with selected strategy
    result = engine.reason(task=task, strategy=strategy)
    
    # Learn from the outcome
    if result.get("success"):
        memory.semantic.learn(
            concept=f"task_strategy_mapping_{strategy.value}",
            knowledge=f"Strategy {strategy.value} effective for: {task}",
            category="strategy_patterns",
            confidence=0.8
        )

# After learning, query memory for patterns
print("\n\nLearned strategy patterns:")
patterns = memory.semantic.search("strategy", category="strategy_patterns")
for pattern in patterns:
    print(f"  - {pattern['concept']}: {pattern['knowledge']}")
```

---

## Example 6: Self-Reflection and Continuous Improvement

```python
"""
Example: Using self-reflection to learn from task execution and improve
"""

from Barrot_Agent.reasoning_engine import SelfReflectionEvaluator, ReasoningTrace
from Barrot_Agent.memory_system import MemoryManager

evaluator = SelfReflectionEvaluator()
memory = MemoryManager()

# Simulate a task execution with traces
task = "Implement new reasoning module"

execution_trace = [
    ReasoningTrace(
        timestamp="2025-12-31T10:00:00",
        strategy="react",
        thought="I should start by researching existing patterns",
        action="research",
        observation="Found ReAct and ToT patterns"
    ),
    ReasoningTrace(
        timestamp="2025-12-31T10:05:00",
        strategy="react",
        thought="I'll implement ReAct first as it's foundational",
        action="implement",
        observation="ReAct module created successfully"
    ),
    ReasoningTrace(
        timestamp="2025-12-31T10:15:00",
        strategy="react",
        thought="Need to add error handling",
        action="enhance",
        observation="Added try-except blocks"
    )
]

outcome = "Successfully implemented ReAct reasoning module with error handling"
success = True

# Define reflection generator
def generate_reflection(task, traces, outcome, success):
    """Generate reflection insights"""
    return {
        "insights": [
            "Research phase was valuable for understanding patterns",
            "Incremental implementation approach worked well",
            "Error handling added robustness"
        ],
        "mistakes": [
            "Could have planned testing strategy earlier"
        ],
        "improvements": [
            "Create comprehensive test suite from the start",
            "Document design decisions during implementation",
            "Consider edge cases before coding"
        ],
        "learned_patterns": [
            "Research → Implement → Enhance is effective pattern",
            "Error handling should be concurrent with implementation"
        ]
    }

# Perform reflection
reflection = evaluator.reflect_on_execution(
    task=task,
    execution_trace=execution_trace,
    outcome=outcome,
    success=success,
    reflection_generator=generate_reflection
)

print("Self-Reflection Results:")
print(f"\nTask: {reflection['task']}")
print(f"Success: {reflection['success']}")
print(f"Steps taken: {reflection['steps_taken']}")

print("\nInsights:")
for insight in reflection['insights']:
    print(f"  ✓ {insight}")

print("\nMistakes identified:")
for mistake in reflection['mistakes']:
    print(f"  ✗ {mistake}")

print("\nImprovements for next time:")
for improvement in reflection['improvements']:
    print(f"  → {improvement}")

print("\nLearned patterns:")
for pattern in reflection['learned_patterns']:
    print(f"  📚 {pattern}")
    
    # Store learned patterns in semantic memory
    memory.semantic.learn(
        concept=f"learned_pattern_{hash(pattern)}",
        knowledge=pattern,
        category="execution_patterns",
        confidence=0.8,
        source="self_reflection"
    )

# Next time this agent works on similar task, retrieve relevant reflections
print("\n\nRetrieving relevant past reflections for similar task...")
similar_task = "Implement memory system module"
relevant_reflections = evaluator.get_relevant_reflections(similar_task, top_k=3)

if relevant_reflections:
    print(f"Found {len(relevant_reflections)} relevant past reflections:")
    for ref in relevant_reflections:
        print(f"\n  Previous task: {ref['task']}")
        print(f"  Key improvement: {ref['improvements'][0] if ref['improvements'] else 'N/A'}")
```

---

## Running the Examples

To run these examples:

1. Ensure the Barrot-Agent framework is properly installed
2. Create the necessary directory structure:
   ```bash
   mkdir -p memory-bundles
   ```

3. Run any example:
   ```bash
   python example1_react_research.py
   ```

4. Check generated logs in `memory-bundles/` directory

---

## Next Steps

- Experiment with different parameter configurations
- Combine strategies for complex workflows
- Create custom tools for your specific domain
- Build domain-specific agents with specialized capabilities
- Integrate with external APIs and services

For more details, see:
- `FRAMEWORK_INTEGRATION_GUIDE.md` - Complete integration documentation
- `FRAMEWORK_ENHANCEMENT_ANALYSIS.md` - Design rationale and architecture
- Module docstrings - Inline API documentation
