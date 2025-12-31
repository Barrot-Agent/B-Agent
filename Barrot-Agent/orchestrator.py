"""
Barrot Multi-Agent Orchestrator

Implements role-based multi-agent coordination inspired by CrewAI,
LangGraph, and other collaborative agent frameworks.

Enables:
- Role-based agent specialization
- Hierarchical task delegation
- Parallel execution
- Inter-agent communication
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict


class AgentRole(Enum):
    """Predefined agent roles"""
    COORDINATOR = "coordinator"
    ANALYST = "analyst"
    DEVELOPER = "developer"
    RESEARCHER = "researcher"
    EVALUATOR = "evaluator"
    EXECUTOR = "executor"
    SPECIALIST = "specialist"


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    DELEGATED = "delegated"


@dataclass
class AgentCapability:
    """Agent capability definition"""
    name: str
    description: str
    proficiency: float = 0.8  # 0.0 to 1.0


@dataclass
class Agent:
    """Agent definition"""
    agent_id: str
    role: AgentRole
    capabilities: List[AgentCapability]
    status: str = "idle"  # idle, busy, offline
    current_task: Optional[str] = None
    tasks_completed: int = 0
    success_rate: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """Task definition"""
    task_id: str
    description: str
    required_capabilities: List[str]
    priority: int = 1  # Higher = more important
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    parent_task: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    result: Optional[Any] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """Inter-agent message"""
    message_id: str
    sender: str
    recipient: str
    content: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    message_type: str = "info"  # info, request, response, alert


class RoleManager:
    """
    Manages agent roles and capabilities
    """
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.role_registry: Dict[AgentRole, List[str]] = defaultdict(list)
    
    def register_agent(
        self,
        agent_id: str,
        role: AgentRole,
        capabilities: List[AgentCapability]
    ) -> Agent:
        """
        Register a new agent
        
        Args:
            agent_id: Unique agent identifier
            role: Agent role
            capabilities: List of agent capabilities
            
        Returns:
            Created agent
        """
        agent = Agent(
            agent_id=agent_id,
            role=role,
            capabilities=capabilities
        )
        
        self.agents[agent_id] = agent
        self.role_registry[role].append(agent_id)
        
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_agents_by_role(self, role: AgentRole) -> List[Agent]:
        """Get all agents with specific role"""
        agent_ids = self.role_registry.get(role, [])
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]
    
    def find_capable_agent(
        self,
        required_capabilities: List[str],
        preferred_role: Optional[AgentRole] = None
    ) -> Optional[Agent]:
        """
        Find agent with required capabilities
        
        Args:
            required_capabilities: Required capability names
            preferred_role: Preferred agent role
            
        Returns:
            Best matching agent or None
        """
        candidates = []
        
        # Filter by role if specified
        if preferred_role:
            candidates = self.get_agents_by_role(preferred_role)
        else:
            candidates = list(self.agents.values())
        
        # Score candidates by capability match
        scored_candidates = []
        for agent in candidates:
            if agent.status != "offline":
                agent_capabilities = {cap.name for cap in agent.capabilities}
                matches = len(set(required_capabilities) & agent_capabilities)
                proficiency = sum(
                    cap.proficiency for cap in agent.capabilities
                    if cap.name in required_capabilities
                ) / max(len(required_capabilities), 1)
                
                score = matches + proficiency + agent.success_rate
                scored_candidates.append((score, agent))
        
        if not scored_candidates:
            return None
        
        # Return best match
        scored_candidates.sort(reverse=True, key=lambda x: x[0])
        return scored_candidates[0][1]
    
    def update_agent_status(self, agent_id: str, status: str):
        """Update agent status"""
        if agent_id in self.agents:
            self.agents[agent_id].status = status


class TaskDelegator:
    """
    Intelligent task delegation and management
    """
    
    def __init__(self, role_manager: RoleManager):
        self.role_manager = role_manager
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[str] = []
        self.task_counter = 0
    
    def create_task(
        self,
        description: str,
        required_capabilities: List[str],
        priority: int = 1,
        parent_task: Optional[str] = None
    ) -> Task:
        """
        Create a new task
        
        Args:
            description: Task description
            required_capabilities: Required capabilities
            priority: Priority level
            parent_task: Parent task ID if subtask
            
        Returns:
            Created task
        """
        self.task_counter += 1
        task_id = f"task_{self.task_counter}_{int(datetime.utcnow().timestamp())}"
        
        task = Task(
            task_id=task_id,
            description=description,
            required_capabilities=required_capabilities,
            priority=priority,
            parent_task=parent_task
        )
        
        self.tasks[task_id] = task
        self.task_queue.append(task_id)
        
        # Sort queue by priority
        self.task_queue.sort(key=lambda tid: self.tasks[tid].priority, reverse=True)
        
        return task
    
    def delegate_task(self, task_id: str) -> Optional[Agent]:
        """
        Delegate task to appropriate agent
        
        Args:
            task_id: Task to delegate
            
        Returns:
            Assigned agent or None
        """
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        
        # Find capable agent
        agent = self.role_manager.find_capable_agent(task.required_capabilities)
        
        if agent:
            task.assigned_agent = agent.agent_id
            task.status = TaskStatus.DELEGATED
            agent.current_task = task_id
            self.role_manager.update_agent_status(agent.agent_id, "busy")
            
            if task_id in self.task_queue:
                self.task_queue.remove(task_id)
            
            return agent
        
        return None
    
    def complete_task(
        self,
        task_id: str,
        result: Any,
        success: bool = True
    ):
        """
        Mark task as completed
        
        Args:
            task_id: Task ID
            result: Task result
            success: Whether task succeeded
        """
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        task.result = result
        task.completed_at = datetime.utcnow().isoformat()
        
        # Update agent
        if task.assigned_agent:
            agent = self.role_manager.get_agent(task.assigned_agent)
            if agent:
                agent.current_task = None
                agent.tasks_completed += 1
                
                # Update success rate (tasks_completed was just incremented)
                old_count = agent.tasks_completed - 1
                if success and old_count >= 0:
                    agent.success_rate = (agent.success_rate * old_count + 1.0) / agent.tasks_completed
                elif old_count >= 0:
                    agent.success_rate = (agent.success_rate * old_count) / agent.tasks_completed
                
                self.role_manager.update_agent_status(agent.agent_id, "idle")
    
    def decompose_task(
        self,
        task_id: str,
        subtask_descriptions: List[Tuple[str, List[str]]]
    ) -> List[Task]:
        """
        Decompose task into subtasks
        
        Args:
            task_id: Parent task ID
            subtask_descriptions: List of (description, required_capabilities)
            
        Returns:
            List of created subtasks
        """
        subtasks = []
        
        for description, capabilities in subtask_descriptions:
            subtask = self.create_task(
                description=description,
                required_capabilities=capabilities,
                priority=self.tasks[task_id].priority,
                parent_task=task_id
            )
            subtasks.append(subtask)
            self.tasks[task_id].subtasks.append(subtask.task_id)
        
        return subtasks
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks"""
        return [
            self.tasks[tid] for tid in self.task_queue
            if self.tasks[tid].status == TaskStatus.PENDING
        ]


