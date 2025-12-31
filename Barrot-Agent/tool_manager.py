"""
Barrot Tool Management System

Implements Toolformer-inspired tool selection and execution
with safety constraints and intelligent tool orchestration.

Features:
- Dynamic tool discovery and registration
- Context-aware tool selection
- Safe tool execution with error handling
- Result caching and interpretation
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum


class ToolCategory(Enum):
    """Tool categories"""
    DATA_PROCESSING = "data_processing"
    WEB_INTERACTION = "web_interaction"
    FILE_OPERATION = "file_operation"
    API_CALL = "api_call"
    COMPUTATION = "computation"
    ANALYSIS = "analysis"
    COMMUNICATION = "communication"
    SYSTEM = "system"


@dataclass
class ToolParameter:
    """Tool parameter definition"""
    name: str
    type: str  # python type name
    description: str
    required: bool = True
    default: Any = None


@dataclass
class Tool:
    """Tool definition"""
    tool_id: str
    name: str
    description: str
    category: ToolCategory
    parameters: List[ToolParameter]
    returns: str  # Return type description
    executor: Optional[Callable] = None  # Actual execution function
    safety_level: int = 1  # 1=safe, 2=requires review, 3=dangerous
    usage_count: int = 0
    success_rate: float = 1.0
    average_duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolExecution:
    """Tool execution record"""
    execution_id: str
    tool_id: str
    parameters: Dict[str, Any]
    timestamp: str
    duration: float
    success: bool
    result: Any = None
    error: Optional[str] = None


class ToolRegistry:
    """
    Central registry for all available tools
    """
    
    def __init__(self, registry_path: str = "memory-bundles/tool-registry.json"):
        self.registry_path = registry_path
        self.tools: Dict[str, Tool] = {}
        self.category_index: Dict[ToolCategory, List[str]] = {}
        self._load_registry()
    
    def register_tool(
        self,
        name: str,
        description: str,
        category: ToolCategory,
        parameters: List[ToolParameter],
        returns: str,
        executor: Callable,
        safety_level: int = 1
    ) -> Tool:
        """
        Register a new tool
        
        Args:
            name: Tool name
            description: Tool description
            category: Tool category
            parameters: List of parameters
            returns: Return type description
            executor: Execution function
            safety_level: Safety level (1-3)
            
        Returns:
            Registered tool
        """
        tool_id = f"{category.value}_{name}_{int(datetime.utcnow().timestamp())}"
        
        tool = Tool(
            tool_id=tool_id,
            name=name,
            description=description,
            category=category,
            parameters=parameters,
            returns=returns,
            executor=executor,
            safety_level=safety_level
        )
        
        self.tools[tool_id] = tool
        
        # Update category index
        if category not in self.category_index:
            self.category_index[category] = []
        self.category_index[category].append(tool_id)
        
        self._save_registry()
        return tool
    
    def get_tool(self, tool_id: str) -> Optional[Tool]:
        """Get tool by ID"""
        return self.tools.get(tool_id)
    
    def search_tools(
        self,
        query: str,
        category: Optional[ToolCategory] = None,
        max_safety_level: int = 3
    ) -> List[Tool]:
        """
        Search for tools
        
        Args:
            query: Search query
            category: Filter by category
            max_safety_level: Maximum safety level
            
        Returns:
            List of matching tools
        """
        query_lower = query.lower()
        results = []
        
        for tool in self.tools.values():
            # Filter by category
            if category and tool.category != category:
                continue
            
            # Filter by safety level
            if tool.safety_level > max_safety_level:
                continue
            
            # Check query match
            if (query_lower in tool.name.lower() or
                query_lower in tool.description.lower()):
                results.append(tool)
        
        # Sort by success rate and usage
        results.sort(
            key=lambda t: (t.success_rate, t.usage_count),
            reverse=True
        )
        
        return results
    
    def get_tools_by_category(self, category: ToolCategory) -> List[Tool]:
        """Get all tools in category"""
        tool_ids = self.category_index.get(category, [])
        return [self.tools[tid] for tid in tool_ids if tid in self.tools]
    
    def _load_registry(self):
        """Load registry from disk (without executors)"""
        # Registry persistence would store metadata only,
        # executors must be re-registered at runtime
        pass
    
    def _save_registry(self):
        """Save registry to disk (metadata only)"""
        try:
            # Save tool metadata without executors
            metadata = {}
            for tool_id, tool in self.tools.items():
                metadata[tool_id] = {
                    "name": tool.name,
                    "description": tool.description,
                    "category": tool.category.value,
                    "parameters": [asdict(p) for p in tool.parameters],
                    "returns": tool.returns,
                    "safety_level": tool.safety_level,
                    "usage_count": tool.usage_count,
                    "success_rate": tool.success_rate,
                    "average_duration": tool.average_duration
                }
            
            with open(self.registry_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save tool registry: {e}")


class ToolSelector:
    """
    Intelligent tool selection based on context and requirements
    """
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
    
    def select_tool(
        self,
        task_description: str,
        required_category: Optional[ToolCategory] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Tool]:
        """
        Select best tool for task
        
        Args:
            task_description: Description of task
            required_category: Required tool category
            context: Additional context
            
        Returns:
            Selected tool or None
        """
        # Search for relevant tools
        tools = self.registry.search_tools(task_description, required_category)
        
        if not tools:
            return None
        
        # Score tools based on context
        scored_tools = []
        for tool in tools:
            score = self._score_tool(tool, task_description, context)
            scored_tools.append((score, tool))
        
        scored_tools.sort(reverse=True, key=lambda x: x[0])
        return scored_tools[0][1] if scored_tools else None
    
    def select_tool_chain(
        self,
        task_description: str,
        max_tools: int = 5
    ) -> List[Tool]:
        """
        Select chain of tools for complex task
        
        Args:
            task_description: Task description
            max_tools: Maximum tools in chain
            
        Returns:
            List of tools in execution order
        """
        # Simple implementation - can be enhanced with planning
        words = task_description.lower().split()
        tool_chain = []
        used_categories = set()
        
        for word in words:
            if len(tool_chain) >= max_tools:
                break
            
            tools = self.registry.search_tools(word)
            for tool in tools:
                if tool.category not in used_categories:
                    tool_chain.append(tool)
                    used_categories.add(tool.category)
                    break
        
        return tool_chain
    
    def _score_tool(
        self,
        tool: Tool,
        task_description: str,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Score tool relevance for task"""
        score = 0.0
        
        # Base score from success rate and usage
        score += tool.success_rate * 10
        score += min(tool.usage_count / 100, 1.0) * 5
        
        # Keyword matching
        task_words = set(task_description.lower().split())
        tool_words = set(tool.name.lower().split() + tool.description.lower().split())
        overlap = len(task_words & tool_words)
        score += overlap * 2
        
        # Safety penalty for dangerous tools
        if tool.safety_level > 1:
            score -= (tool.safety_level - 1) * 3
        
        # Performance bonus
        if tool.average_duration < 1.0:
            score += 2
        
        return score


