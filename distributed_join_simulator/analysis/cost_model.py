def total_execution_time_seconds(cpu_seconds, io_seconds, communication_latency_ms):
    communication_seconds = communication_latency_ms / 1000.0
    return cpu_seconds + io_seconds + communication_seconds
