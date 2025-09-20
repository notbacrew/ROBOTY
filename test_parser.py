#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки парсинга файлов с большим количеством роботов
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from core.parser import parse_input_file
from core.assigner import assign_operations
from core.planner import run_planner_algorithm

def test_parsing():
    """Тестирует парсинг файла с 12 роботами"""
    try:
        print("🔍 Тестируем парсинг файла с 12 роботами...")
        
        # Загружаем данные
        data = parse_input_file('data/test_scenario_10_robots.json')
        
        print(f"✅ Успешно загружено:")
        print(f"   - Роботов: {len(data.robots)}")
        print(f"   - Операций: {len(data.operations)}")
        print(f"   - Safe distance: {data.safe_dist}")
        
        # Выводим ID роботов
        robot_ids = [r.id for r in data.robots]
        print(f"   - ID роботов: {robot_ids}")
        
        # Тестируем назначение операций
        print("\n🧠 Тестируем назначение операций...")
        assignments = assign_operations(data, "balanced")
        
        print(f"✅ Назначение завершено:")
        for i, ops in enumerate(assignments):
            print(f"   - Робот {i+1}: {len(ops)} операций")
        
        # Тестируем планирование траекторий
        print("\n📊 Тестируем планирование траекторий...")
        result = run_planner_algorithm(data, "balanced")
        
        print(f"✅ Планирование завершено:")
        print(f"   - Makespan: {result['makespan']:.2f}")
        print(f"   - Роботов в результате: {len(result['robots'])}")
        
        for robot in result['robots']:
            print(f"   - Робот {robot['id']}: {robot['operations_count']} операций, {len(robot['trajectory'])} точек траектории")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_parsing()
    if success:
        print("\n🎉 Все тесты прошли успешно!")
    else:
        print("\n💥 Тесты провалились!")
        sys.exit(1)
