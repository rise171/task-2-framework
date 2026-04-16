"""
Модуль Distance Vector Routing для фреймворка
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.contract import Module, ModuleInfo
from core.container import DIContainer
from distance_vector_router import DistanceVectorRouter, SimpleDVRouter


class DistanceVectorModule(Module):
    """Модуль маршрутизации по вектору расстояний"""
    
    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="distance_vector",
            version="1.0.0",
            contract_version="1.0",
            description="Distance Vector Routing (алгоритм Беллмана-Форда)"
        )
    
    @property
    def requires(self) -> list:
        return []
    
    def register_services(self, container: DIContainer) -> None:
        # Простая версия для бенчмарка
        container.register_singleton(SimpleDVRouter, SimpleDVRouter())
        
        # Полная версия с демонстрацией протокола
        router = DistanceVectorRouter("DV_Router_Main")
        router.add_direct_route("192.168.1.0/24", "eth0", 1)
        router.add_direct_route("10.0.0.0/8", "eth1", 1)
        router.add_neighbor("R2", 1, "eth0")
        router.add_neighbor("R3", 2, "eth1")
        
        container.register_singleton(DistanceVectorRouter, router)
        print("  [DistanceVectorModule] Зарегистрирован DistanceVectorRouter")
    
    def init(self, container: DIContainer) -> None:
        router = container.get(DistanceVectorRouter)
        router.print_table()
        print("  [DistanceVectorModule] Инициализация завершена")