import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from distributed_join_simulator.analysis.benchmark import run_comparison_benchmark_to_csv, summarize_comparison_results
from distributed_join_simulator.graphs.plot_results import plot_comparison_results


def main():
    output_csv = Path("graphs") / "semi_join_comparison.csv"
    time_plot = Path("graphs") / "execution_time_vs_latency.png"
    block_size_plot = Path("graphs") / "execution_time_vs_block_size.png"
    communication_plot = Path("graphs") / "communication_cost_comparison.png"
    packet_plot = Path("graphs") / "packet_transfer_comparison.png"

    run_comparison_benchmark_to_csv(
        latency_values_ms=list(range(1, 201)),
        block_sizes=[5, 10, 20, 50, 100, 200],
        num_customers=1000,
        num_orders=100000,
        output_path=output_csv,
        semi_join_selectivity=0.25,
        customer_selection_selectivity=0.4,
        order_selection_selectivity=0.5,
    )
    plot_comparison_results(output_csv, time_plot, block_size_plot, communication_plot, packet_plot)

    summary = summarize_comparison_results(output_csv)
    print(summary)


if __name__ == "__main__":
    main()
