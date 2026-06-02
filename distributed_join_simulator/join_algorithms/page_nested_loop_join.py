import math

from distributed_join_simulator.network.latency_simulator import LatencySimulator


def simulate_page_nested_loop_join(
    num_customers,
    num_orders,
    customer_block_size,
    order_block_size,
    latency_ms,
    mode="standard",
    semi_join_selectivity=0.25,
    customer_selection_selectivity=1.0,
    order_selection_selectivity=1.0,
):
    localized_customer_rows = _selected_rows(num_customers, customer_selection_selectivity)
    localized_order_rows = _selected_rows(num_orders, order_selection_selectivity)
    customer_blocks = math.ceil(localized_customer_rows / customer_block_size)
    order_blocks = math.ceil(localized_order_rows / order_block_size)

    if mode == "standard":
        blocks_transferred = customer_blocks * order_blocks
        packets_sent = blocks_transferred * 2
        filtered_order_blocks = order_blocks
        key_transfer_packets = 0
    elif mode == "semi_join":
        filtered_order_blocks = math.ceil(order_blocks * semi_join_selectivity)
        filtered_order_blocks = min(filtered_order_blocks, order_blocks)

        key_transfer_packets = customer_blocks * 2
        blocks_transferred = customer_blocks * filtered_order_blocks
        packets_sent = key_transfer_packets + (blocks_transferred * 2)
    # Mô phỏng trường hợp node B bị lỗi (không phản hồi)
    elif mode == "node_b_failed":
        print("\n[NETWORK ALERT] Site A is initiating distributed join...")
        print("[NETWORK ALERT] Sending initial packet to Site B (Remote Node)...")
        print("[CRITICAL ERROR] Connection Timeout! Site B is down or unreachable.")
        raise ConnectionError("Distributed Query Aborted: Remote Node failed to respond.")
    else:
        raise ValueError("mode must be 'standard' or 'semi_join'")

    latency_simulator = LatencySimulator(latency_ms=latency_ms)
    communication_latency_ms = latency_simulator.compute_latency_ms(packets_sent)

    return {
        "mode": mode,
        "matched_rows": 0,
        "source_customer_rows": num_customers,
        "source_order_rows": num_orders,
        "localized_customer_rows": localized_customer_rows,
        "localized_order_rows": localized_order_rows,
        "pruned_customer_rows": num_customers - localized_customer_rows,
        "pruned_order_rows": num_orders - localized_order_rows,
        "customer_selection_selectivity": customer_selection_selectivity,
        "order_selection_selectivity": order_selection_selectivity,
        "query_decomposition": "sigma_customers_site_a + sigma_orders_site_b + distributed_join",
        "customer_blocks": customer_blocks,
        "order_blocks": order_blocks,
        "filtered_order_blocks": filtered_order_blocks,
        "key_transfer_packets": key_transfer_packets,
        "blocks_transferred": blocks_transferred,
        "packets_sent": packets_sent,
        "communication_latency_ms": communication_latency_ms,
    }


def _selected_rows(total_rows, selectivity):
    return math.ceil(total_rows * selectivity)
