class ModuleError(Exception):
    """Базовое исключение для модулей"""
    pass

class ModuleNotFoundError(ModuleError):
    """Модуль не найден"""
    def __init__(self, module_name: str, available_modules: list):
        self.module_name = module_name
        self.available_modules = available_modules
        super().__init__(
            f"Модуль '{module_name}' не найден. "
            f"Доступные модули: {available_modules if available_modules else 'нет'}"
        )

class CircularDependencyError(ModuleError):
    """Циклическая зависимость модулей"""
    def __init__(self, cycle: list):
        self.cycle = cycle
        cycle_str = " -> ".join(cycle + [cycle[0]])
        super().__init__(
            f"Обнаружена циклическая зависимость модулей: {cycle_str}\n"
            f"Проверьте зависимости модулей, чтобы разорвать цикл."
        )

class VersionMismatchError(ModuleError):
    """Несовместимая версия контракта"""
    def __init__(self, module_name: str, required_version: str, actual_version: str):
        super().__init__(
            f"Модуль '{module_name}' требует версию контракта {required_version}, "
            f"но фреймворк поддерживает {actual_version}"
        )