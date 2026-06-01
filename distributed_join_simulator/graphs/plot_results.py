import csv
from pathlib import Path

import matplotlib.pyplot as plt


def plot_comparison_results(csv_path, time_plot_path, block_size_plot_path, communication_plot_path, packet_plot_path):
    rows = _read_rows(csv_path)
    _plot_comparison(
        rows,
        x_key="latency_ms",
        y_key="total_execution_time_s",
        output_path=time_plot_path,
        title="Execution Time vs Latency: Standard vs Semi-Join",
        x_label="Network Latency (ms)",
        y_label="Total Execution Time (s)",
    )
    _plot_comparison(
        rows,
        x_key="block_size",
        y_key="total_execution_time_s",
        output_path=block_size_plot_path,
        title="Execution Time vs Block Size: Standard vs Semi-Join",
        x_label="Block Size (rows/page)",
        y_label="Total Execution Time (s)",
    )
    _plot_comparison(
        rows,
        x_key="latency_ms",
        y_key="communication_latency_ms",
        output_path=communication_plot_path,
        title="Communication Cost Comparison",
        x_label="Network Latency (ms)",
        y_label="Communication Latency (ms)",
    )
    _plot_comparison(
        rows,
        x_key="latency_ms",
        y_key="packets_sent",
        output_path=packet_plot_path,
        title="Packet Transfer Comparison",
        x_label="Network Latency (ms)",
        y_label="Packets Sent",
    )


def _read_rows(csv_path):
    with Path(csv_path).open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _plot_comparison(rows, x_key, y_key, output_path, title, x_label, y_label):
    plt.figure()
    for mode in ["standard", "semi_join"]:
        mode_rows = [row for row in rows if row["mode"] == mode]
        x_values = [float(row[x_key]) for row in mode_rows]
        y_values = [float(row[y_key]) for row in mode_rows]
        plt.plot(x_values, y_values, marker="o", label=mode.replace("_", " ").title())

    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.grid(True)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close()
