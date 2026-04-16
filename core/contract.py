from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum

# Для аннотаций типов, чтобы избежать циклического импорта
if TYPE_CHECKING:
    from .container import DIContainer

class ModuleState(Enum):
    REGISTERED = "registered"
    INITIALIZED = "initialized"
    STARTED = "started"
    FAILED = "failed"

@dataclass
class ModuleInfo:
    """Информация о модуле для проверки совместимости"""
    name: str
    version: str
    contract_version: str = "1.0"
    description: str = ""

class Module(ABC):
    """
    Контракт модуля расширения.
    Все модули должны реализовывать этот интерфейс.
    """
    
    @property
    @abstractmethod
    def info(self) -> ModuleInfo:
        """Информация о модуле (имя, версия, совместимость)"""
        pass
    
    @property
    @abstractmethod
    def requires(self) -> List[str]:
        """Список имён модулей, от которых зависит данный модуль"""
        pass
    
    @abstractmethod
    def register_services(self, container: 'DIContainer') -> None:
        """
        1: Регистрация служб в контейнере DI.
        Здесь модуль регистрирует свои классы, фабрики, синглтоны.
        """
        pass
    
    @abstractmethod
    def init(self, container: 'DIContainer') -> None:
        """
        2: Инициализация модуля.
        Здесь модуль получает зависимости из контейнера и выполняет инициализацию.
        """
        pass
    
    def start(self, container: 'DIContainer') -> None:
        """
        3: Запуск модуля.
        Для модулей, которым нужен отдельный поток или сервер.
        """
        pass