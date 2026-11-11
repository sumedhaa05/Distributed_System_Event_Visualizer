import unittest
from simulator import LamportSimulator

class LamportTests(unittest.TestCase):
    def test_internal_clock_increments(self):
        sim = LamportSimulator(["P1"])
        p = sim.processes["P1"]
        p.internal_event()
        p.internal_event()
        self.assertEqual([e.timestamp for e in p.log], [1, 2])

    def test_receive_uses_max_plus_one(self):
        sim = LamportSimulator(["P1", "P2"])
        p1, p2 = sim.processes["P1"], sim.processes["P2"]
        for _ in range(5):
            p2.internal_event()
        p1.send("P2", "hello")
        self.assertEqual(p2.clock, 6)

    def test_send_receive_causality(self):
        sim = LamportSimulator(["P1", "P2"])
        sim.processes["P1"].send("P2", "hello")
        result = sim.as_dict()
        self.assertTrue(result["consistent"])
        self.assertEqual(result["checks"][0]["send_timestamp"], 1)
        self.assertEqual(result["checks"][0]["receive_timestamp"], 2)

if __name__ == "__main__":
    unittest.main()
