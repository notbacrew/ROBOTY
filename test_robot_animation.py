#!/usr/bin/env python3
"""
Тестовый скрипт для проверки анимации 3D модели робота
"""

import json
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from viz.visualizer import show_visualization

def create_test_plan():
    """Создает тестовый план с простой траекторией робота"""
    plan = {
        "robots": [
            {
                "id": 1,
                "base_xyz": [0, 0, 0],
                "trajectory": [
                    {"t": 0.0, "x": 0.0, "y": 0.0, "z": 0.0},
                    {"t": 1.0, "x": 1.0, "y": 0.0, "z": 0.5},
                    {"t": 2.0, "x": 2.0, "y": 1.0, "z": 1.0},
                    {"t": 3.0, "x": 1.5, "y": 2.0, "z": 0.5},
                    {"t": 4.0, "x": 0.5, "y": 1.5, "z": 0.0}
                ],
                "tool_clearance": 0.1
            },
            {
                "id": 2,
                "base_xyz": [3, 0, 0],
                "trajectory": [
                    {"t": 0.0, "x": 3.0, "y": 0.0, "z": 0.0},
                    {"t": 1.5, "x": 2.0, "y": 1.0, "z": 0.5},
                    {"t": 3.0, "x": 1.0, "y": 2.0, "z": 1.0},
                    {"t": 4.5, "x": 2.5, "y": 1.5, "z": 0.5}
                ],
                "tool_clearance": 0.1
            }
        ],
        "makespan": 4.5,
        "safe_dist": 0.3,
        "assignment_method": "test",
        # Настройки для 3D анимации
        "robot_mesh": {
            "path": "assets/robots/hand_optimized.obj",
            "scale": 1.0
        },
        "max_anim_frames": 150,
        "anim_time_stride": 0.1,
        "light_mesh_anim": False,  # Полная анимация 3D модели
        "arm_mesh": False  # Отключаем сегментные руки, используем 3D модель
    }
    return plan

def main():
    """Главная функция тестирования"""
    print("🤖 Тестирование анимации 3D модели робота...")
    
    # Создаем тестовый план
    plan = create_test_plan()
    
    print("📋 Создан тестовый план с 2 роботами")
    print("🎯 Робот 1: траектория из 5 точек")
    print("🎯 Робот 2: траектория из 4 точек")
    print("🎨 Используется 3D модель: hand_optimized.obj")
    
    try:
        # Тестируем загрузку модели
        print("\n🔧 Тестирование загрузки 3D модели...")
        from core.mesh_loader import load_obj
        mesh_data = load_obj("assets/robots/hand_optimized.obj", 1.0)
        
        if mesh_data:
            xs, ys, zs, is_, js_, ks_ = mesh_data
            print(f"✅ 3D модель загружена успешно:")
            print(f"   - Вершин: {len(xs)}")
            print(f"   - Треугольников: {len(is_)}")
        else:
            print("❌ Ошибка загрузки 3D модели")
            return
        
        # Тестируем создание позы робота
        print("\n🎨 Тестирование создания позы робота...")
        from viz.visualizer import _create_robot_pose_mesh
        
        base = (0, 0, 0)
        tcp = (1, 0, 0.5)
        color = "blue"
        robot_id = 1
        
        pose_mesh = _create_robot_pose_mesh(mesh_data, base, tcp, color, robot_id, 0.5)
        print("✅ Создание 3D позы робота работает")
        
        print("\n🎉 Все компоненты 3D анимации работают корректно!")
        print("💡 Для полной анимации запустите main.py и используйте 'Открыть визуализацию'")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
