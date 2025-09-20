#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест для проверки работоспособности ROBOTY
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Тест импортов основных модулей"""
    try:
        from core.parser import parse_input_file
        from core.planner import run_planner_algorithm
        from core.collision import check_collisions
        from viz.visualizer import show_visualization
        print("✅ Все импорты успешны")
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_basic_functionality():
    """Тест базовой функциональности"""
    try:
        from core.parser import parse_input_file
        from core.planner import run_planner_algorithm
        
        # Тест с простым сценарием
        scenario = parse_input_file("data/test_scenario_simple.json")
        plan = run_planner_algorithm(scenario)
        
        print("✅ Базовая функциональность работает")
        return True
    except Exception as e:
        print(f"❌ Ошибка функциональности: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Простой тест ROBOTY...")
    print("=" * 40)
    
    # Тест импортов
    imports_ok = test_imports()
    print()
    
    # Тест функциональности
    if imports_ok:
        functionality_ok = test_basic_functionality()
        print()
        
        if functionality_ok:
            print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        else:
            print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
    else:
        print("❌ ОШИБКИ ИМПОРТА")
