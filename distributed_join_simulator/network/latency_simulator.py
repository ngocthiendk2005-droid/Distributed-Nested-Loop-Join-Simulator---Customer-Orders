class LatencySimulator:
    """Deterministic latency model for distributed communication."""

    def __init__(self, latency_ms):
        self.latency_ms = latency_ms

    def compute_latency_ms(self, packets):
        return packets * self.latency_ms

    def compute_latency_seconds(self, packets):
        return self.compute_latency_ms(packets) / 1000.0
