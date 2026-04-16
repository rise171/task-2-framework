"""
Distance Vector Routing (Алгоритм Беллмана-Форда)
Используется в протоколах RIP, IGRP
Сложность: O(N * E) на обновление, O(N) на поиск
"""

import ipaddress
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class DVRouteEntry:
    """Запись в таблице маршрутизации Distance Vector"""
    destination: str
    next_hop: str
    distance: int          # метрика (количество прыжков)
    interface: str = "eth0"
    is_active: bool = True


class DistanceVectorRouter:
    """
    Маршрутизатор на основе вектора расстояний.
    Распространяет обновления соседям (алгоритм Беллмана-Форда).
    """
    
    INFINITY = 16  # максимальное расстояние (16 = недоступно)
    
    def __init__(self, router_id: str = "DV_Router"):
        self.router_id = router_id
        self.routing_table: Dict[str, DVRouteEntry] = {}
        self.neighbors: Dict[str, Dict] = {}  # {neighbor_id: {'cost': int, 'interface': str}}
        self.version = 1
    
    def add_route(self, network: str, next_hop: str, distance: int = 1, interface: str = "eth0"):
        """
        Добавляет маршрут в таблицу
        """
        entry = DVRouteEntry(
            destination=network,
            next_hop=next_hop,
            distance=distance,
            interface=interface
        )
        self.routing_table[network] = entry
    
    def add_direct_route(self, network: str, interface: str, distance: int = 1):
        """
        Добавляет непосредственно подключённую сеть
        """
        self.add_route(network, self.router_id, distance, interface)
    
    def add_neighbor(self, neighbor_id: str, cost: int = 1, interface: str = "eth0"):
        """
        Добавляет соседний маршрутизатор
        """
        self.neighbors[neighbor_id] = {
            'cost': cost,
            'interface': interface
        }
    
    def process_update(self, neighbor_id: str, update: Dict[str, int]) -> bool:
        """
        Обрабатывает полученное обновление от соседа
        Алгоритм Беллмана-Форда: dist(A, X) = min(cost(A,B) + dist(B,X))
        """
        if neighbor_id not in self.neighbors:
            return False
        
        neighbor_cost = self.neighbors[neighbor_id]['cost']
        updated = False
        
        for destination, neighbor_distance in update.items():
            if neighbor_distance >= self.INFINITY:
                continue
            
            new_distance = neighbor_cost + neighbor_distance
            
            if destination not in self.routing_table:
                # Новая сеть - добавляем
                entry = DVRouteEntry(
                    destination=destination,
                    next_hop=neighbor_id,
                    distance=new_distance,
                    interface=self.neighbors[neighbor_id]['interface']
                )
                self.routing_table[destination] = entry
                updated = True
                
            elif new_distance < self.routing_table[destination].distance:
                # Нашли более короткий путь
                self.routing_table[destination].next_hop = neighbor_id
                self.routing_table[destination].distance = new_distance
                self.routing_table[destination].interface = self.neighbors[neighbor_id]['interface']
                updated = True
        
        return updated
    
    def get_update_vector(self) -> Dict[str, int]:
        """
        Формирует вектор расстояний для отправки соседям
        """
        update = {}
        for dest, entry in self.routing_table.items():
            if entry.distance < self.INFINITY and entry.next_hop == self.router_id:
                # Отправляем только свои прямые маршруты (split horizon)
                update[dest] = entry.distance
        return update
    
    def lookup(self, ip: str) -> Optional[DVRouteEntry]:
        """
        Поиск маршрута для IP-адреса (Longest Prefix Match)
        Сложность: O(N) - линейный поиск по таблице
        """
        ip_addr = ipaddress.ip_address(ip)
        best_entry = None
        best_prefix_len = -1
        
        for dest, entry in self.routing_table.items():
            if not entry.is_active:
                continue
            try:
                network = ipaddress.ip_network(dest)
                if ip_addr in network:
                    if network.prefixlen > best_prefix_len:
                        best_entry = entry
                        best_prefix_len = network.prefixlen
            except ValueError:
                continue
        
        return best_entry
    
    def print_table(self):
        """Выводит таблицу маршрутизации"""
        print(f"\n  📋 Таблица маршрутизации {self.router_id}:")
        print("  " + "-" * 65)
        print(f"  {'Сеть назначения':<20} {'Next Hop':<12} {'Distance':<10} {'Interface':<10}")
        print("  " + "-" * 65)
        
        for dest, entry in sorted(self.routing_table.items()):
            print(f"  {dest:<20} {entry.next_hop:<12} {entry.distance:<10} {entry.interface:<10}")
        
        print("  " + "-" * 65)


class SimpleDVRouter:
    """
    Упрощённая версия Distance Vector для бенчмарка
    Только lookup с линейным поиском
    """
    
    def __init__(self):
        self.routes: List[Tuple] = []  # (network, next_hop, distance)
    
    def add_route(self, route):
        """Добавляет маршрут (совместимость с генератором)"""
        network = ipaddress.ip_network(route.network)
        self.routes.append((network, route.next_hop, 1))
    
    def lookup(self, ip: str) -> Optional[Tuple]:
        """Поиск маршрута - O(N)"""
        ip_addr = ipaddress.ip_address(ip)
        best = None
        best_prefix = -1
        
        for network, next_hop, distance in self.routes:
            if ip_addr in network:
                if network.prefixlen > best_prefix:
                    best = (network, next_hop, distance)
                    best_prefix = network.prefixlen
        
        return best