class CommunicationHub:
    """
    Inter-agent communication system
    """
    
    def __init__(self):
        self.messages: List[Message] = []
        self.message_counter = 0
        self.mailboxes: Dict[str, List[Message]] = defaultdict(list)
    
    def send_message(
        self,
        sender: str,
        recipient: str,
        content: Dict[str, Any],
        message_type: str = "info"
    ) -> Message:
        """
        Send message between agents
        
        Args:
            sender: Sender agent ID
            recipient: Recipient agent ID
            content: Message content
            message_type: Message type
            
        Returns:
            Sent message
        """
        self.message_counter += 1
        message_id = f"msg_{self.message_counter}_{int(datetime.utcnow().timestamp())}"
        
        message = Message(
            message_id=message_id,
            sender=sender,
            recipient=recipient,
            content=content,
            message_type=message_type
        )
        
        self.messages.append(message)
        self.mailboxes[recipient].append(message)
        
        return message
    
    def get_messages(
        self,
        agent_id: str,
        unread_only: bool = True
    ) -> List[Message]:
        """
        Get messages for agent
        
        Args:
            agent_id: Agent ID
            unread_only: Only return unread messages
            
        Returns:
            List of messages
        """
        messages = self.mailboxes.get(agent_id, [])
        
        if unread_only:
            messages = [m for m in messages if not m.metadata.get('read', False)]
            # Mark as read
            for msg in messages:
                msg.metadata['read'] = True
        
        return messages
    
    def broadcast(
        self,
        sender: str,
        recipients: List[str],
        content: Dict[str, Any],
        message_type: str = "info"
    ) -> List[Message]:
        """
        Broadcast message to multiple agents
        
        Args:
            sender: Sender agent ID
            recipients: List of recipient agent IDs
            content: Message content
            message_type: Message type
            
        Returns:
            List of sent messages
        """
        messages = []
        for recipient in recipients:
            msg = self.send_message(sender, recipient, content, message_type)
            messages.append(msg)
        return messages


