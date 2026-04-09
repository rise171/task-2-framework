from linear_router import LinearRouter
from trie_router import TrieRouter
from generator import generate_routes, generate_ips
from benchmark import benchmark, get_stats

def run():
    sizes = [100, 1000, 5000]
    requests = 3000

    for size in sizes:
        print(f"\n=== ROUTES: {size} ===")

        routes = generate_routes(size)
        ips = generate_ips(requests)

        # Linear
        linear = LinearRouter()
        for r in routes:
            linear.add_route(r)

        linear_stats = get_stats(benchmark(linear, ips))

        # Trie
        trie = TrieRouter()
        for r in routes:
            trie.add_route(r)

        trie_stats = get_stats(benchmark(trie, ips))

        print("Linear:", linear_stats)
        print("Trie  :", trie_stats)


if __name__ == "__main__":
    run()