import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from models.process import Process
from models.resource import Resource
from core.rag import ResourceAllocationGraph
from core.detector import DeadlockDetector


def make_two_process_deadlock():
    rag = ResourceAllocationGraph()
    p1, p2 = Process("P1"), Process("P2")
    r1, r2 = Resource("R1"), Resource("R2")
    for p in (p1, p2): rag.add_process(p)
    for r in (r1, r2): rag.add_resource(r)
    rag.add_assignment_edge("R1", "P1")
    rag.add_assignment_edge("R2", "P2")
    rag.add_request_edge("P1", "R2")
    rag.add_request_edge("P2", "R1")
    return rag


class TestDeadlockDetector(unittest.TestCase):

    def test_two_process_deadlock(self):
        rag = make_two_process_deadlock()
        detector = DeadlockDetector(rag)
        self.assertTrue(detector.detect())
        self.assertGreater(len(detector.deadlocked_processes), 0)

    def test_safe_state(self):
        rag = ResourceAllocationGraph()
        p1 = Process("P1")
        r1 = Resource("R1")
        rag.add_process(p1)
        rag.add_resource(r1)
        rag.add_assignment_edge("R1", "P1")
        detector = DeadlockDetector(rag)
        self.assertFalse(detector.detect())

    def test_three_process_deadlock(self):
        rag = ResourceAllocationGraph()
        p1, p2, p3 = Process("P1"), Process("P2"), Process("P3")
        r1, r2, r3 = Resource("R1"), Resource("R2"), Resource("R3")
        for p in (p1, p2, p3): rag.add_process(p)
        for r in (r1, r2, r3): rag.add_resource(r)
        rag.add_assignment_edge("R1", "P1")
        rag.add_assignment_edge("R2", "P2")
        rag.add_assignment_edge("R3", "P3")
        rag.add_request_edge("P1", "R2")
        rag.add_request_edge("P2", "R3")
        rag.add_request_edge("P3", "R1")
        detector = DeadlockDetector(rag)
        self.assertTrue(detector.detect())

    def test_single_process_no_deadlock(self):
        rag = ResourceAllocationGraph()
        p1 = Process("P1")
        rag.add_process(p1)
        detector = DeadlockDetector(rag)
        self.assertFalse(detector.detect())

    def test_empty_graph(self):
        rag = ResourceAllocationGraph()
        detector = DeadlockDetector(rag)
        self.assertFalse(detector.detect())


if __name__ == "__main__":
    unittest.main()
