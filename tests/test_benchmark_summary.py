import tempfile
import unittest
from pathlib import Path

from distributed_join_simulator.analysis.benchmark import summarize_comparison_results


class BenchmarkSummaryTests(unittest.TestCase):
    def test_summary_reports_absolute_savings_trend(self):
        csv_content = "mode,latency_ms,block_size,semi_join_selectivity,packets_sent,blocks_transferred,communication_latency_ms,total_execution_time_s,packet_reduction_percent,communication_reduction_percent,execution_time_reduction_percent\n"
        csv_content += "standard,10,10,0.25,200,100,2000,2.5,0,0,0\n"
        csv_content += "semi_join,10,10,0.25,100,50,1000,1.8,50,50,28\n"
        csv_content += "standard,200,10,0.25,200,100,40000,40.5,0,0,0\n"
        csv_content += "semi_join,200,10,0.25,100,50,20000,20.8,50,50,48\n"

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "comparison.csv"
            csv_path.write_text(csv_content, encoding="utf-8")

            summary = summarize_comparison_results(csv_path)

        self.assertIn("average absolute communication latency savings", summary)
        self.assertIn("average absolute execution time savings", summary)
        self.assertIn("As network latency increased, absolute time savings from Semi-Join increased", summary)


if __name__ == "__main__":
    unittest.main()