class ToolExecutor:
    """
    Safe tool execution with error handling and result caching
    """
    
    def __init__(
        self,
        registry: ToolRegistry,
        cache_enabled: bool = True,
        execution_log_path: str = "memory-bundles/tool-executions.json"
    ):
        self.registry = registry
        self.cache_enabled = cache_enabled
        self.execution_log_path = execution_log_path
        self.execution_cache: Dict[str, Tuple[Any, datetime]] = {}
        self.execution_log: List[ToolExecution] = []
        self.execution_counter = 0
    
    def execute(
        self,
        tool_id: str,
        parameters: Dict[str, Any],
        use_cache: bool = True
    ) -> Tuple[bool, Any, Optional[str]]:
        """
        Execute tool with parameters
        
        Args:
            tool_id: Tool to execute
            parameters: Execution parameters
            use_cache: Whether to use cached results
            
        Returns:
            (success, result, error_message)
        """
        tool = self.registry.get_tool(tool_id)
        if not tool:
            return False, None, f"Tool {tool_id} not found"
        
        if not tool.executor:
            return False, None, "Tool has no executor function"
        
        # Check cache
        if use_cache and self.cache_enabled:
            cached_result = self._get_cached_result(tool_id, parameters)
            if cached_result is not None:
                return True, cached_result, None
        
        # Validate parameters
        validation_error = self._validate_parameters(tool, parameters)
        if validation_error:
            return False, None, validation_error
        
        # Execute tool
        start_time = datetime.utcnow()
        try:
            result = tool.executor(**parameters)
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Update tool statistics
            tool.usage_count += 1
            tool.success_rate = (
                (tool.success_rate * (tool.usage_count - 1) + 1.0) / tool.usage_count
            )
            tool.average_duration = (
                (tool.average_duration * (tool.usage_count - 1) + duration) / tool.usage_count
            )
            
            # Cache result
            if self.cache_enabled:
                self._cache_result(tool_id, parameters, result)
            
            # Log execution
            self._log_execution(tool_id, parameters, duration, True, result, None)
            
            return True, result, None
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            error_msg = str(e)
            
            # Update statistics
            tool.usage_count += 1
            tool.success_rate = (
                (tool.success_rate * (tool.usage_count - 1)) / tool.usage_count
            )
            
            # Log execution
            self._log_execution(tool_id, parameters, duration, False, None, error_msg)
            
            return False, None, error_msg
    
    def _validate_parameters(
        self,
        tool: Tool,
        parameters: Dict[str, Any]
    ) -> Optional[str]:
        """Validate parameters against tool definition"""
        for param in tool.parameters:
            if param.required and param.name not in parameters:
                return f"Missing required parameter: {param.name}"
        return None
    
    def _get_cache_key(self, tool_id: str, parameters: Dict[str, Any]) -> str:
        """Generate cache key from tool and parameters"""
        param_str = json.dumps(parameters, sort_keys=True)
        return hashlib.md5(f"{tool_id}:{param_str}".encode()).hexdigest()
    
    def _get_cached_result(
        self,
        tool_id: str,
        parameters: Dict[str, Any]
    ) -> Optional[Any]:
        """Get cached result if available and not expired"""
        cache_key = self._get_cache_key(tool_id, parameters)
        
        if cache_key in self.execution_cache:
            result, timestamp = self.execution_cache[cache_key]
            # Cache expires after 1 hour
            if datetime.utcnow() - timestamp < timedelta(hours=1):
                return result
            else:
                del self.execution_cache[cache_key]
        
        return None
    
    def _cache_result(
        self,
        tool_id: str,
        parameters: Dict[str, Any],
        result: Any
    ):
        """Cache execution result"""
        cache_key = self._get_cache_key(tool_id, parameters)
        self.execution_cache[cache_key] = (result, datetime.utcnow())
    
    def _log_execution(
        self,
        tool_id: str,
        parameters: Dict[str, Any],
        duration: float,
        success: bool,
        result: Any,
        error: Optional[str]
    ):
        """Log tool execution"""
        self.execution_counter += 1
        execution_id = f"exec_{self.execution_counter}_{int(datetime.utcnow().timestamp())}"
        
        execution = ToolExecution(
            execution_id=execution_id,
            tool_id=tool_id,
            parameters=parameters,
            timestamp=datetime.utcnow().isoformat(),
            duration=duration,
            success=success,
            result=str(result)[:200] if result else None,  # Truncate large results
            error=error
        )
        
        self.execution_log.append(execution)
        self._save_log()
    
    def _save_log(self):
        """Save execution log"""
        try:
            with open(self.execution_log_path, 'w') as f:
                json.dump(
                    [asdict(e) for e in self.execution_log[-1000:]],  # Keep last 1000
                    f,
                    indent=2
                )
        except Exception as e:
            print(f"Warning: Could not save execution log: {e}")


