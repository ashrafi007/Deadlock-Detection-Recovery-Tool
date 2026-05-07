"""FastAPI backend exposing deadlock detection & recovery as REST endpoints."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "deadlock-tool"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from models.process import Process
from models.resource import Resource
from core.rag import ResourceAllocationGraph
from core.detector import DeadlockDetector
from core.recovery import DeadlockRecovery

app = FastAPI(title="Deadlock Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Input models ---
class ProcessIn(BaseModel):
    id: str
    priority: int = 0
    cpu_time_used: float = 0.0

class ResourceIn(BaseModel):
    id: str
    total_instances: int = 1

class AssignmentIn(BaseModel):
    resource: str
    process: str

class RequestIn(BaseModel):
    process: str
    resource: str

class ScenarioIn(BaseModel):
    processes: List[ProcessIn]
    resources: List[ResourceIn]
    assignments: List[AssignmentIn]
    requests: List[RequestIn]
    description: Optional[str] = ""


def build_rag(scenario: ScenarioIn) -> ResourceAllocationGraph:
    rag = ResourceAllocationGraph()
    for p in scenario.processes:
        rag.add_process(Process(p.id, p.priority, p.cpu_time_used))
    for r in scenario.resources:
        rag.add_resource(Resource(r.id, r.total_instances))
    for a in scenario.assignments:
        rag.add_assignment_edge(a.resource, a.process)
    for req in scenario.requests:
        rag.add_request_edge(req.process, req.resource)
    return rag


def rag_to_graph_data(rag: ResourceAllocationGraph, deadlocked: List[str]):
    """Convert RAG to nodes/edges for the frontend."""
    nodes = []
    edges = []

    for pid, proc in rag.processes.items():
        nodes.append({
            "id": pid,
            "type": "process",
            "label": pid,
            "priority": proc.priority,
            "cpu_time_used": proc.cpu_time_used,
            "is_deadlocked": pid in deadlocked,
        })

    for rid, res in rag.resources.items():
        nodes.append({
            "id": rid,
            "type": "resource",
            "label": rid,
            "total_instances": res.total_instances,
            "available_instances": res.available_instances,
        })

    # Assignment edges: resource -> process
    for rid, procs in rag.assignment_edges.items():
        for pid in procs:
            edges.append({
                "id": f"assign-{rid}-{pid}",
                "source": rid,
                "target": pid,
                "edge_type": "assignment",
            })

    # Request edges: process -> resource
    for pid, resources in rag.request_edges.items():
        for rid in resources:
            edges.append({
                "id": f"req-{pid}-{rid}",
                "source": pid,
                "target": rid,
                "edge_type": "request",
            })

    return {"nodes": nodes, "edges": edges}


@app.post("/api/detect")
def detect(scenario: ScenarioIn):
    rag = build_rag(scenario)
    detector = DeadlockDetector(rag)
    has_deadlock = detector.detect()
    graph = rag_to_graph_data(rag, detector.deadlocked_processes)
    return {
        "has_deadlock": has_deadlock,
        "deadlocked_processes": detector.deadlocked_processes,
        "cycle_path": detector.cycle_path,
        "report": detector.report(),
        "graph": graph,
    }


@app.post("/api/recover")
def recover(scenario: ScenarioIn, strategy: str = "terminate"):
    rag = build_rag(scenario)
    detector = DeadlockDetector(rag)
    has_deadlock = detector.detect()

    before_graph = rag_to_graph_data(rag, detector.deadlocked_processes)
    before_deadlocked = list(detector.deadlocked_processes)
    before_cycle = list(detector.cycle_path)

    recovery_log = []
    if has_deadlock:
        recovery = DeadlockRecovery(rag)
        if strategy == "terminate":
            recovery.terminate_processes()
        else:
            recovery.preempt_resources()
        recovery_log = recovery.log

    after_detector = DeadlockDetector(rag)
    after_detector.detect()
    after_graph = rag_to_graph_data(rag, after_detector.deadlocked_processes)

    return {
        "had_deadlock": has_deadlock,
        "before_deadlocked": before_deadlocked,
        "before_cycle": before_cycle,
        "recovery_log": recovery_log,
        "after_graph": after_graph,
        "strategy": strategy,
    }


@app.get("/api/scenarios")
def get_scenarios():
    """Return the built-in example scenarios."""
    import json
    examples_dir = os.path.join(os.path.dirname(__file__), "..", "deadlock-tool", "examples")
    scenarios = {}
    for fname in sorted(os.listdir(examples_dir)):
        if fname.endswith(".json"):
            with open(os.path.join(examples_dir, fname)) as f:
                scenarios[fname.replace(".json", "")] = json.load(f)
    return scenarios
