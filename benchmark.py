"""
Единый бенчмарк для сравнения трёх алгоритмов маршрутизации:
1. Linear Router (O(N))
2. Trie Router (O(32))
3. Distance Vector Router (O(N))
"""

import time
import statistics
import sys
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent))

from generator import generate_routes, generate_ips
from linear_router import LinearRouter
from trie_router import TrieRouter
from distance_vector_router import SimpleDVRouter


def benchmark(router, ips):
    """Измеряет время выполнения lookup для каждого IP"""
    times = []
    
    for ip in ips:
        start = time.perf_counter()
        router.lookup(ip)
        end = time.perf_counter()
        times.append((end - start) * 1e6)  # микросекунды
    
    return times


def get_stats(times):
    """Вычисляет статистику: avg, p50, p95, p99"""
    times_sorted = sorted(times)
    
    return {
        "avg": round(statistics.mean(times), 2),
        "p50": round(times_sorted[int(len(times) * 0.5)], 2),
        "p95": round(times_sorted[int(len(times) * 0.95)], 2),
        "p99": round(times_sorted[int(len(times) * 0.99)], 2),
    }


def print_table(results):
    """Выводит результаты в виде таблицы"""
    print("\n" + "=" * 80)
    print(" СРАВНЕНИЕ АЛГОРИТМОВ МАРШРУТИЗАЦИИ")
    print("=" * 80)
    
    for size in results:
        print(f"\ КОЛИЧЕСТВО МАРШРУТОВ: {size}")
        print("-" * 80)
        print(f"{'Алгоритм':<18} {'avg (мкс)':<12} {'p50 (мкс)':<12} {'p95 (мкс)':<12} {'p99 (мкс)':<12} {'p99/avg':<10}")
        print("-" * 80)
        
        for algo_name, stats in results[size].items():
            p99_avg_ratio = round(stats['p99'] / stats['avg'], 2) if stats['avg'] > 0 else 0
            print(f"{algo_name:<18} {stats['avg']:<12} {stats['p50']:<12} {stats['p95']:<12} {stats['p99']:<12} {p99_avg_ratio:<10}")
        
        print("-" * 80)
        
        # Вычисляем ускорение
        linear_avg = results[size]['Linear']['avg']
        trie_avg = results[size]['Trie']['avg']
        dv_avg = results[size]['Distance Vector']['avg']
        
        print(f"\ Ускорение:")
        print(f"   Trie vs Linear:  {linear_avg / trie_avg:.1f}x быстрее")
        print(f"   DV vs Linear:    {linear_avg / dv_avg:.1f}x быстрее")
        print(f"   Trie vs DV:      {dv_avg / trie_avg:.1f}x быстрее")


def print_tail_analysis(results):
    """Анализ хвостов распределения"""
    print("\n" + "=" * 80)
    print(" АНАЛИЗ ХВОСТОВ РАСПРЕДЕЛЕНИЯ (Tail Latency)")
    print("=" * 80)
    
    for size in results:
        print(f"\n При {size} маршрутах:")
        print("-" * 50)
        
        for algo_name, stats in results[size].items():
            p99_avg_ratio = stats['p99'] / stats['avg']
            tail_quality = " отличные" if p99_avg_ratio < 1.5 else " средние" if p99_avg_ratio < 2 else "❌ плохие"
            
            print(f"   {algo_name}: p99/avg = {p99_avg_ratio:.2f} → {tail_quality} хвосты")
            
            if p99_avg_ratio > 2:
                print(f"       Каждый 100-й запрос выполняется в {p99_avg_ratio:.1f} раз дольше среднего!")


