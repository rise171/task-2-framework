from typing import Dict, Type, TypeVar, Callable, Any, Optional
from threading import Lock

T = TypeVar('T')

class DIContainer:
    """
    Контейнер внедрения зависимостей.
    Поддерживает синглтоны, транзиентные зависимости и фабрики.
    """
    
    def __init__(self):
        self._singletons: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._lock = Lock()
    
    def register_singleton(self, interface: Type[T], implementation: Any) -> None:
        """Регистрирует синглтон (один экземпляр на всё приложение)"""
        with self._lock:
            self._singletons[interface] = implementation
    
    def register_factory(self, interface: Type[T], factory: Callable[..., T]) -> None:
        """Регистрирует фабрику для создания экземпляров"""
        with self._lock:
            self._factories[interface] = factory
    
    def register_transient(self, interface: Type[T], implementation: Type[T]) -> None:
        """Регистрирует транзиентную зависимость (новый экземпляр при каждом запросе)"""
        def factory():
            return implementation()
        self.register_factory(interface, factory)
    
    def get(self, interface: Type[T], **kwargs) -> T:
        """Получает зависимость из контейнера"""
        # Сначала проверяем синглтоны
        if interface in self._singletons:
            return self._singletons[interface]
        
        # Затем фабрики
        if interface in self._factories:
            return self._factories[interface](**kwargs)
        
        raise KeyError(f"Зависимость {interface.__name__} не зарегистрирована в контейнере")
    
    def has(self, interface: Type) -> bool:
        """Проверяет, зарегистрирована ли зависимость"""
        return interface in self._singletons or interface in self._factories
    
    def clear(self) -> None:
        """Очищает контейнер (для тестов)"""
        with self._lock:
            self._singletons.clear()
            self._factories.clear()