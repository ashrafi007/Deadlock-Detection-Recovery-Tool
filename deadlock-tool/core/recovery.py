from __future__ import annotations
from typing import List
from core.rag import ResourceAllocationGraph
from core.detector import DeadlockDetector


class DeadlockRecovery:
    def __init__(self, rag: ResourceAllocationGraph):
        self.rag = rag
        self.log: List[str] = []

    def _is_deadlocked(self) -> bool:
        detector = DeadlockDetector(self.rag)
        return detector.detect()

    def terminate_processes(self) -> None:
        """Kill lowest-cost deadlocked process one at a time until safe."""
        self.log.clear()
        detector = DeadlockDetector(self.rag)
        while detector.detect():
            victims = [
                self.rag.processes[pid]
                for pid in detector.deadlocked_processes
                if pid in self.rag.processes
            ]
            if not victims:
                break
            victim = min(victims, key=lambda p: p.recovery_cost())
            self.log.append(f"Terminating process {victim.process_id} "
                            f"(cost={victim.recovery_cost():.2f})")
            self.rag.remove_process(victim.process_id)
            detector = DeadlockDetector(self.rag)
        self.log.append("Recovery complete — system is now in a safe state.")

    def preempt_resources(self) -> None:
        """Forcibly take a resource from the cheapest deadlocked victim."""
        self.log.clear()
        detector = DeadlockDetector(self.rag)
        while detector.detect():
            victims = [
                self.rag.processes[pid]
                for pid in detector.deadlocked_processes
                if pid in self.rag.processes
            ]
            if not victims:
                break
            victim = min(victims, key=lambda p: p.recovery_cost())
            victim.preemption_count += 1
            held = list(victim.held_resources.keys())
            if not held:
                self.rag.remove_process(victim.process_id)
                self.log.append(f"Terminated {victim.process_id} (no resources to preempt)")
            else:
                resource_id = held[0]
                self.rag.assignment_edges.get(resource_id, set()).discard(victim.process_id)
                victim.held_resources.pop(resource_id, None)
                self.log.append(f"Preempted resource {resource_id} from {victim.process_id}")
            detector = DeadlockDetector(self.rag)
        self.log.append("Recovery complete — system is now in a safe state.")
