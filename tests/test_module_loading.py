#!/usr/bin/env python3
"""
Тесты для проверки загрузки модулей из директории и конфигурации
"""

import sys
import os
import unittest
import tempfile
import shutil
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.container import DIContainer
from core.module_manager import ModuleManager
from core.contract import Module, ModuleInfo
from core.exceptions import ModuleNotFoundError, CircularDependencyError

class TestModuleLoading(unittest.TestCase):
    
    def setUp(self):
        self.container = DIContainer()
        # Создаём временную директорию для тестов
        self.test_dir = tempfile.mkdtemp()
        self.modules_dir = Path(self.test_dir) / "modules"
        self.modules_dir.mkdir()
        
    def tearDown(self):
        # Удаляем временную директорию
        shutil.rmtree(self.test_dir)
    
    def create_test_module_file(self, module_name: str, requires: list = None):
        """Создаёт тестовый файл модуля"""
        if requires is None:
            requires = []
        
        module_content = f'''
import sys
sys.path.append(str(Path(__file__).parent.parent))

from core.contract import Module, ModuleInfo

class {module_name.capitalize()}Module(Module):
    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="{module_name}",
            version="1.0.0",
            contract_version="1.0"
        )
    
    @property
    def requires(self) -> list:
        return {requires}
    
    def register_services(self, container):
        print(f"  Регистрация {{self.info.name}}")
    
    def init(self, container):
        print(f"  Инициализация {{self.info.name}}")
'''
        
        module_file = self.modules_dir / f"{module_name}_module.py"
        with open(module_file, 'w', encoding='utf-8') as f:
            f.write(module_content)
        
        # Создаём __init__.py если нужно
        init_file = self.modules_dir / "__init__.py"
        if not init_file.exists():
            init_file.touch()
    
    def test_load_modules_from_directory(self):
        """Тест 1: Загрузка модулей из директории"""
        # Создаём тестовые модули
        self.create_test_module_file("test_a")
        self.create_test_module_file("test_b")
        
        # Создаём менеджер модулей
        manager = ModuleManager(self.container, str(self.modules_dir))
        
        # Загружаем модули из директории
        manager.load_from_directory()
        
        # Проверяем, что модули загружены
        self.assertIn("test_a", manager.modules)
        self.assertIn("test_b", manager.modules)
        self.assertEqual(len(manager.modules), 2)
        
        print(f"\n✅ Тест 1 пройден: загружено {len(manager.modules)} модулей из директории")
    
    def test_load_modules_with_dependencies(self):
        """Тест 2: Загрузка модулей с зависимостями"""
        # Создаём модули с зависимостями
        self.create_test_module_file("base", [])
        self.create_test_module_file("dependent", ["base"])
        
        manager = ModuleManager(self.container, str(self.modules_dir))
        manager.load_from_directory()
        
        # Проверяем, что оба модуля загружены
        self.assertIn("base", manager.modules)
        self.assertIn("dependent", manager.modules)
        
        # Проверяем зависимости
        self.assertEqual(manager.modules["dependent"].requires, ["base"])
        
        print(f"\n✅ Тест 2 пройден: модули с зависимостями загружены корректно")
    
    def test_load_nonexistent_module_error(self):
        """Тест 3: Ошибка при загрузке несуществующего модуля"""
        manager = ModuleManager(self.container, str(self.modules_dir))
        
        # Пытаемся загрузить несуществующий модуль через конфиг
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("modules:\n  - non_existent_module")
            config_path = f.name
        
        try:
            with self.assertRaises(Exception):  # Должна быть ошибка импорта
                manager.load_from_config(config_path)
            print(f"\n✅ Тест 3 пройден: ошибка при загрузке несуществующего модуля")
        finally:
            os.unlink(config_path)
    
    def test_load_module_with_missing_dependency(self):
        """Тест 4: Модуль с отсутствующей зависимостью"""
        # Создаём модуль, который требует несуществующий модуль
        self.create_test_module_file("dependent", ["missing_module"])
        
        manager = ModuleManager(self.container, str(self.modules_dir))
        manager.load_from_directory()
        
        # Проверяем, что модуль загружен, но зависимость отсутствует
        self.assertIn("dependent", manager.modules)
        
        # При попытке разрешить порядок должна быть ошибка
        with self.assertRaises(ModuleNotFoundError) as context:
            manager.resolve_order()
        
        error_message = str(context.exception)
        self.assertIn("missing_module", error_message)
        
        print(f"\n✅ Тест 4 пройден: обнаружена отсутствующая зависимость - '{error_message}'")
    
    def test_load_module_with_circular_dependency(self):
        """Тест 5: Модули с циклическими зависимостями"""
        # Создаём модули с циклическими зависимостями
        self.create_test_module_file("module_a", ["module_b"])
        self.create_test_module_file("module_b", ["module_a"])
        
        manager = ModuleManager(self.container, str(self.modules_dir))
        manager.load_from_directory()
        
        # При попытке разрешить порядок должна быть ошибка цикла
        with self.assertRaises(CircularDependencyError) as context:
            manager.resolve_order()
        
        error_message = str(context.exception)
        self.assertIn("циклическую", error_message.lower())
        
        print(f"\n✅ Тест 5 пройден: обнаружена циклическая зависимость - '{error_message}'")
    
    def test_load_modules_from_config(self):
        """Тест 6: Загрузка модулей из конфигурационного файла"""
        # Создаём тестовые модули
        self.create_test_module_file("config_test_a")
        self.create_test_module_file("config_test_b")
        
        # Создаём конфиг
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("modules:\n  - config_test_a\n  - config_test_b")
            config_path = f.name
        
        try:
            manager = ModuleManager(self.container, str(self.modules_dir))
            manager.load_from_config(config_path)
            
            # Проверяем, что модули загружены
            self.assertIn("config_test_a", manager.modules)
            self.assertIn("config_test_b", manager.modules)
            
            print(f"\n✅ Тест 6 пройден: загружено {len(manager.modules)} модулей из конфига")
        finally:
            os.unlink(config_path)
    
    def test_load_modules_both_sources(self):
        """Тест 7: Загрузка модулей из обоих источников"""
        # Создаём модули
        self.create_test_module_file("from_dir")
        
        # Создаём конфиг с другим модулем
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("modules:\n  - from_config")
            config_path = f.name
        
        try:
            # Создаём модуль для конфига (должен существовать в директории)
            self.create_test_module_file("from_config")
            
            manager = ModuleManager(self.container, str(self.modules_dir))
            manager.load_from_config(config_path)
            manager.load_from_directory()
            
            # Оба модуля должны быть загружены
            self.assertIn("from_dir", manager.modules)
            self.assertIn("from_config", manager.modules)
            
            print(f"\n✅ Тест 7 пройден: загрузка из обоих источников")
        finally:
            os.unlink(config_path)

