import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.contract import Module, ModuleInfo
from core.container import DIContainer
from trie_router import TrieRouter

class TrieRouterModule(Module):
    """Модуль, предоставляющий Trie-маршрутизатор"""
    
    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="trie_router",
            version="1.0.0",
            contract_version="1.0",
            description="Trie-маршрутизатор (O(32) сложность)"
        )
    
    @property
    def requires(self) -> list:
        return []  # Не зависит от других модулей
    
    def register_services(self, container: DIContainer) -> None:
        """Регистрирует TrieRouter в контейнере"""
        container.register_singleton(TrieRouter, TrieRouter())
        print("  [TrieRouterModule] Зарегистрирован TrieRouter как синглтон")
    
    def init(self, container: DIContainer) -> None:
        """Инициализация модуля"""
        router = container.get(TrieRouter)
        print(f"  [TrieRouterModule] Инициализирован, router={router}")