class AgentCoordinator:
    """
    Main orchestrator for multi-agent collaboration
    
    Coordinates agents, delegates tasks, and manages communication.
    Inspired by CrewAI's crew coordination and LangGraph's graph orchestration.
    """
    
    def __init__(
        self,
        log_path: str = "memory-bundles/orchestration-log.json"
    ):
        self.role_manager = RoleManager()
        self.task_delegator = TaskDelegator(self.role_manager)
        self.communication_hub = CommunicationHub()
        self.log_path = log_path
        self.orchestration_log: List[Dict] = []
    
    def register_agent(
        self,
        agent_id: str,
        role: AgentRole,
        capabilities: List[str]
    ) -> Agent:
        """
        Register agent with orchestrator
        
        Args:
            agent_id: Agent identifier
            role: Agent role
            capabilities: Capability names
            
        Returns:
            Registered agent
        """
        capability_objects = [
            AgentCapability(name=cap, description=f"{cap} capability")
            for cap in capabilities
        ]
        
        agent = self.role_manager.register_agent(agent_id, role, capability_objects)
        self._log_event("agent_registered", {"agent_id": agent_id, "role": role.value})
        
        return agent
    
    def create_and_delegate_task(
        self,
        description: str,
        required_capabilities: List[str],
        priority: int = 1
    ) -> Tuple[Task, Optional[Agent]]:
        """
        Create task and immediately delegate to capable agent
        
        Args:
            description: Task description
            required_capabilities: Required capabilities
            priority: Priority level
            
        Returns:
            (Task, assigned agent or None)
        """
        task = self.task_delegator.create_task(
            description=description,
            required_capabilities=required_capabilities,
            priority=priority
        )
        
        agent = self.task_delegator.delegate_task(task.task_id)
        
        self._log_event("task_delegated", {
            "task_id": task.task_id,
            "agent_id": agent.agent_id if agent else None,
            "description": description
        })
        
        return task, agent
    
    def execute_collaborative_workflow(
        self,
        workflow_name: str,
        workflow_steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute multi-agent collaborative workflow
        
        Args:
            workflow_name: Workflow identifier
            workflow_steps: List of workflow steps with tasks
            
        Returns:
            Workflow execution result
        """
        self._log_event("workflow_started", {"workflow": workflow_name})
        
        results = {}
        for step in workflow_steps:
            step_name = step.get("name", "unnamed_step")
            tasks = step.get("tasks", [])
            
            # Execute tasks in step
            step_results = []
            for task_desc in tasks:
                task, agent = self.create_and_delegate_task(
                    description=task_desc["description"],
                    required_capabilities=task_desc.get("capabilities", []),
                    priority=task_desc.get("priority", 1)
                )
                
                # Simulate task execution (in real scenario, would be async)
                if agent:
                    step_results.append({
                        "task_id": task.task_id,
                        "agent": agent.agent_id,
                        "status": "delegated"
                    })
            
            results[step_name] = step_results
        
        self._log_event("workflow_completed", {
            "workflow": workflow_name,
            "steps": len(workflow_steps)
        })
        
        return results
    
    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get current orchestration status"""
        return {
            "agents": {
                "total": len(self.role_manager.agents),
                "idle": sum(1 for a in self.role_manager.agents.values() if a.status == "idle"),
                "busy": sum(1 for a in self.role_manager.agents.values() if a.status == "busy")
            },
            "tasks": {
                "pending": len(self.task_delegator.get_pending_tasks()),
                "total": len(self.task_delegator.tasks),
                "completed": sum(1 for t in self.task_delegator.tasks.values() if t.status == TaskStatus.COMPLETED)
            },
            "messages": {
                "total": len(self.communication_hub.messages)
            }
        }
    
    def _log_event(self, event_type: str, details: Dict[str, Any]):
        """Log orchestration event"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details
        }
        self.orchestration_log.append(event)
        self._save_log()
    
    def _save_log(self):
        """Save orchestration log"""
        try:
            with open(self.log_path, 'w') as f:
                json.dump(self.orchestration_log, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save orchestration log: {e}")


# Example usage and testing
if __name__ == "__main__":
    print("Barrot Multi-Agent Orchestrator")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = AgentCoordinator()
    
    # Register agents
    print("\n1. Registering Agents:")
    orchestrator.register_agent(
        agent_id="analyst_01",
        role=AgentRole.ANALYST,
        capabilities=["data_analysis", "pattern_recognition", "reporting"]
    )
    print("  - Registered Analyst agent")
    
    orchestrator.register_agent(
        agent_id="developer_01",
        role=AgentRole.DEVELOPER,
        capabilities=["coding", "debugging", "testing", "architecture"]
    )
    print("  - Registered Developer agent")
    
    orchestrator.register_agent(
        agent_id="researcher_01",
        role=AgentRole.RESEARCHER,
        capabilities=["research", "documentation", "synthesis"]
    )
    print("  - Registered Researcher agent")
    
    # Create and delegate tasks
    print("\n2. Creating and Delegating Tasks:")
    task1, agent1 = orchestrator.create_and_delegate_task(
        description="Analyze AI agent frameworks",
        required_capabilities=["data_analysis", "pattern_recognition"],
        priority=5
    )
    print(f"  - Task delegated to: {agent1.agent_id if agent1 else 'None'}")
    
    task2, agent2 = orchestrator.create_and_delegate_task(
        description="Implement ReAct reasoning module",
        required_capabilities=["coding", "architecture"],
        priority=4
    )
    print(f"  - Task delegated to: {agent2.agent_id if agent2 else 'None'}")
    
    # Check status
    print("\n3. Orchestration Status:")
    status = orchestrator.get_orchestration_status()
    print(f"  - Total agents: {status['agents']['total']}")
    print(f"  - Busy agents: {status['agents']['busy']}")
    print(f"  - Pending tasks: {status['tasks']['pending']}")
    print(f"  - Total tasks: {status['tasks']['total']}")
    
    print("\n" + "=" * 50)
    print("Orchestrator initialized successfully!")
