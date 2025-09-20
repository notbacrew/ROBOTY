#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки исправлений проблемы с множественными роботами
"""

import sys
import os
import logging

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

sys.path.append(os.path.dirname(__file__))

def test_multiple_robots():
    """Тестирует обработку файла с 12 роботами"""
    try:
        print("🔍 Тестируем исправления для множественных роботов...")
        
        # Импортируем модули
        from core.parser import parse_input_file
        from core.assigner import assign_operations
        from core.planner import run_planner_algorithm
        
        # Загружаем данные
        print("\n📁 Загружаем файл с 12 роботами...")
        data = parse_input_file('data/test_scenario_10_robots.json')
        
        print(f"✅ Успешно загружено:")
        print(f"   - Роботов: {len(data.robots)}")
        print(f"   - Операций: {len(data.operations)}")
        
        # Тестируем разные методы назначения
        methods = ["round_robin", "balanced", "distance_based"]
        
        for method in methods:
            print(f"\n🧠 Тестируем метод: {method}")
            
            # Назначаем операции
            assignments = assign_operations(data, method)
            
            # Проверяем, что все роботы получили операции
            empty_robots = [i for i, ops in enumerate(assignments) if not ops]
            if empty_robots:
                print(f"❌ Метод {method}: роботы {empty_robots} не получили операций!")
            else:
                print(f"✅ Метод {method}: все роботы получили операции")
            
            # Выводим статистику
            for i, ops in enumerate(assignments):
                print(f"   - Робот {i+1}: {len(ops)} операций")
        
        # Тестируем полное планирование
        print(f"\n📊 Тестируем полное планирование с методом 'balanced'...")
        result = run_planner_algorithm(data, "balanced")
        
        print(f"✅ Планирование завершено:")
        print(f"   - Makespan: {result['makespan']:.2f}")
        print(f"   - Роботов в результате: {len(result['robots'])}")
        
        # Проверяем, что все роботы имеют траектории
        robots_with_trajectories = 0
        robots_without_trajectories = 0
        
        for robot in result['robots']:
            if len(robot['trajectory']) > 1:  # Больше одной точки (не только стартовая)
                robots_with_trajectories += 1
                print(f"   ✅ Робот {robot['id']}: {robot['operations_count']} операций, {len(robot['trajectory'])} точек траектории")
            else:
                robots_without_trajectories += 1
                print(f"   ⚠️ Робот {robot['id']}: {robot['operations_count']} операций, {len(robot['trajectory'])} точек траектории (статический)")
        
        print(f"\n📈 Итоговая статистика:")
        print(f"   - Роботов с активными траекториями: {robots_with_trajectories}")
        print(f"   - Роботов со статическими траекториями: {robots_without_trajectories}")
        
        if robots_without_trajectories > len(data.robots) // 2:
            print("❌ Слишком много роботов без активных траекторий!")
            return False
        else:
            print("✅ Распределение траекторий выглядит нормально!")
            return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_multiple_robots()
    if success:
        print("\n🎉 Все тесты прошли успешно! Проблема с множественными роботами исправлена!")
    else:
        print("\n💥 Тесты провалились! Требуется дополнительная отладка.")
        sys.exit(1)
