"""
System Scheduler - Execution ordering, dependency resolution, parallel execution.

Implements:
- Topological sort for system dependency ordering
- Parallel system execution in independent groups
- Frame timing and performance profiling
- System enable/disable at runtime
"""

from __future__ import annotations

import time
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from .ecs_system import EntityRegistry, System


@dataclass
class SystemNode:
    """A system with its dependency metadata."""
    system: System
    depends_on: Set[str] = field(default_factory=set)
    run_after: Set[str] = field(default_factory=set)
    can_run_parallel: bool = False
    execution_group: int = 0


class SystemScheduler:
    """
    Schedules systems with dependency resolution and optional parallelism.

    Groups systems into execution waves where each wave can run in parallel
    after all systems in the previous wave complete.
    """

    def __init__(self):
        self._nodes: Dict[str, SystemNode] = {}
        self._execution_order: List[List[SystemNode]] = []
        self._dirty = True
        self._frame_times: Dict[str, float] = {}

    def add_system(
        self,
        system: System,
        depends_on: Optional[List[str]] = None,
        can_run_parallel: bool = False,
    ) -> None:
        """Register a system with its dependencies."""
        node = SystemNode(
            system=system,
            depends_on=set(depends_on or []),
            can_run_parallel=can_run_parallel,
        )
        self._nodes[system.name] = node
        self._dirty = True

    def remove_system(self, name: str) -> bool:
        """Remove a system from the scheduler."""
        if name in self._nodes:
            del self._nodes[name]
            self._dirty = True
            return True
        return False

    def _build_execution_order(self) -> None:
        """Perform topological sort to determine execution waves."""
        resolved: Set[str] = set()
        waves: List[List[SystemNode]] = []

        remaining = dict(self._nodes)
        max_iterations = len(remaining) + 1
        iteration = 0

        while remaining and iteration < max_iterations:
            iteration += 1
            wave = []
            for name, node in list(remaining.items()):
                if node.depends_on.issubset(resolved):
                    wave.append(node)

            if not wave:
                # Cycle detected - add remaining in arbitrary order
                wave = list(remaining.values())

            for node in wave:
                resolved.add(node.system.name)
                del remaining[node.system.name]
            waves.append(wave)

        self._execution_order = waves
        self._dirty = False

    def execute(self, registry: EntityRegistry, delta_time: float) -> Dict[str, float]:
        """Execute all systems in dependency order."""
        if self._dirty:
            self._build_execution_order()

        for wave in self._execution_order:
            parallel = [n for n in wave if n.can_run_parallel]
            sequential = [n for n in wave if not n.can_run_parallel]

            # Run parallel systems concurrently
            if parallel:
                threads = []
                for node in parallel:
                    if node.system.enabled:
                        t = threading.Thread(
                            target=self._run_system,
                            args=(node.system, registry, delta_time),
                        )
                        threads.append(t)
                        t.start()
                for t in threads:
                    t.join()

            # Run sequential systems
            for node in sequential:
                if node.system.enabled:
                    self._run_system(node.system, registry, delta_time)

        return dict(self._frame_times)

    def _run_system(
        self, system: System, registry: EntityRegistry, delta_time: float
    ) -> None:
        """Run a single system and record its timing."""
        start = time.perf_counter()
        system.update(registry, delta_time)
        self._frame_times[system.name] = (time.perf_counter() - start) * 1000.0

    def get_execution_waves(self) -> List[List[str]]:
        """Return the execution wave structure (list of system name lists)."""
        if self._dirty:
            self._build_execution_order()
        return [[node.system.name for node in wave] for wave in self._execution_order]

    def enable_system(self, name: str) -> bool:
        """Enable a system."""
        node = self._nodes.get(name)
        if node:
            node.system.enabled = True
            return True
        return False

    def disable_system(self, name: str) -> bool:
        """Disable a system without removing it."""
        node = self._nodes.get(name)
        if node:
            node.system.enabled = False
            return True
        return False
