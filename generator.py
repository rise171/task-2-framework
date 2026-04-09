import random
import ipaddress
from models import Route

def generate_routes(n):
    routes = []
    for _ in range(n):
        ip = ipaddress.IPv4Address(random.randint(0, 2**32 - 1))
        prefix = random.randint(8, 32)
        network = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)
        routes.append(Route(str(network), f"NH"))
    return routes


def generate_ips(n):
    return [
        str(ipaddress.IPv4Address(random.randint(0, 2**32 - 1)))
        for _ in range(n)
    ]