class ToolManager:
    """
    Unified tool management system
    
    Integrates registry, selector, and executor for complete
    tool lifecycle management.
    """
    
    def __init__(self):
        self.registry = ToolRegistry()
        self.selector = ToolSelector(self.registry)
        self.executor = ToolExecutor(self.registry)
    
    def register_standard_tools(self):
        """Register standard built-in tools"""
        
        # Example: String processing tool
        def process_text(text: str, operation: str) -> str:
            if operation == "upper":
                return text.upper()
            elif operation == "lower":
                return text.lower()
            elif operation == "reverse":
                return text[::-1]
            return text
        
        self.registry.register_tool(
            name="text_processor",
            description="Process text with various operations",
            category=ToolCategory.DATA_PROCESSING,
            parameters=[
                ToolParameter("text", "str", "Input text", True),
                ToolParameter("operation", "str", "Operation to perform", True)
            ],
            returns="str",
            executor=process_text,
            safety_level=1
        )
        
        # Example: Math computation tool
        def compute(expression: str) -> float:
            # Simple and safe evaluation (in practice, use proper parser)
            try:
                return eval(expression, {"__builtins__": {}}, {})
            except:
                return 0.0
        
        self.registry.register_tool(
            name="calculator",
            description="Perform mathematical computations",
            category=ToolCategory.COMPUTATION,
            parameters=[
                ToolParameter("expression", "str", "Math expression", True)
            ],
            returns="float",
            executor=compute,
            safety_level=2
        )
    
    def auto_select_and_execute(
        self,
        task_description: str,
        parameters: Dict[str, Any]
    ) -> Tuple[bool, Any, Optional[str]]:
        """
        Automatically select and execute appropriate tool
        
        Args:
            task_description: Task description
            parameters: Parameters to pass
            
        Returns:
            (success, result, error)
        """
        tool = self.selector.select_tool(task_description)
        
        if not tool:
            return False, None, "No suitable tool found"
        
        return self.executor.execute(tool.tool_id, parameters)


# Example usage and testing
if __name__ == "__main__":
    print("Barrot Tool Management System")
    print("=" * 50)
    
    # Initialize tool manager
    manager = ToolManager()
    manager.register_standard_tools()
    
    print("\n1. Registered Tools:")
    for tool in manager.registry.tools.values():
        print(f"  - {tool.name}: {tool.description}")
    
    print("\n2. Test Tool Execution:")
    success, result, error = manager.auto_select_and_execute(
        task_description="process text to uppercase",
        parameters={"text": "hello world", "operation": "upper"}
    )
    print(f"  Success: {success}")
    print(f"  Result: {result}")
    
    print("\n" + "=" * 50)
    print("Tool management system initialized successfully!")
