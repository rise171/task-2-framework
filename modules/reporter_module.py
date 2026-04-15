import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.contract import Module, ModuleInfo
from core.container import DIContainer
from datetime import datetime

class ReporterModule(Module):
    """Модуль для формирования отчётов о маршрутизации"""
    
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
        return ["linear_router"]  # Зависит от любого маршрутизатора
    
    def register_services(self, container: DIContainer) -> None:
        """Регистрирует сервис отчётности"""
        container.register_singleton(Reporter, Reporter())
        print("  [ReporterModule] Зарегистрирован Reporter как синглтон")
    
    def init(self, container: DIContainer) -> None:
        """Инициализирует отчётность"""
        reporter = container.get(Reporter)
        reporter.generate_report()
        print("  [ReporterModule] Отчёт сгенерирован")

class Reporter:
    """Сервис для генерации отчётов"""
    
    def generate_report(self) -> str:
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