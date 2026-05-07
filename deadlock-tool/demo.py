"""Standalone demo — no user input needed. Auto-runs the 3-process deadlock."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from models.process import Process
from models.resource import Resource
from core.rag import ResourceAllocationGraph
from core.detector import DeadlockDetector
from core.recovery import DeadlockRecovery
from visualizer.graph_viz import draw_rag


def build_three_process_deadlock() -> ResourceAllocationGraph:
    rag = ResourceAllocationGraph()
    processes = [Process("P1", priority=1, cpu_time_used=0.5),
                 Process("P2", priority=2, cpu_time_used=1.0),
                 Process("P3", priority=3, cpu_time_used=1.5)]
    resources = [Resource("R1"), Resource("R2"), Resource("R3")]
    for p in processes:
        rag.add_process(p)
    for r in resources:
        rag.add_resource(r)
    rag.add_assignment_edge("R1", "P1")
    rag.add_assignment_edge("R2", "P2")
    rag.add_assignment_edge("R3", "P3")
    rag.add_request_edge("P1", "R2")
    rag.add_request_edge("P2", "R3")
    rag.add_request_edge("P3", "R1")
    return rag


def main():
    print("=" * 50)
    print("  Deadlock Detection & Recovery Tool — Demo")
    print("=" * 50)

    rag = build_three_process_deadlock()

    print("\n[Step 1] Detecting deadlock...")
    detector = DeadlockDetector(rag)
    has_deadlock = detector.detect()
    print(detector.report())

    if has_deadlock:
        draw_rag(rag, cycle_nodes=detector.deadlocked_processes,
                 output_path="rag_deadlock.png", title="RAG — Deadlock State")

        print("\n[Step 2] Recovering via process termination...")
        recovery = DeadlockRecovery(rag)
        recovery.terminate_processes()
        for entry in recovery.log:
            print(f"  {entry}")

        print("\n[Step 3] Verifying recovery...")
        detector2 = DeadlockDetector(rag)
        detector2.detect()
        print(detector2.report())
        draw_rag(rag, output_path="rag_recovered.png", title="RAG — After Recovery")

    print("\nDone.")


if __name__ == "__main__":
    main()
