import unittest

from distributed_join_simulator.analysis.cost_model import total_execution_time_seconds


class CostModelTests(unittest.TestCase):
    def test_total_execution_time_includes_communication_seconds(self):
        total = total_execution_time_seconds(
            cpu_seconds=2.0,
            io_seconds=3.0,
            communication_latency_ms=500,
        )

        self.assertEqual(total, 5.5)


if __name__ == "__main__":
    unittest.main()
