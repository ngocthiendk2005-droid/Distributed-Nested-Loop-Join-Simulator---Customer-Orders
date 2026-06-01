import csv
from pathlib import Path

from distributed_join_simulator.analysis.cost_model import total_execution_time_seconds
from distributed_join_simulator.join_algorithms.page_nested_loop_join import simulate_page_nested_loop_join

COMPARISON_CSV_COLUMNS = [
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
]


def run_comparison_benchmark_to_csv(
    latency_values_ms,
    block_sizes,
    num_customers,
    num_orders,
    output_path,
    semi_join_selectivity=0.25,
    customer_selection_selectivity=1.0,
    order_selection_selectivity=1.0,
):
    rows = []

    for latency_ms in latency_values_ms:
        for block_size in block_sizes:
            standard = _comparison_result(
                mode="standard",
                latency_ms=latency_ms,
                block_size=block_size,
                num_customers=num_customers,
                num_orders=num_orders,
                semi_join_selectivity=semi_join_selectivity,
                customer_selection_selectivity=customer_selection_selectivity,
                order_selection_selectivity=order_selection_selectivity,
            )
            semi_join = _comparison_result(
                mode="semi_join",
                latency_ms=latency_ms,
                block_size=block_size,
                num_customers=num_customers,
                num_orders=num_orders,
                semi_join_selectivity=semi_join_selectivity,
                customer_selection_selectivity=customer_selection_selectivity,
                order_selection_selectivity=order_selection_selectivity,
            )

            rows.append(_with_reductions(standard, standard))
            rows.append(_with_reductions(semi_join, standard))

    _write_csv(output_path, COMPARISON_CSV_COLUMNS, rows)
    return rows


def summarize_comparison_results(csv_path):
    rows = _read_rows(csv_path)
    standard_rows = [row for row in rows if row["mode"] == "standard"]
    semi_rows = [row for row in rows if row["mode"] == "semi_join"]

    average_communication_savings_ms = sum(
        float(standard["communication_latency_ms"]) - float(semi["communication_latency_ms"])
        for standard, semi in zip(standard_rows, semi_rows)
    ) / len(semi_rows)
    average_execution_savings_s = sum(
        float(standard["total_execution_time_s"]) - float(semi["total_execution_time_s"])
        for standard, semi in zip(standard_rows, semi_rows)
    ) / len(semi_rows)

    low_standard, low_semi = min(
        zip(standard_rows, semi_rows),
        key=lambda pair: float(pair[0]["latency_ms"]),
    )
    high_standard, high_semi = max(
        zip(standard_rows, semi_rows),
        key=lambda pair: float(pair[0]["latency_ms"]),
    )

    low_latency_execution_savings = float(low_standard["total_execution_time_s"]) - float(low_semi["total_execution_time_s"])
    high_latency_execution_savings = float(high_standard["total_execution_time_s"]) - float(high_semi["total_execution_time_s"])

    trend = "As network latency increased, absolute time savings from Semi-Join increased"
    if high_latency_execution_savings < low_latency_execution_savings:
        trend = "As network latency increased, absolute time savings from Semi-Join did not increase"

    return (
        f"Semi-Join achieved average absolute communication latency savings of {average_communication_savings_ms:.2f} ms.\n"
        f"Semi-Join achieved average absolute execution time savings of {average_execution_savings_s:.4f} s.\n"
        f"{trend}."
    )


def _comparison_result(
    mode,
    latency_ms,
    block_size,
    num_customers,
    num_orders,
    semi_join_selectivity,
    customer_selection_selectivity,
    order_selection_selectivity,
):
    result = simulate_page_nested_loop_join(
        num_customers=num_customers,
        num_orders=num_orders,
        customer_block_size=block_size,
        order_block_size=block_size,
        latency_ms=latency_ms,
        mode=mode,
        semi_join_selectivity=semi_join_selectivity,
        customer_selection_selectivity=customer_selection_selectivity,
        order_selection_selectivity=order_selection_selectivity,
    )
    return {
        "mode": mode,
        "latency_ms": latency_ms,
        "block_size": block_size,
        "semi_join_selectivity": semi_join_selectivity,
        "customer_selection_selectivity": customer_selection_selectivity,
        "order_selection_selectivity": order_selection_selectivity,
        "query_decomposition": result["query_decomposition"],
        "localized_customer_rows": result["localized_customer_rows"],
        "localized_order_rows": result["localized_order_rows"],
        "pruned_customer_rows": result["pruned_customer_rows"],
        "pruned_order_rows": result["pruned_order_rows"],
        "packets_sent": result["packets_sent"],
        "blocks_transferred": result["blocks_transferred"],
        "communication_latency_ms": result["communication_latency_ms"],
        "total_execution_time_s": _total_time(result),
    }


def _with_reductions(row, standard_row):
    row = dict(row)
    row["packet_reduction_percent"] = _reduction_percent(row["packets_sent"], standard_row["packets_sent"])
    row["communication_reduction_percent"] = _reduction_percent(
        row["communication_latency_ms"],
        standard_row["communication_latency_ms"],
    )
    row["execution_time_reduction_percent"] = _reduction_percent(
        row["total_execution_time_s"],
        standard_row["total_execution_time_s"],
    )
    return row


def _reduction_percent(value, baseline):
    if baseline == 0:
        return 0.0
    return max(0.0, ((baseline - value) / baseline) * 100.0)


def _total_time(result):
    return total_execution_time_seconds(
        cpu_seconds=0.001,
        io_seconds=result["blocks_transferred"] * 0.00001,
        communication_latency_ms=result["communication_latency_ms"],
    )


def _write_csv(output_path, columns, rows):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _read_rows(csv_path):
    with Path(csv_path).open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))
