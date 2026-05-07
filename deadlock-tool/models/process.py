from __future__ import annotations
from typing import Dict


class Process:
    def __init__(self, process_id: str, priority: int = 0, cpu_time_used: float = 0.0):
        self.process_id = process_id
        self.priority = priority
        self.cpu_time_used = cpu_time_used
        self.held_resources: Dict[str, int] = {}
        self.waiting_for: Dict[str, int] = {}
        self.is_terminated: bool = False
        self.preemption_count: int = 0

    def hold(self, resource_id: str, count: int = 1) -> None:
        self.held_resources[resource_id] = self.held_resources.get(resource_id, 0) + count

    def request(self, resource_id: str, count: int = 1) -> None:
        self.waiting_for[resource_id] = self.waiting_for.get(resource_id, 0) + count

    def release_all(self) -> Dict[str, int]:
        released = dict(self.held_resources)
        self.held_resources.clear()
        self.waiting_for.clear()
        self.is_terminated = True
        return released

    def recovery_cost(self) -> float:
        """Lower cost = better victim. Combines priority and CPU time invested."""
        return self.priority + self.cpu_time_used

    def __repr__(self) -> str:
        return (f"Process({self.process_id}, priority={self.priority}, "
                f"terminated={self.is_terminated})")
