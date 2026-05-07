import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from models.process import Process
from models.resource import Resource
from core.rag import ResourceAllocationGraph
from core.detector import DeadlockDetector
from core.recovery import DeadlockRecovery


def make_deadlock():
    rag = ResourceAllocationGraph()
    p1, p2 = Process("P1", priority=1), Process("P2", priority=2)
    r1, r2 = Resource("R1"), Resource("R2")
    for p in (p1, p2): rag.add_process(p)
    for r in (r1, r2): rag.add_resource(r)
    rag.add_assignment_edge("R1", "P1")
    rag.add_assignment_edge("R2", "P2")
    rag.add_request_edge("P1", "R2")
    rag.add_request_edge("P2", "R1")
    return rag


class TestDeadlockRecovery(unittest.TestCase):

    def test_termination_resolves_deadlock(self):
        rag = make_deadlock()
        recovery = DeadlockRecovery(rag)
        recovery.terminate_processes()
        detector = DeadlockDetector(rag)
        self.assertFalse(detector.detect())

    def test_termination_reduces_process_count(self):
        rag = make_deadlock()
        initial_count = len(rag.processes)
        recovery = DeadlockRecovery(rag)
        recovery.terminate_processes()
        self.assertLess(len(rag.processes), initial_count)

    def test_preemption_resolves_deadlock(self):
        rag = make_deadlock()
        recovery = DeadlockRecovery(rag)
        recovery.preempt_resources()
        detector = DeadlockDetector(rag)
        self.assertFalse(detector.detect())

    def test_recovery_log_not_empty(self):
        rag = make_deadlock()
        recovery = DeadlockRecovery(rag)
        recovery.terminate_processes()
        self.assertGreater(len(recovery.log), 0)

    def test_safe_state_needs_no_recovery(self):
        rag = ResourceAllocationGraph()
        p1 = Process("P1")
        r1 = Resource("R1")
        rag.add_process(p1)
        rag.add_resource(r1)
        rag.add_assignment_edge("R1", "P1")
        recovery = DeadlockRecovery(rag)
        recovery.terminate_processes()
        self.assertEqual(len(rag.processes), 1)


if __name__ == "__main__":
    unittest.main()
