#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест для проверки работоспособности
"""

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

if __name__ == "__main__":
    print("🧪 Простой тест...")
    test_imports()
