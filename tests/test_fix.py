#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Временный файл для тестирования исправлений
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.parser import parse_input_file
from core.planner import run_planner_algorithm
from core.collision import check_collisions
from viz.visualizer import show_visualization

def test_basic_functionality():
    """Тест базовой функциональности"""
    print("🧪 Тестирование базовой функциональности...")
    
    try:
        # Тест парсинга
        print("1. Тест парсинга...")
        scenario = parse_input_file("data/test_scenario_simple.json")
        print("   ✅ Парсинг успешен")
        
        # Тест планирования
        print("2. Тест планирования...")
        plan = run_planner_algorithm(scenario)
        print("   ✅ Планирование успешно")
        
        # Тест проверки коллизий
        print("3. Тест проверки коллизий...")
        collisions = check_collisions(plan)
        print(f"   ✅ Обнаружено {len(collisions)} коллизий")
        
        print("🎉 Все тесты прошли успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_ui_import():
    """Тест импорта UI"""
    print("🧪 Тестирование импорта UI...")
    
    try:
        from ui_files.main_window_improved import Ui_MainWindow
        print("   ✅ UI импорт успешен")
        
        from main import MainApp
        print("   ✅ MainApp импорт успешен")
        
        print("🎉 UI тесты прошли успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка UI: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестов исправлений...")
    print("=" * 50)
    
    # Тест базовой функциональности
    basic_ok = test_basic_functionality()
    print()
    
    # Тест UI
    ui_ok = test_ui_import()
    print()
    
    # Итоговый результат
    print("=" * 50)
    if basic_ok and ui_ok:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        sys.exit(0)
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        sys.exit(1)
