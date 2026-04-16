#!/usr/bin/env python3
"""
Мини веб служба и конвейер обработки запросов
Модульная архитектура с DI контейнером
"""

import sys
import argparse
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from core.container import DIContainer
from core.module_manager import ModuleManager
from core.exception import ModuleNotFoundError, CircularDependencyError, VersionMismatchError

def print_banner():
    """Печатает баннер приложения"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     МИНИ ВЕБ СЛУЖБА И КОНВЕЙЕР ОБРАБОТКИ ЗАПРОСОВ            ║
    ║     Модульная архитектура с DI контейнером                   ║
    ║     Версия: 1.0                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def run_framework(config_path: str, modules_dir: str = "modules"):
    """
    Запускает фреймворк с указанной конфигурацией
    """
    print_banner()
    
    # Создаём DI контейнер
    container = DIContainer()
    
    # Создаём менеджер модулей
    module_manager = ModuleManager(container, modules_dir)
    
    try:
        # Загружаем модули из конфигурации
        print(f"\n Загрузка модулей из конфигурации: {config_path}")
        module_manager.load_from_config(config_path)
        
        # Дополнительно загружаем модули из директории
        print(f" Поиск модулей в директории: {modules_dir}")
        module_manager.load_from_directory(modules_dir)
        
        # Выводим загруженные модули
        print(f"\n Загружено модулей: {len(module_manager.modules)}")
        for name, module in module_manager.modules.items():
            print(f"   - {name} v{module.info.version} (требует: {module.requires})")
        
        # Определяем порядок запуска
        print(f"\n Определение порядка запуска...")
        order = module_manager.resolve_order()
        print(f"   Порядок: {' -> '.join(order)}")
        
        # Регистрируем службы
        print(f"\n Регистрация служб в DI контейнере...")
        module_manager.register_all_services()
        
        # Инициализируем модули
        print(f"\n Инициализация модулей...")
        module_manager.init_all_modules()
        
        print(f"\n Фреймворк успешно запущен!")
        
    except ModuleNotFoundError as e:
        print(f"\n ОШИБКА: {e}")
        sys.exit(1)
    except CircularDependencyError as e:
        print(f"\n ОШИБКА: {e}")
        sys.exit(1)
    except VersionMismatchError as e:
        print(f"\n ОШИБКА: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n НЕОЖИДАННАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Модульный фреймворк с DI контейнером")
    parser.add_argument(
        "--config", "-c",
        default="config.yaml",
        help="Путь к конфигурационному файлу (по умолчанию: config.yaml)"
    )
    parser.add_argument(
        "--modules-dir", "-m",
        default="modules",
        help="Директория с модулями (по умолчанию: modules)"
    )
    
    args = parser.parse_args()
    run_framework(args.config, args.modules_dir)

if __name__ == "__main__":
    main()