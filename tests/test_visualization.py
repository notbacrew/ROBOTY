#!/usr/bin/env python3
"""
Простой тест визуализации без GUI для проверки работы Plotly.
"""
import sys
import os
import logging

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.parser import parse_input
from core.planner import run_planner_algorithm
from viz.visualizer import show_visualization

def test_visualization():
    """Тест визуализации"""
    print("🧪 ТЕСТ ВИЗУАЛИЗАЦИИ ROBOTY")
    print("=" * 50)
    
    try:
        # Загружаем простой сценарий
        print("1. Загрузка тестового файла...")
        file_path = os.path.join(os.path.dirname(__file__), "data", "test_scenario_simple.json")
        scenario = parse_input(file_path)
        print(f"   ✅ Загружено {len(scenario.robots)} роботов, {len(scenario.operations)} операций")
        
        # Планируем
        print("\n2. Планирование...")
        plan = run_planner_algorithm(scenario)
        print(f"   ✅ Makespan: {plan['makespan']:.2f} сек")
        
        # Тестируем визуализацию
        print("\n3. Тестирование визуализации...")
        
        # 3D визуализация
        print("   📊 Создание 3D визуализации...")
        show_visualization(plan, "3d")
        print("   ✅ 3D визуализация создана")
        
        # 2D визуализация
        print("   📊 Создание 2D визуализации...")
        show_visualization(plan, "2d_xy")
        print("   ✅ 2D визуализация создана")
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("\n📁 HTML файлы созданы в папке ROBOTY")
        print("🌐 Откройте их в браузере для просмотра")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(level=logging.WARNING)  # Минимальное логирование
    
    success = test_visualization()
    sys.exit(0 if success else 1)
