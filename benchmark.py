import time
import statistics

def benchmark(router, ips):
    times = []

    for ip in ips:
        start = time.perf_counter()
        router.lookup(ip)
        end = time.perf_counter()

        times.append((end - start) * 1e6)

    return times


def get_stats(times):
    times_sorted = sorted(times)

    return {
        "avg": round(statistics.mean(times), 2),
        "p50": round(times_sorted[int(len(times)*0.5)], 2),
        "p95": round(times_sorted[int(len(times)*0.95)], 2),
        "p99": round(times_sorted[int(len(times)*0.99)], 2),
    }