"""
Модуль журналирования и валидации данных
Демонстрирует:
- Журналирование операций маршрутизации
- Валидацию IP-адресов
- Статистику запросов
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.contract import Module, ModuleInfo
from core.container import DIContainer


class ValidationLogger:
    """
    Сервис валидации и журналирования
    Собирает статистику, проверяет IP, логирует операции
    """
    
    def __init__(self):
        self.logs: List[Dict] = []
        self.stats = {
            'total_lookups': 0,
            'valid_ips': 0,
            'invalid_ips': 0,
            'private_ips': 0,
            'public_ips': 0,
            'routes_found': 0,
            'routes_not_found': 0,
            'avg_lookup_time': 0,
            'lookup_times': [],
            'last_hour_requests': defaultdict(int)
        }
        self.start_time = time.time()
    
    def validate_ip(self, ip: str) -> Dict[str, any]:
        """
        Валидация IP-адреса
        Проверяет: формат, приватность, корректность
        """
        import ipaddress
        
        result = {
            'ip': ip,
            'is_valid': False,
            'is_private': False,
            'is_loopback': False,
            'is_multicast': False,
            'version': None,
            'error': None
        }
        
        try:
            addr = ipaddress.ip_address(ip)
            result['is_valid'] = True
            result['version'] = addr.version
            
            # Проверка приватности
            if addr.is_private:
                result['is_private'] = True
            if addr.is_loopback:
                result['is_loopback'] = True
            if addr.is_multicast:
                result['is_multicast'] = True
                
        except ValueError as e:
            result['error'] = str(e)
        
        return result
    
    def log_lookup(self, ip: str, route_found: bool, lookup_time: float):
        """
        Логирование операции поиска маршрута
        """
        # Валидация IP
        validation = self.validate_ip(ip)
        
        # Обновляем статистику
        self.stats['total_lookups'] += 1
        self.stats['lookup_times'].append(lookup_time)
        
        if validation['is_valid']:
            self.stats['valid_ips'] += 1
            if validation['is_private']:
                self.stats['private_ips'] += 1
            else:
                self.stats['public_ips'] += 1
        else:
            self.stats['invalid_ips'] += 1
        
        if route_found:
            self.stats['routes_found'] += 1
        else:
            self.stats['routes_not_found'] += 1
        
        # Добавляем в лог
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'ip': ip,
            'route_found': route_found,
            'lookup_time_us': round(lookup_time, 2),
            'validation': validation
        }
        self.logs.append(log_entry)
        
        # Ограничиваем размер лога
        if len(self.logs) > 1000:
            self.logs = self.logs[-1000:]
    
    def get_stats_report(self) -> Dict:
        """
        Формирует отчёт по статистике
        """
        import statistics
        
        uptime = time.time() - self.start_time
        
        # Вычисляем среднее время
        times = self.stats.get('lookup_times', [])
        avg_time = statistics.mean(times) if times else 0
        
        return {
            'uptime_seconds': round(uptime, 2),
            'total_lookups': self.stats['total_lookups'],
            'valid_ips': self.stats['valid_ips'],
            'invalid_ips': self.stats['invalid_ips'],
            'private_ips': self.stats['private_ips'],
            'public_ips': self.stats['public_ips'],
            'routes_found': self.stats['routes_found'],
            'routes_not_found': self.stats['routes_not_found'],
            'avg_lookup_time_us': round(avg_time, 2),
            'success_rate': round(
                self.stats['routes_found'] / self.stats['total_lookups'] * 100 
                if self.stats['total_lookups'] > 0 else 0, 2
            ),
            'log_size': len(self.logs)
        }
    
    def save_logs(self, filename: str = "validation_logs.json"):
        """
        Сохраняет логи в JSON файл
        """
        output = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.get_stats_report(),
            'last_100_logs': self.logs[-100:]  # Последние 100 записей
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def print_report(self):
        """
        Выводит отчёт о работе
        """
        stats = self.get_stats_report()
        
        print("\n" + "="*50)
        print(" 📊 ОТЧЁТ ВАЛИДАЦИИ И ЖУРНАЛИРОВАНИЯ")
        print("="*50)
        print(f"  Время работы: {stats['uptime_seconds']} сек")
        print(f"  Всего запросов: {stats['total_lookups']}")
        print(f"   Валидных IP: {stats['valid_ips']}")
        print(f"   Невалидных IP: {stats['invalid_ips']}")
        print(f"   Приватных IP: {stats['private_ips']}")
        print(f"   Публичных IP: {stats['public_ips']}")
        print(f"   Маршрутов найдено: {stats['routes_found']}")
        print(f"   Маршрутов не найдено: {stats['routes_not_found']}")
        print(f"   Среднее время: {stats['avg_lookup_time_us']} мкс")
        print(f"   Успешность: {stats['success_rate']}%")
        print("="*50)


class LoggerModule(Module):
    """
    Модуль журналирования и валидации
    Зависит от маршрутизатора (перехватывает вызовы)
    """
    
    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="logger",
            version="1.0.0",
            contract_version="1.0",
            description="Модуль валидации IP и журналирования операций"
        )
    
    @property
    def requires(self) -> list:
        # Зависит от линейного маршрутизатора (можно перехватывать вызовы)
        return ["linear_router"]
    
    def register_services(self, container: DIContainer) -> None:
        """Регистрирует сервис валидации и журналирования"""
        logger = ValidationLogger()
        container.register_singleton(ValidationLogger, logger)
        print("  [LoggerModule] Зарегистрирован ValidationLogger")
    
    def init(self, container: DIContainer) -> None:
        """Инициализация модуля"""
        logger = container.get(ValidationLogger)
        
        # Демонстрация работы валидации
        print("\n  [LoggerModule] Демонстрация валидации IP:")
        
        test_ips = [
            "192.168.1.100",    # приватный
            "8.8.8.8",          # публичный (Google DNS)
            "127.0.0.1",        # loopback
            "224.0.0.1",        # multicast
            "invalid_ip",       # невалидный
            "256.256.256.256"   # невалидный
        ]
        
        for ip in test_ips:
            result = logger.validate_ip(ip)
            status = "✅" if result['is_valid'] else "❌"
            details = []
            if result.get('is_private'):
                details.append("приватный")
            if result.get('is_loopback'):
                details.append("loopback")
            if result.get('is_multicast'):
                details.append("multicast")
            
            detail_str = f" ({', '.join(details)})" if details else ""
            print(f"    {status} {ip} → {'валидный' if result['is_valid'] else 'НЕВАЛИДНЫЙ'}{detail_str}")
        
        # Демонстрация логирования
        print("\n  [LoggerModule] Демонстрация логирования:")
        
        # Симулируем несколько запросов
        sample_ips = ["10.0.0.1", "192.168.1.5", "8.8.4.4", "172.16.0.1"]
        for ip in sample_ips:
            logger.log_lookup(ip, route_found=True, lookup_time=2.5)
        
        # Выводим отчёт
        logger.print_report()
        
        # Сохраняем логи
        log_file = logger.save_logs()
        print(f"\n  📁 Логи сохранены в: {log_file}")
        
        print("\n  [LoggerModule] Инициализация завершена")