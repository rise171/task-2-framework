#!/usr/bin/env python3
"""
Точка входа для запуска фреймворка с модульной архитектурой
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

def run_framework(config_path: str = None, modules_dir: str = "modules"):
    """
    Запускает фреймворк с указанной конфигурацией
    """
    print_banner()
    
    # Создаём DI контейнер
    container = DIContainer()
    
    # Создаём менеджер модулей
    module_manager = ModuleManager(container, modules_dir)
    
    try:
        # Загружаем модули из директории (если config не указан)
        print(f" Поиск модулей в директории: {modules_dir}")
        module_manager.load_from_directory()
        
        # Если есть конфиг, загружаем из него
        if config_path and Path(config_path).exists():
            print(f" Загрузка модулей из конфигурации: {config_path}")
            module_manager.load_from_config(config_path)
        
        # Выводим загруженные модули
        if module_manager.modules:
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
        else:
            print(f"\n Модули не найдены в директории {modules_dir}")
            print(f"   Создайте модули в папке modules/ или укажите config файл")
        
        return 0
        
    except ModuleNotFoundError as e:
        print(f"\n ОШИБКА: {e}")
        return 1
    except CircularDependencyError as e:
        print(f"\n ОШИБКА: {e}")
        return 1
    except VersionMismatchError as e:
        print(f"\n ОШИБКА: {e}")
        return 1
    except Exception as e:
        print(f"\n НЕОЖИДАННАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    parser = argparse.ArgumentParser(
        description="Модульный фреймворк с DI контейнером",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python run_framework.py                           # загрузка всех модулей из папки modules/
  python run_framework.py --config config.yaml      # загрузка из конфига
  python run_framework.py --modules-dir ./my_modules # указать другую папку с модулями
        """
    )
    parser.add_argument(
        "--config", "-c",
        default=None,
        help="Путь к конфигурационному файлу (опционально)"
    )
    parser.add_argument(
        "--modules-dir", "-m",
        default="modules",
        help="Директория с модулями (по умолчанию: modules)"
    )
    
    args = parser.parse_args()
    exit_code = run_framework(args.config, args.modules_dir)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()