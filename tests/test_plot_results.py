import tempfile
import unittest
from pathlib import Path

from distributed_join_simulator.graphs.plot_results import plot_comparison_results


class PlotResultsTests(unittest.TestCase):
    def test_plot_comparison_results_creates_required_graphs(self):
        csv_content = "mode,latency_ms,block_size,semi_join_selectivity,packets_sent,blocks_transferred,communication_latency_ms,total_execution_time_s,packet_reduction_percent,communication_reduction_percent,execution_time_reduction_percent\n"
        csv_content += "standard,10,10,0.25,200,100,2000,2.5,0,0,0\n"
        csv_content += "semi_join,10,10,0.25,120,60,1200,1.8,40,40,28\n"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            csv_path = temp_path / "comparison.csv"
            time_plot = temp_path / "execution_time_vs_latency.png"
            block_size_plot = temp_path / "execution_time_vs_block_size.png"
            comm_plot = temp_path / "communication_cost_comparison.png"
            packet_plot = temp_path / "packet_transfer_comparison.png"
            csv_path.write_text(csv_content, encoding="utf-8")

            plot_comparison_results(csv_path, time_plot, block_size_plot, comm_plot, packet_plot)

            self.assertTrue(time_plot.exists())
            self.assertTrue(block_size_plot.exists())
            self.assertTrue(comm_plot.exists())
            self.assertTrue(packet_plot.exists())


if __name__ == "__main__":
    unittest.main()
