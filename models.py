import ipaddress

class Route:
    def __init__(self, network: str, next_hop: str):
        self.network = ipaddress.ip_network(network)
        self.next_hop = next_hop

    def matches(self, ip: str):
        return ipaddress.ip_address(ip) in self.network