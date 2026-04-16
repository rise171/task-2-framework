import sys
from pathlib import Path
from datetime import datetime

# Добавляем корневую директорию в путь для абсолютного импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.contract import Module, ModuleInfo
from core.container import DIContainer


class Reporter:
    """Сервис формирования отчётов"""
    
    def generate_report(self):
        report = f"""
        ========================================
        ОТЧЁТ О МАРШРУТИЗАЦИИ
        Время: {datetime.now()}
        ========================================
        
        Состояние системы: OK
        Модули загружены: линейный маршрутизатор, репортёр
        
        ========================================
        """
        print(report)
        return report


class ReporterModule(Module):
    """Модуль формирования отчётов"""
    
    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="reporter",
            version="1.0.0",
            contract_version="1.0",
            description="Модуль формирования отчётов"
        )
    
    @property
    def requires(self) -> list:
        return ["linear_router"]
    
    def register_services(self, container: DIContainer) -> None:
        """Регистрация сервиса Reporter"""
        container.register_singleton(Reporter, Reporter())
        print("  [ReporterModule] Зарегистрирован Reporter")
    
    def init(self, container: DIContainer) -> None:
        """Инициализация модуля - генерация отчёта"""
        reporter = container.get(Reporter)
        reporter.generate_report()
        print("  [ReporterModule] Отчёт сгенерирован")