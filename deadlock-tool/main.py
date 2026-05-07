"""CLI entry point. Loads a scenario file, runs detection, and optionally recovers."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import argparse
import json
import unittest

from models.process import Process
from models.resource import Resource
from core.rag import ResourceAllocationGraph
from core.detector import DeadlockDetector
from core.recovery import DeadlockRecovery
from visualizer.graph_viz import draw_rag


def load_scenario(path: str) -> ResourceAllocationGraph:
    with open(path) as f:
        data = json.load(f)
    rag = ResourceAllocationGraph()
    for p in data.get("processes", []):
        rag.add_process(Process(p["id"], p.get("priority", 0), p.get("cpu_time_used", 0.0)))
    for r in data.get("resources", []):
        rag.add_resource(Resource(r["id"], r.get("total_instances", 1)))
    for a in data.get("assignments", []):
        rag.add_assignment_edge(a["resource"], a["process"])
    for req in data.get("requests", []):
        rag.add_request_edge(req["process"], req["resource"])
    return rag


def run_tests():
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=os.path.join(os.path.dirname(__file__), "tests"))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


def main():
    parser = argparse.ArgumentParser(
        description="Deadlock Detection & Recovery Tool"
    )
    parser.add_argument("--scenario", "-s", help="Path to a scenario JSON file")
    parser.add_argument("--recover", "-r", choices=["terminate", "preempt"],
                        help="Recovery strategy to apply after detection")
    parser.add_argument("--visualize", "-v", action="store_true",
                        help="Save RAG visualization as PNG")
    parser.add_argument("--test", action="store_true",
                        help="Run unit test suite")
    args = parser.parse_args()

    if args.test:
        run_tests()
        return

    if not args.scenario:
        parser.print_help()
        return

    rag = load_scenario(args.scenario)

    detector = DeadlockDetector(rag)
    has_deadlock = detector.detect()
    print(detector.report())

    if args.visualize:
        draw_rag(rag, cycle_nodes=detector.deadlocked_processes,
                 output_path="rag_before.png", title="RAG — Initial State")

    if has_deadlock and args.recover:
        recovery = DeadlockRecovery(rag)
        if args.recover == "terminate":
            recovery.terminate_processes()
        else:
            recovery.preempt_resources()
        print("\nRecovery log:")
        for entry in recovery.log:
            print(f"  {entry}")
        if args.visualize:
            draw_rag(rag, output_path="rag_after.png", title="RAG — After Recovery")


if __name__ == "__main__":
    main()

