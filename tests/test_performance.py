import sys
import os
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from linear_router import LinearRouter
from trie_router import TrieRouter
from generator import generate_routes, generate_ips
from benchmark import benchmark


def test_trie_faster_than_linear():
    routes = generate_routes(2000)
    ips = generate_ips(1000)

    linear = LinearRouter()
    trie = TrieRouter()

    for r in routes:
        linear.add_route(r)
        trie.add_route(r)

    linear_time = sum(benchmark(linear, ips))
    trie_time = sum(benchmark(trie, ips))

    assert trie_time < linear_time
    print(f"\n Trie router быстрее Linear router: {linear_time:.4f}s vs {trie_time:.4f}s")


if __name__ == "__main__":
    test_trie_faster_than_linear()