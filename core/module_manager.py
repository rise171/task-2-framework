from typing import List, Dict, Set, Tuple, Optional
from collections import deque
import yaml
import importlib
import os
from pathlib import Path

from .contract import Module, ModuleInfo
from .exception import ModuleNotFoundError, CircularDependencyError, VersionMismatchError
from .container import DIContainer

class ModuleManager:
    """
    Менеджер модулей.
    Отвечает за загрузку, проверку зависимостей, определение порядка запуска.
    """
    
    def __init__(self, container: DIContainer, modules_path: str = "modules"):
        self.container = container
        self.modules_path = Path(modules_path)
        self._modules: Dict[str, Module] = {}
        self._contract_version = "1.0"
    
    def load_from_config(self, config_path: str) -> None:
        """Загружает модули из конфигурационного файла"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        module_names = config.get('modules', [])
        self._load_modules(module_names)
    
    def load_from_directory(self, directory: str = None) -> None:
        """Загружает все модули из директории"""
        if directory:
            self.modules_path = Path(directory)
        
        if not self.modules_path.exists():
            return
        
        # Ищем все файлы с суффиксом _module.py
        module_files = list(self.modules_path.glob("*_module.py"))
        
        for module_file in module_files:
            module_name = module_file.stem
            self._load_single_module(module_name)
    
    def _load_modules(self, module_names: List[str]) -> None:
        """Загружает указанные модули"""
        for module_name in module_names:
            self._load_single_module(module_name)
    
    def _load_single_module(self, module_name: str) -> None:
        """Загружает один модуль"""
        try:
            # Импортируем модуль
            module_path = f"modules.{module_name}"
            imported_module = importlib.import_module(module_path)
            
            # Ищем класс Module
            for attr_name in dir(imported_module):
                attr = getattr(imported_module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, Module) and 
                    attr != Module):
                    module_instance = attr()
                    
                    # Проверяем совместимость версий
                    self._check_version_compatibility(module_instance.info)
                    
                    self._modules[module_instance.info.name] = module_instance
                    break
            else:
                print(f"Предупреждение: В модуле {module_name} не найден класс Module")
                
        except ImportError as e:
            print(f"Ошибка импорта модуля {module_name}: {e}")
        except VersionMismatchError as e:
            print(f"Ошибка версии: {e}")
            raise
    
    def _check_version_compatibility(self, module_info: ModuleInfo) -> None:
        """Проверяет совместимость версий контракта"""
        if module_info.contract_version != self._contract_version:
            raise VersionMismatchError(
                module_info.name,
                module_info.contract_version,
                self._contract_version
            )
    
    def resolve_order(self) -> List[str]:
        """
        Определяет порядок запуска модулей с учётом зависимостей.
        Использует топологическую сортировку (алгоритм Кана).
        """
        # Строим граф зависимостей
        graph: Dict[str, Set[str]] = {}
        in_degree: Dict[str, int] = {}
        
        for name, module in self._modules.items():
            graph[name] = set(module.requires)
            in_degree[name] = len(module.requires)
        
        # Проверяем существование всех зависимостей
        for name, deps in graph.items():
            for dep in deps:
                if dep not in self._modules:
                    raise ModuleNotFoundError(dep, list(self._modules.keys()))
        
        # Топологическая сортировка
        queue = deque([name for name, degree in in_degree.items() if degree == 0])
        result = []
        
        while queue:
            module = queue.popleft()
            result.append(module)
            
            # Уменьшаем счётчики зависимых модулей
            for other, deps in graph.items():
                if module in deps:
                    in_degree[other] -= 1
                    if in_degree[other] == 0:
                        queue.append(other)
        
        # Проверка на циклы
        if len(result) != len(self._modules):
            # Находим цикл
            remaining = set(self._modules.keys()) - set(result)
            cycle = self._detect_cycle(graph, remaining)
            raise CircularDependencyError(cycle)
        
        return result
    
    def _detect_cycle(self, graph: Dict[str, Set[str]], remaining: Set[str]) -> list:
        """Обнаруживает цикл в графе зависимостей"""
        visited = set()
        
        def dfs(node: str, path: List[str]) -> List[str]:
            if node in path:
                cycle_start = path.index(node)
                return path[cycle_start:]
            if node in visited:
                return []
            
            visited.add(node)
            for neighbor in graph.get(node, []):
                if neighbor in remaining:
                    result = dfs(neighbor, path + [node])
                    if result:
                        return result
            return []
        
        for node in remaining:
            cycle = dfs(node, [])
            if cycle:
                return cycle
        return []
    
    def register_all_services(self) -> None:
        """Регистрирует службы всех модулей в контейнере"""
        for module in self._modules.values():
            module.register_services(self.container)
    
    def init_all_modules(self) -> None:
        """Инициализирует все модули в правильном порядке"""
        order = self.resolve_order()
        
        for module_name in order:
            module = self._modules[module_name]
            print(f"Инициализация модуля: {module_name}")
            module.init(self.container)
    
    @property
    def modules(self) -> Dict[str, Module]:
        """Возвращает загруженные модули"""
        return self._modules.copy()