import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.contract import Module, ModuleInfo
from core.container import DIContainer
from datetime import datetime

class ExporterModule(Module):
    """Модуль для экспорта данных в JSON"""
    
    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="exporter",
            version="1.0.0",
            contract_version="1.0",
            description="Модуль экспорта данных"
        )
    
    @property
    def requires(self) -> list:
        return ["reporter"]  # Зависит от модуля репортёра
    
    def register_services(self, container: DIContainer) -> None:
        """Регистрирует сервис экспорта"""
        container.register_singleton(Exporter, Exporter())
        print("  [ExporterModule] Зарегистрирован Exporter как синглтон")
    
    def init(self, container: DIContainer) -> None:
        """Экспортирует данные"""
        exporter = container.get(Exporter)
        exporter.export_to_json()
        print("  [ExporterModule] Данные экспортированы в JSON")

class Exporter:
    """Сервис для экспорта данных"""
    
    def export_to_json(self) -> None:
        data = {
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "modules": ["linear_router", "reporter", "exporter"],
            "message": "Данные успешно экспортированы"
        }
        
        with open("export_result.json", "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"  [Exporter] Данные сохранены в export_result.json")