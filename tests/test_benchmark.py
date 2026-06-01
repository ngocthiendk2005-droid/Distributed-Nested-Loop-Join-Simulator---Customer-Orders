import csv
import tempfile
import unittest
from pathlib import Path

from distributed_join_simulator.analysis.benchmark import run_comparison_benchmark_to_csv


class BenchmarkTests(unittest.TestCase):
    def test_comparison_benchmark_writes_required_csv_columns(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "comparison.csv"

            run_comparison_benchmark_to_csv(
                latency_values_ms=[10, 20],
                block_sizes=[5],
                num_customers=10,
                num_orders=100,
                output_path=output_path,
            )

            with output_path.open(newline="", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

        self.assertEqual(len(rows), 4)
        self.assertEqual(
            rows[0].keys(),
            {
                "mode",
                "latency_ms",
                "block_size",
                "semi_join_selectivity",
                "customer_selection_selectivity",
                "order_selection_selectivity",
                "query_decomposition",
                "localized_customer_rows",
                "localized_order_rows",
                "pruned_customer_rows",
                "pruned_order_rows",
                "packets_sent",
                "blocks_transferred",
                "communication_latency_ms",
                "total_execution_time_s",
                "packet_reduction_percent",
                "communication_reduction_percent",
                "execution_time_reduction_percent",
            },
        )

    def test_comparison_benchmark_contains_reduction_metrics_for_semi_join_rows(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "comparison.csv"

            run_comparison_benchmark_to_csv(
                latency_values_ms=[50],
                block_sizes=[10],
                num_customers=100,
                num_orders=1000,
                output_path=output_path,
            )

            with output_path.open(newline="", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

        semi_row = next(row for row in rows if row["mode"] == "semi_join")
        self.assertGreaterEqual(float(semi_row["packet_reduction_percent"]), 0.0)
        self.assertGreaterEqual(float(semi_row["communication_reduction_percent"]), 0.0)
        self.assertGreaterEqual(float(semi_row["execution_time_reduction_percent"]), 0.0)

    def test_comparison_benchmark_records_localization_metrics(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "comparison.csv"

            run_comparison_benchmark_to_csv(
                latency_values_ms=[10],
                block_sizes=[100],
                num_customers=1000,
                num_orders=100000,
                output_path=output_path,
                customer_selection_selectivity=0.2,
                order_selection_selectivity=0.5,
            )

            with output_path.open(newline="", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

        standard_row = next(row for row in rows if row["mode"] == "standard")
        self.assertEqual(standard_row["customer_selection_selectivity"], "0.2")
        self.assertEqual(standard_row["order_selection_selectivity"], "0.5")
        self.assertEqual(standard_row["localized_customer_rows"], "200")
        self.assertEqual(standard_row["localized_order_rows"], "50000")
        self.assertEqual(standard_row["pruned_customer_rows"], "800")
        self.assertEqual(standard_row["pruned_order_rows"], "50000")
        self.assertEqual(
            standard_row["query_decomposition"],
            "sigma_customers_site_a + sigma_orders_site_b + distributed_join",
        )


if __name__ == "__main__":
    unittest.main()