def print_conclusion(results):
    """Выводит итоговые выводы"""
    print("\n" + "=" * 80)
    print(" ВЫВОДЫ")
    print("=" * 80)
    
    # Берём результаты для максимального размера
    max_size = max(results.keys())
    linear = results[max_size]['Linear']
    trie = results[max_size]['Trie']
    dv = results[max_size]['Distance Vector']
    
    print(f"\n На основе тестов при {max_size} маршрутах:")
    print()
    print(f"   Линейный маршрутизатор:")
    print(f"      - Среднее время: {linear['avg']} мкс")
    print(f"      - Хвост (p99): {linear['p99']} мкс (в {linear['p99']/linear['avg']:.1f}x хуже среднего)")
    print(f"      - Вывод:  Не подходит для production при большом количестве маршрутов")
    
    print(f"\n    Trie-маршрутизатор:")
    print(f"      - Среднее время: {trie['avg']} мкс")
    print(f"      - Хвост (p99): {trie['p99']} мкс (в {trie['p99']/trie['avg']:.1f}x хуже среднего)")
    print(f"      - Ускорение: в {linear['avg']/trie['avg']:.0f}x быстрее Linear")
    print(f"      - Вывод:  Лучший выбор для production")
    
    print(f"\n    Distance Vector маршрутизатор:")
    print(f"      - Среднее время: {dv['avg']} мкс")
    print(f"      - Хвост (p99): {dv['p99']} мкс (в {dv['p99']/dv['avg']:.1f}x хуже среднего)")
    print(f"      - Ускорение: в {linear['avg']/dv['avg']:.0f}x быстрее Linear")
    print(f"      - вывод:  Хорош для распределённых сетей, но медленнее Trie")
    
    print("\n" + "=" * 80)
    print(" ИТОГОВАЯ РЕКОМЕНДАЦИЯ:")
    print("   Для production-систем с большим количеством маршрутов используйте Trie.")
    print("   Distance Vector подходит для небольших распределённых сетей (RIP).")
    print("   Linear применим только для прототипов или <100 маршрутов.")
    print("=" * 80)


def run_benchmark():
    """Запускает полный бенчмарк"""
    print("\n" + "=" * 80)
    print(" ЗАПУСК БЕНЧМАРКА ТРЁХ АЛГОРИТМОВ МАРШРУТИЗАЦИИ")
    print(" Linear | Trie | Distance Vector")
    print("=" * 80)
    
    sizes = [100, 1000, 5000]
    requests = 3000
    
    results = {}
    
    for size in sizes:
        print(f"\ Генерация {size} маршрутов и {requests} IP-адресов...")
        
        routes = generate_routes(size)
        ips = generate_ips(requests)
        
        results[size] = {}
        
        # === Linear Router ===
        print(f"    Тестирование Linear Router...")
        linear = LinearRouter()
        for r in routes:
            linear.add_route(r)
        linear_times = benchmark(linear, ips)
        results[size]['Linear'] = get_stats(linear_times)
        
        # === Trie Router ===
        print(f"    Тестирование Trie Router...")
        trie = TrieRouter()
        for r in routes:
            trie.add_route(r)
        trie_times = benchmark(trie, ips)
        results[size]['Trie'] = get_stats(trie_times)
        
        # === Distance Vector Router ===
        print(f"    Тестирование Distance Vector Router...")
        dv = SimpleDVRouter()
        for r in routes:
            dv.add_route(r)
        dv_times = benchmark(dv, ips)
        results[size]['Distance Vector'] = get_stats(dv_times)
    
    # Вывод результатов
    print_table(results)
    print_tail_analysis(results)
    print_conclusion(results)
    
    return results


def save_results_to_json(results, filename="benchmark_results.json"):
    """Сохраняет результаты в JSON файл"""
    import json
    from datetime import datetime
    
    output = {
        "timestamp": datetime.now().isoformat(),
        "algorithms": ["Linear", "Trie", "Distance Vector"],
        "requests_per_test": 3000,
        "results": {}
    }
    
    for size, algo_results in results.items():
        output["results"][str(size)] = algo_results
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n Результаты сохранены в {filename}")
    return filename


if __name__ == "__main__":
    results = run_benchmark()
    save_results_to_json(results)