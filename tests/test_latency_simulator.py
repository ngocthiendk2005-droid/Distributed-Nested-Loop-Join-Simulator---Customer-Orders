import unittest

from distributed_join_simulator.network.latency_simulator import LatencySimulator


class LatencySimulatorTests(unittest.TestCase):
    def test_compute_latency_ms_from_packets(self):
        simulator = LatencySimulator(latency_ms=50)

        self.assertEqual(simulator.compute_latency_ms(10), 500)

    def test_compute_latency_seconds_from_packets(self):
        simulator = LatencySimulator(latency_ms=25)

        self.assertEqual(simulator.compute_latency_seconds(40), 1.0)

    def test_zero_packets_has_zero_latency(self):
        simulator = LatencySimulator(latency_ms=100)

        self.assertEqual(simulator.compute_latency_ms(0), 0)
        self.assertEqual(simulator.compute_latency_seconds(0), 0.0)


if __name__ == "__main__":
    unittest.main()
