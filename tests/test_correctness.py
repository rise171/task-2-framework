from linear_router import LinearRouter
from trie_router import TrieRouter
from models import Route


def test_same_results():
    routes = [
        Route("192.168.1.0/24", "A"),
        Route("192.168.0.0/16", "B"),
    ]

    ip = "192.168.1.10"

    linear = LinearRouter()
    trie = TrieRouter()

    for r in routes:
        linear.add_route(r)
        trie.add_route(r)

    assert linear.lookup(ip).next_hop == trie.lookup(ip).next_hop