class TestModuleVersionCheck(unittest.TestCase):
    
    def setUp(self):
        self.container = DIContainer()
        self.test_dir = tempfile.mkdtemp()
        self.modules_dir = Path(self.test_dir) / "modules"
        self.modules_dir.mkdir()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def create_module_with_version(self, module_name: str, contract_version: str):
        """Создаёт модуль с указанной версией контракта"""
        module_content = f'''
import sys
sys.path.append(str(Path(__file__).parent.parent))

from core.contract import Module, ModuleInfo

class {module_name.capitalize()}Module(Module):
    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="{module_name}",
            version="1.0.0",
            contract_version="{contract_version}"
        )
    
    @property
    def requires(self) -> list:
        return []
    
    def register_services(self, container):
        pass
    
    def init(self, container):
        pass
'''
        module_file = self.modules_dir / f"{module_name}_module.py"
        with open(module_file, 'w', encoding='utf-8') as f:
            f.write(module_content)
        
        init_file = self.modules_dir / "__init__.py"
        if not init_file.exists():
            init_file.touch()
    
    def test_version_compatibility(self):
        """Тест 8: Проверка совместимости версий"""
        from core.exceptions import VersionMismatchError
        
        # Создаём модуль с несовместимой версией
        self.create_module_with_version("incompatible", "2.0")
        
        manager = ModuleManager(self.container, str(self.modules_dir))
        
        # Должна быть ошибка версии
        with self.assertRaises(VersionMismatchError) as context:
            manager.load_from_directory()
        
        error_message = str(context.exception)
        self.assertIn("версию", error_message)
        
        print(f"\n✅ Тест 8 пройден: проверка версий - '{error_message}'")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("ЗАПУСК ТЕСТОВ ЗАГРУЗКИ МОДУЛЕЙ")
    print("="*60)
    unittest.main(verbosity=2)