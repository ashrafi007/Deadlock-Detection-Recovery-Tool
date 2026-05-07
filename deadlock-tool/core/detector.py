from __future__ import annotations
from typing import List, Set, Dict
from core.rag import ResourceAllocationGraph


class DeadlockDetector:
    def __init__(self, rag: ResourceAllocationGraph):
        self.rag = rag
        self.deadlocked_processes: List[str] = []
        self.cycle_path: List[str] = []

    def detect(self) -> bool:
        wait_for = self.rag.get_wait_for_graph()
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        self.deadlocked_processes = []
        self.cycle_path = []

        def dfs(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            for neighbour in wait_for.get(node, set()):
                if neighbour not in visited:
                    if dfs(neighbour, path):
                        return True
                elif neighbour in rec_stack:
                    cycle_start = path.index(neighbour)
                    self.cycle_path = path[cycle_start:]
                    self.deadlocked_processes = list(set(self.cycle_path))
                    return True
            path.pop()
            rec_stack.discard(node)
            return False

        for process_id in list(wait_for.keys()):
            if process_id not in visited:
                if dfs(process_id, []):
                    return True
        return False

    def report(self) -> str:
        if not self.deadlocked_processes:
            return "SAFE STATE — No deadlock detected."
        processes = ", ".join(self.deadlocked_processes)
        cycle = " -> ".join(self.cycle_path + [self.cycle_path[0]])
        return (f"DEADLOCK DETECTED\n"
                f"Deadlocked processes : {processes}\n"
                f"Cycle               : {cycle}")
