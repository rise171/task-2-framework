#!/usr/bin/env python3
"""
Тест взаимодействия трёх модулей:
1. Reporter - формирование отчётов
2. Exporter - экспорт данных
3. Logger - валидация и журналирование
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.container import DIContainer
from core.module_manager import ModuleManager


class TestThreeModules(unittest.TestCase):
    
    def setUp(self):
        self.container = DIContainer()
        self.manager = ModuleManager(self.container, "modules")
    
    def test_modules_interaction(self):
        """Тест взаимодействия трёх модулей"""
        
        # Загружаем модули
        self.manager.load_from_directory()
        
        # Проверяем, что все три модуля загружены
        module_names = list(self.manager.modules.keys())
        
        required_modules = ["reporter", "exporter", "logger"]
        for required in required_modules:
            self.assertIn(required, module_names)
        
        # Проверяем порядок запуска
        order = self.manager.resolve_order()
        
        # Logger должен быть после router, но до остальных
        linear_index = order.index("linear_router")
        logger_index = order.index("logger")
        reporter_index = order.index("reporter")
        exporter_index = order.index("exporter")
        
        self.assertLess(linear_index, logger_index)
        self.assertLess(logger_index, reporter_index)
        self.assertLess(reporter_index, exporter_index)
        
        print(f"\n Тест пройден: порядок модулей - {order}")
    
    def test_logger_validation(self):
        """Тест валидации IP"""
        from modules.logger_modules import ValidationLogger
        
        logger = ValidationLogger()
        
        test_cases = [
            ("192.168.1.1", True, True),    # валидный, приватный
            ("8.8.8.8", True, False),        # валидный, публичный
            ("invalid", False, False),       # невалидный
            ("127.0.0.1", True, True),       # loopback (приватный)
        ]
        
        for ip, expected_valid, expected_private in test_cases:
            result = logger.validate_ip(ip)
            self.assertEqual(result['is_valid'], expected_valid)
            if expected_valid:
                self.assertEqual(result['is_private'], expected_private)
        
        print(f"\n Тест валидации пройден")
    
    def test_logger_stats(self):
        """Тест статистики логгера"""
        from modules.logger_modules import ValidationLogger
        
        logger = ValidationLogger()
        
        # Добавляем тестовые записи
        logger.log_lookup("192.168.1.1", True, 1.5)
        logger.log_lookup("8.8.8.8", True, 2.0)
        logger.log_lookup("invalid_ip", False, 0.5)
        
        stats = logger.get_stats_report()
        
        self.assertEqual(stats['total_lookups'], 3)
        self.assertEqual(stats['valid_ips'], 2)
        self.assertEqual(stats['invalid_ips'], 1)
        self.assertEqual(stats['private_ips'], 1)
        self.assertEqual(stats['public_ips'], 1)
        
        print(f"\n✅ Тест статистики пройден")
        print(f"   Статистика: {stats}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print(" ТЕСТ ТРЁХ МОДУЛЕЙ: Reporter + Exporter + Logger")
    print("="*60)
    unittest.main(verbosity=2)