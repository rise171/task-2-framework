"""
Тесты для проверки DI контейнера
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.container import DIContainer

class TestDIContainer(unittest.TestCase):
    
    def setUp(self):
        self.container = DIContainer()
    
    def test_singleton(self):
        """Тест: синглтон возвращает один и тот же объект"""
        class Service:
            pass
        
        service_instance = Service()
        self.container.register_singleton(Service, service_instance)
        
        obj1 = self.container.get(Service)
        obj2 = self.container.get(Service)
        
        self.assertIs(obj1, obj2)
    
    def test_factory(self):
        """Тест: фабрика создаёт новые объекты"""
        class Service:
            def __init__(self):
                self.id = id(self)
        
        def factory():
            return Service()
        
        self.container.register_factory(Service, factory)
        
        obj1 = self.container.get(Service)
        obj2 = self.container.get(Service)
        
        self.assertIsNot(obj1, obj2)
    
    def test_transient(self):
        """Тест: транзиентные зависимости"""
        class Service:
            pass
        
        self.container.register_transient(Service, Service)
        
        obj1 = self.container.get(Service)
        obj2 = self.container.get(Service)
        
        self.assertIsNot(obj1, obj2)
    
    def test_missing_dependency(self):
        """Тест: отсутствующая зависимость вызывает ошибку"""
        class Service:
            pass
        
        with self.assertRaises(KeyError):
            self.container.get(Service)
    
    def test_has_dependency(self):
        """Тест: проверка наличия зависимости"""
        class Service:
            pass
        
        self.assertFalse(self.container.has(Service))
        
        self.container.register_singleton(Service, Service())
        self.assertTrue(self.container.has(Service))
    
    def test_clear_container(self):
        """Тест: очистка контейнера"""
        class Service:
            pass
        
        self.container.register_singleton(Service, Service())
        self.assertTrue(self.container.has(Service))
        
        self.container.clear()
        self.assertFalse(self.container.has(Service))

if __name__ == "__main__":
    print("\n" + "="*60)
    print("ЗАПУСК ТЕСТОВ DI КОНТЕЙНЕРА")
    print("="*60)
    unittest.main(verbosity=2)