# barrot/core/goals.py
from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum

class GoalStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    ABANDONED = "abandoned"

@dataclass
class Goal:
    id: str
    description: str
    problem: str
    status: GoalStatus = GoalStatus.PENDING
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GoalTracker:
    goals: Dict[str, Goal] = field(default_factory=dict)
    
    def add_goal(self, goal: Goal) -> None:
        self.goals[goal.id] = goal
    
    def update_status(self, goal_id: str, status: GoalStatus) -> None:
        if goal_id in self.goals:
            self.goals[goal_id].status = status
    
    def get_active_goals(self) -> List[Goal]:
        return [g for g in self.goals.values() 
                if g.status in [GoalStatus.PENDING, GoalStatus.IN_PROGRESS]]
    
    def get_blocked_goals(self) -> List[Goal]:
        return [g for g in self.goals.values() if g.status == GoalStatus.BLOCKED]
