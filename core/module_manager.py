from typing import List, Dict, Set, Deque
from collections import deque
import yaml
import importlib
import sys
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
        
        # Добавляем путь к модулям в sys.path для возможности импорта
        modules_dir = str(self.modules_path.parent)
        if modules_dir not in sys.path:
            sys.path.insert(0, modules_dir)
    
    def load_from_config(self, config_path: str) -> None:
        """Загружает модули из конфигурационного файла"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            module_names = config.get('modules', [])
            self._load_modules(module_names)
        except FileNotFoundError:
            raise FileNotFoundError(f"Конфигурационный файл не найден: {config_path}")
    
    def load_from_directory(self, directory: str = None) -> None:
        """Загружает все модули из директории"""
        if directory:
            self.modules_path = Path(directory)
            # Обновляем sys.path
            modules_dir = str(self.modules_path.parent)
            if modules_dir not in sys.path:
                sys.path.insert(0, modules_dir)
        
        if not self.modules_path.exists():
            return
        
        # Ищем все Python файлы в директории
        module_files = list(self.modules_path.glob("*.py"))
        
        # Исключаем __init__.py
        module_files = [f for f in module_files if f.name != "__init__.py"]
        
        for module_file in module_files:
            module_name = module_file.stem  # Имя файла без расширения
            
            # Пропускаем уже загруженные модули
            if module_name in self._modules:
                continue
                
            self._load_single_module(module_name)
    
    def _load_modules(self, module_names: List[str]) -> None:
        """Загружает указанные модули"""
        for module_name in module_names:
            if module_name not in self._modules:
                self._load_single_module(module_name)
    
    def _load_single_module(self, module_name: str) -> None:
        """Загружает один модуль"""
        try:
            # Пробуем импортировать модуль
            # Сначала пробуем как есть (без modules. префикса)
            imported_module = None
            tried_paths = []
            
            # Варианты путей для импорта
            import_paths = [
                module_name,                    # прямой импорт
                f"{self.modules_path.name}.{module_name}",  # modules.module_name
                f"{self.modules_path.parent.name}.{self.modules_path.name}.{module_name}",  # полный путь
            ]
            
            for import_path in import_paths:
                try:
                    imported_module = importlib.import_module(import_path)
                    tried_paths.append(import_path)
                    break
                except ImportError:
                    tried_paths.append(import_path)
                    continue
            
            if imported_module is None:
                raise ImportError(f"Не удалось импортировать модуль '{module_name}'. Попробованные пути: {tried_paths}")
            
            # Ищем класс Module
            module_class = None
            for attr_name in dir(imported_module):
                attr = getattr(imported_module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, Module) and 
                    attr != Module):
                    module_class = attr
                    break
            
            if module_class is None:
                raise ImportError(f"В модуле {module_name} не найден класс Module")
            
            # Создаём экземпляр модуля
            module_instance = module_class()
            
            # Проверяем совместимость версий
            self._check_version_compatibility(module_instance.info)
            
            # Сохраняем модуль
            self._modules[module_instance.info.name] = module_instance
            
        except ImportError as e:
            raise ModuleNotFoundError(module_name, list(self._modules.keys())) from e
        except VersionMismatchError:
            raise
        except Exception as e:
            raise ImportError(f"Ошибка загрузки модуля {module_name}: {e}") from e
    
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
        if not self._modules:
            return []
        
        # Строим граф зависимостей
        graph: Dict[str, Set[str]] = {}
        in_degree: Dict[str, int] = {}
        
        for name, module in self._modules.items():
            requires = set(module.requires)
            graph[name] = requires
            in_degree[name] = len(requires)
        
        # Проверяем существование всех зависимостей
        for name, deps in graph.items():
            for dep in deps:
                if dep not in self._modules:
                    raise ModuleNotFoundError(dep, list(self._modules.keys()))
        
        # Топологическая сортировка (алгоритм Кана)
        queue: Deque[str] = deque([name for name, degree in in_degree.items() if degree == 0])
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
            # Находим цикл для сообщения об ошибке
            remaining = set(self._modules.keys()) - set(result)
            cycle = self._detect_cycle(graph, remaining)
            raise CircularDependencyError(cycle if cycle else list(remaining))
        
        return result
    
    def _detect_cycle(self, graph: Dict[str, Set[str]], remaining: Set[str]) -> List[str]:
        """Обнаруживает цикл в графе зависимостей"""
        visited = set()
        
        def dfs(node: str, path: List[str]) -> List[str]:
            if node in path:
                cycle_start = path.index(node)
                return path[cycle_start:] + [node]
            if node in visited:
                return []
            
            visited.add(node)
            for neighbor in graph.get(node, []):
                if neighbor in remaining or neighbor in path:
                    result = dfs(neighbor, path + [node])
                    if result:
                        return result
            return []
        
        for node in remaining:
            cycle = dfs(node, [])
            if cycle:
                return cycle
        return list(remaining)
    
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
    
    def get_module(self, name: str) -> Module:
        """Возвращает модуль по имени"""
        if name not in self._modules:
            raise ModuleNotFoundError(name, list(self._modules.keys()))
        return self._modules[name]
    
    @property
    def modules(self) -> Dict[str, Module]:
        """Возвращает загруженные модули"""
        return self._modules.copy()