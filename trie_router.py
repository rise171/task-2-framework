import ipaddress
from models import Route

class TrieNode:
    def __init__(self):
        self.children = {}
        self.route = None


class TrieRouter:
    def __init__(self):
        self.root = TrieNode()

    def add_route(self, route: Route):
        node = self.root
        bits = bin(int(route.network.network_address))[2:].zfill(32)

        for i in range(route.network.prefixlen):
            bit = bits[i]
            if bit not in node.children:
                node.children[bit] = TrieNode()
            node = node.children[bit]

        node.route = route

    def lookup(self, ip: str):
        node = self.root
        bits = bin(int(ipaddress.ip_address(ip)))[2:].zfill(32)

        best = None

        for bit in bits:
            if node.route:
                best = node.route

            if bit not in node.children:
                break

            node = node.children[bit]

        if node.route:
            best = node.route

        return best