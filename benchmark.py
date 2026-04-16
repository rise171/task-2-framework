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

from generator import generate_ips, generate_routes
from linear_router import LinearRouter
from trie_router import TrieRouter

def run():
    sizes = [100, 1000, 5000]  # РАЗНЫЙ РАЗМЕР МАРШРУТОВ
    requests = 3000

    for size in sizes:
        print(f"\n=== ROUTES: {size} ===")
        
        routes = generate_routes(size)  # Генерируем N маршрутов
        ips = generate_ips(requests)     # Генерируем IP для запросов
        
        # Измеряем LINEAR
        linear = LinearRouter()
        for r in routes:
            linear.add_route(r)
        linear_stats = get_stats(benchmark(linear, ips))
        
        # Измеряем TRIE
        trie = TrieRouter()
        for r in routes:
            trie.add_route(r)
        trie_stats = get_stats(benchmark(trie, ips))
        
        print("Linear:", linear_stats)
        print("Trie  :", trie_stats)

if __name__ == "__main__":
    run()