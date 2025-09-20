#!/usr/bin/env python3
"""
Скрипт для тестирования приложения ROBOTY без GUI.
"""
import sys
import os
import logging

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.parser import parse_input
from core.planner import run_planner_algorithm
from core.collision import check_collisions_detailed, get_collision_summary
from viz.visualizer import show_visualization

def setup_test_logging():
    """Настройка логирования для тестов"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_file(file_path):
    """Тестирование конкретного файла"""
    print(f"\n{'='*60}")
    print(f"ТЕСТИРОВАНИЕ ФАЙЛА: {file_path}")
    print(f"{'='*60}")
    
    try:
        # 1. Загрузка файла
        print("1. Загрузка файла...")
        scenario = parse_input(file_path)
        print(f"   ✅ Файл загружен успешно")
        print(f"   📊 Роботов: {len(scenario.robots)}")
        print(f"   📊 Операций: {len(scenario.operations)}")
        print(f"   📊 Безопасное расстояние: {scenario.safe_dist}")
        
        # 2. Планирование
        print("\n2. Планирование траекторий...")
        plan = run_planner_algorithm(scenario, assignment_method="balanced")
        print(f"   ✅ Планирование завершено")
        print(f"   ⏱️  Makespan: {plan['makespan']:.2f} сек")
        print(f"   🤖 Роботов в плане: {len(plan['robots'])}")
        
        # 3. Проверка коллизий
        print("\n3. Проверка коллизий...")
        collisions = check_collisions_detailed(plan)
        if collisions:
            summary = get_collision_summary(collisions)
            print(f"   ⚠️  Обнаружено {len(collisions)} коллизий")
            print(f"   📊 Затронуто роботов: {summary['affected_robots']}")
        else:
            print(f"   ✅ Коллизий не обнаружено")
        
        # 4. Визуализация
        print("\n4. Создание визуализации...")
        try:
            show_visualization(plan, "3d")
            print(f"   ✅ 3D визуализация создана")
        except Exception as e:
            print(f"   ⚠️  Ошибка 3D визуализации: {e}")
        
        try:
            show_visualization(plan, "2d_xy")
            print(f"   ✅ 2D визуализация создана")
        except Exception as e:
            print(f"   ⚠️  Ошибка 2D визуализации: {e}")
        
        print(f"\n✅ ТЕСТ ФАЙЛА {file_path} ЗАВЕРШЕН УСПЕШНО")
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА В ТЕСТЕ {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Главная функция тестирования"""
    setup_test_logging()
    
    print("🤖 ТЕСТИРОВАНИЕ ПРИЛОЖЕНИЯ ROBOTY")
    print("="*60)
    
    # Список файлов для тестирования
    test_files = [
        "data/test_scenario_simple.json",
        "data/test_scenario_complex.json", 
        "data/example_schedule.json",
        "data/test_scenario_collision.txt"
    ]
    
    successful_tests = 0
    total_tests = 0
    
    for test_file_path in test_files:
        full_path = os.path.join(os.path.dirname(__file__), test_file_path)
        if os.path.exists(full_path):
            total_tests += 1
            if test_file(full_path):
                successful_tests += 1
        else:
            print(f"\n⚠️  Файл не найден: {full_path}")
    
    # Итоговый отчет
    print(f"\n{'='*60}")
    print("ИТОГОВЫЙ ОТЧЕТ")
    print(f"{'='*60}")
    print(f"Всего тестов: {total_tests}")
    print(f"Успешных: {successful_tests}")
    print(f"Неудачных: {total_tests - successful_tests}")
    
    if successful_tests == total_tests:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        return 0
    else:
        print("⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        return 1

if __name__ == "__main__":
    sys.exit(main())
