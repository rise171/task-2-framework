import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.contract import Module, ModuleInfo
from core.container import DIContainer
from benchmark import benchmark, get_stats
from generator import generate_routes, generate_ips

class BenchmarkModule(Module):
    """Модуль для бенчмаркинга маршрутизаторов"""
    
    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="benchmark",
            version="1.0.0",
            contract_version="1.0",
            description="Модуль бенчмаркинга маршрутизаторов"
        )
    
    @property
    def requires(self) -> list:
        # Зависит от одного из маршрутизаторов (определяется в конфиге)
        return ["linear_router"]  # или ["trie_router"]
    
    def register_services(self, container: DIContainer) -> None:
        """Регистрирует сервисы бенчмарка"""
        # Ничего не регистрируем, просто будем использовать зависимости
        pass
    
    def init(self, container: DIContainer) -> None:
        """Запускает бенчмарк"""
        # Пытаемся получить любой из маршрутизаторов
        router = None
        router_type = None
        
        try:
            from linear_router import LinearRouter
            router = container.get(LinearRouter)
            router_type = "Linear"
        except KeyError:
            pass
        
        try:
            from trie_router import TrieRouter
            if router is None:
                router = container.get(TrieRouter)
                router_type = "Trie"
        except KeyError:
            pass
        
        if router is None:
            print("  [BenchmarkModule] Ошибка: Не найден маршрутизатор для тестирования")
            return
        
        print(f"  [BenchmarkModule] Запуск бенчмарка на {router_type} маршрутизаторе")
        
        # Генерируем маршруты
        routes = generate_routes(1000)
        for route in routes:
            router.add_route(route)
        
        # Генерируем IP для запросов
        ips = generate_ips(3000)
        
        # Запускаем бенчмарк
        times = benchmark(router, ips)
        stats = get_stats(times)
        
        print(f"  [BenchmarkModule] Результаты:")
        print(f"    Среднее: {stats['avg']} мкс")
        print(f"    P50: {stats['p50']} мкс")
        print(f"    P95: {stats['p95']} мкс")
        print(f"    P99: {stats['p99']} мкс")