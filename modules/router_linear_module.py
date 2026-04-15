import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.contract import Module, ModuleInfo
from core.container import DIContainer
from linear_router import LinearRouter
from models import Route

class LinearRouterModule(Module):
    """Модуль, предоставляющий линейный маршрутизатор"""
    
    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="linear_router",
            version="1.0.0",
            contract_version="1.0",
            description="Линейный маршрутизатор (O(N) сложность)"
        )
    
    @property
    def requires(self) -> list:
        return []  # Не зависит от других модулей
    
    def register_services(self, container: DIContainer) -> None:
        """Регистрирует LinearRouter в контейнере"""
        container.register_singleton(LinearRouter, LinearRouter())
        print("  [LinearRouterModule] Зарегистрирован LinearRouter как синглтон")
    
    def init(self, container: DIContainer) -> None:
        """Инициализация модуля"""
        router = container.get(LinearRouter)
        print(f"  [LinearRouterModule] Инициализирован, router={router}")