"""
Запуск модульного фреймворка с конфигурацией
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.container import DIContainer
from core.module_manager import ModuleManager
from core.exception import ModuleNotFoundError, CircularDependencyError
from benchmark import run_benchmark


def print_banner():
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║     МИНИ ВЕБ СЛУЖБА И КОНВЕЙЕР ОБРАБОТКИ ЗАПРОСОВ                ║
    ║     Модульная архитектура с DI контейнером                       ║
    ║     Алгоритмы: Linear | Trie | Distance Vector                   ║
    ║     Версия: 2.0                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)


def run_framework(config_path: str = "config.yaml", run_bench: bool = True):
    print_banner()
    
    container = DIContainer()
    manager = ModuleManager(container, "modules")
    
    try:
        # Загрузка модулей
        print(f"\n Загрузка модулей из {config_path}")
        manager.load_from_config(config_path)
        manager.load_from_directory()
        
        print(f"\n Загружено модулей: {len(manager.modules)}")
        for name, module in manager.modules.items():
            print(f"   - {name} v{module.info.version} (требует: {module.requires})")
        
        # Определение порядка запуска
        print(f"\n Определение порядка запуска...")
        order = manager.resolve_order()
        print(f"   Порядок: {' → '.join(order)}")
        
        # Регистрация и инициализация
        print(f"\n Регистрация служб...")
        manager.register_all_services()
        
        print(f"\n Инициализация модулей...")
        manager.init_all_modules()
        
        # Запуск бенчмарка
        if run_bench:
            print(f"\n Запуск бенчмарка...")
            run_benchmark()
        
        print(f"\n✨ Фреймворк успешно запущен!")
        return 0
        
    except ModuleNotFoundError as e:
        print(f"\n ОШИБКА: {e}")
        return 1
    except CircularDependencyError as e:
        print(f"\n ОШИБКА: {e}")
        return 1
    except Exception as e:
        print(f"\n НЕОЖИДАННАЯ ОШИБКА: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-c", default="config.yaml")
    parser.add_argument("--no-benchmark", action="store_true")
    
    args = parser.parse_args()
    sys.exit(run_framework(args.config, not args.no_benchmark))


if __name__ == "__main__":
    main()