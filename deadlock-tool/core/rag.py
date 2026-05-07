from __future__ import annotations
from typing import Dict, Set
from models.process import Process
from models.resource import Resource


class ResourceAllocationGraph:
    def __init__(self):
        self.processes: Dict[str, Process] = {}
        self.resources: Dict[str, Resource] = {}
        # assignment_edges: resource_id -> set of process_ids holding it
        self.assignment_edges: Dict[str, Set[str]] = {}
        # request_edges: process_id -> set of resource_ids it is waiting for
        self.request_edges: Dict[str, Set[str]] = {}

    def add_process(self, process: Process) -> None:
        self.processes[process.process_id] = process
        self.request_edges.setdefault(process.process_id, set())

    def add_resource(self, resource: Resource) -> None:
        self.resources[resource.resource_id] = resource
        self.assignment_edges.setdefault(resource.resource_id, set())

    def add_assignment_edge(self, resource_id: str, process_id: str) -> None:
        """Resource R is assigned to process P."""
        self.assignment_edges.setdefault(resource_id, set()).add(process_id)
        self.processes[process_id].hold(resource_id)

    def add_request_edge(self, process_id: str, resource_id: str) -> None:
        """Process P is waiting for resource R."""
        self.request_edges.setdefault(process_id, set()).add(resource_id)
        self.processes[process_id].request(resource_id)

    def remove_process(self, process_id: str) -> None:
        process = self.processes.pop(process_id, None)
        if process is None:
            return
        released = process.release_all()
        for resource_id in released:
            self.assignment_edges.get(resource_id, set()).discard(process_id)
        self.request_edges.pop(process_id, None)

    def remove_request_edge(self, process_id: str, resource_id: str) -> None:
        self.request_edges.get(process_id, set()).discard(resource_id)
        self.processes[process_id].waiting_for.pop(resource_id, None)

    def get_wait_for_graph(self) -> Dict[str, Set[str]]:
        """Return process -> set of processes it is waiting on (for cycle detection)."""
        wait_for: Dict[str, Set[str]] = {pid: set() for pid in self.processes}
        for process_id, wanted_resources in self.request_edges.items():
            for resource_id in wanted_resources:
                holding_processes = self.assignment_edges.get(resource_id, set())
                for holder in holding_processes:
                    if holder != process_id:
                        wait_for[process_id].add(holder)
        return wait_for
