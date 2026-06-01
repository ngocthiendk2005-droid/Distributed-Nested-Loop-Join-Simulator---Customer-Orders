import subprocess
import sys
import unittest


class RunSimulationTests(unittest.TestCase):
    def test_run_simulation_module_succeeds(self):
        result = subprocess.run(
            [sys.executable, "-m", "distributed_join_simulator.simulation.run_simulation"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
