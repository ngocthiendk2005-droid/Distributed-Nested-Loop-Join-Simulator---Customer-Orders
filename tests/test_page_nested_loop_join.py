import unittest

from distributed_join_simulator.join_algorithms.page_nested_loop_join import simulate_page_nested_loop_join


class PageNestedLoopJoinTests(unittest.TestCase):
    def test_standard_join_reports_packets_blocks_and_latency(self):
        result = simulate_page_nested_loop_join(
            num_customers=8,
            num_orders=100,
            customer_block_size=2,
            order_block_size=10,
            latency_ms=50,
            mode="standard",
        )

        self.assertEqual(result["blocks_transferred"], 40)
        self.assertEqual(result["packets_sent"], 80)
        self.assertEqual(result["communication_latency_ms"], 4000)

    def test_selectivity_one_matches_standard_transfer(self):
        standard = simulate_page_nested_loop_join(
            num_customers=100,
            num_orders=1000,
            customer_block_size=10,
            order_block_size=10,
            latency_ms=50,
            mode="standard",
        )
        semi = simulate_page_nested_loop_join(
            num_customers=100,
            num_orders=1000,
            customer_block_size=10,
            order_block_size=10,
            latency_ms=50,
            mode="semi_join",
            semi_join_selectivity=1.0,
        )

        self.assertEqual(semi["blocks_transferred"], standard["blocks_transferred"])

    def test_selectivity_zero_is_minimum_transfer_case(self):
        semi = simulate_page_nested_loop_join(
            num_customers=100,
            num_orders=1000,
            customer_block_size=10,
            order_block_size=10,
            latency_ms=50,
            mode="semi_join",
            semi_join_selectivity=0.0,
        )

        self.assertEqual(semi["filtered_order_blocks"], 0)
        self.assertGreaterEqual(semi["packets_sent"], 0)

    def test_default_selectivity_is_0_25(self):
        default_mode = simulate_page_nested_loop_join(
            num_customers=100,
            num_orders=1000,
            customer_block_size=10,
            order_block_size=10,
            latency_ms=50,
            mode="semi_join",
        )
        explicit = simulate_page_nested_loop_join(
            num_customers=100,
            num_orders=1000,
            customer_block_size=10,
            order_block_size=10,
            latency_ms=50,
            mode="semi_join",
            semi_join_selectivity=0.25,
        )

        self.assertEqual(default_mode, explicit)

    def test_semi_join_never_transfers_more_blocks_than_standard(self):
        standard = simulate_page_nested_loop_join(
            num_customers=100,
            num_orders=1000,
            customer_block_size=10,
            order_block_size=10,
            latency_ms=50,
            mode="standard",
        )
        semi = simulate_page_nested_loop_join(
            num_customers=100,
            num_orders=1000,
            customer_block_size=10,
            order_block_size=10,
            latency_ms=50,
            mode="semi_join",
            semi_join_selectivity=0.25,
        )

        self.assertLessEqual(semi["blocks_transferred"], standard["blocks_transferred"])

    def test_selection_predicates_prune_local_rows_before_join(self):
        result = simulate_page_nested_loop_join(
            num_customers=1000,
            num_orders=100000,
            customer_block_size=100,
            order_block_size=1000,
            latency_ms=10,
            mode="standard",
            customer_selection_selectivity=0.2,
            order_selection_selectivity=0.5,
        )

        self.assertEqual(result["localized_customer_rows"], 200)
        self.assertEqual(result["localized_order_rows"], 50000)
        self.assertEqual(result["customer_blocks"], 2)
        self.assertEqual(result["order_blocks"], 50)
        self.assertEqual(result["pruned_customer_rows"], 800)
        self.assertEqual(result["pruned_order_rows"], 50000)
        self.assertEqual(result["query_decomposition"], "sigma_customers_site_a + sigma_orders_site_b + distributed_join")


if __name__ == "__main__":
    unittest.main()
