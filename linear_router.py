from models import Route

class LinearRouter:
    def __init__(self):
        self.routes = []

    def add_route(self, route: Route):
        self.routes.append(route)

    def lookup(self, ip: str):
        best = None
        best_prefix = -1

        for route in self.routes:
            if route.matches(ip):
                if route.network.prefixlen > best_prefix:
                    best = route
                    best_prefix = route.network.prefixlen

        return best