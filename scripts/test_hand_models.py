#!/usr/bin/env python3
"""
Тестовый скрипт для проверки загрузки и производительности моделей руки
"""

import os
import sys
import time
from typing import List, Tuple

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.mesh_loader import load_obj
except ImportError:
    print("Ошибка: не удалось импортировать mesh_loader")
    sys.exit(1)

def test_model_loading(filepath: str) -> Tuple[bool, int, int, float]:
    """
    Тестирует загрузку модели и возвращает результаты
    """
    if not os.path.exists(filepath):
        return False, 0, 0, 0.0
    
    start_time = time.time()
    result = load_obj(filepath)
    load_time = time.time() - start_time
    
    if result is None:
        return False, 0, 0, load_time
    
    xs, ys, zs, is_, js_, ks_ = result
    vertex_count = len(xs)
    face_count = len(is_)
    
    return True, vertex_count, face_count, load_time

def main():
    """Основная функция тестирования"""
    print("🤖 Тестирование моделей руки-робота для ROBOTY")
    print("=" * 60)
    
    # Список моделей для тестирования
    models = [
        ("hand_ultra_simple.obj", "Ультра-простая модель"),
        ("hand_simple.obj", "Простая модель"),
        ("hand_optimized.obj", "Оптимизированная модель"),
        ("hand_auto_optimized.obj", "Авто-оптимизированная модель"),
        ("1758706684_68d3bbfcdbb32.obj", "Оригинальная модель")
    ]
    
    results = []
    
    for filename, description in models:
        filepath = os.path.join("assets", "robots", filename)
        print(f"\n📁 Тестируем: {description}")
        print(f"   Файл: {filepath}")
        
        success, vertices, faces, load_time = test_model_loading(filepath)
        
        if success:
            print(f"   ✅ Успешно загружена")
            print(f"   📊 Вершин: {vertices:,}")
            print(f"   📊 Граней: {faces:,}")
            print(f"   ⏱️  Время загрузки: {load_time:.3f} сек")
            
            # Оценка производительности
            if vertices < 100:
                perf = "🚀 Отличная"
            elif vertices < 500:
                perf = "⚡ Хорошая"
            elif vertices < 2000:
                perf = "⚠️  Средняя"
            else:
                perf = "🐌 Низкая"
            
            print(f"   🎯 Производительность: {perf}")
            
            results.append({
                'name': description,
                'file': filename,
                'vertices': vertices,
                'faces': faces,
                'load_time': load_time,
                'performance': perf
            })
        else:
            print(f"   ❌ Ошибка загрузки")
            results.append({
                'name': description,
                'file': filename,
                'vertices': 0,
                'faces': 0,
                'load_time': 0,
                'performance': "❌ Ошибка"
            })
    
    # Сводная таблица
    print("\n" + "=" * 60)
    print("📋 СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
    print("=" * 60)
    print(f"{'Модель':<25} {'Вершин':<10} {'Граней':<10} {'Время':<8} {'Производительность'}")
    print("-" * 60)
    
    for result in results:
        print(f"{result['name']:<25} {result['vertices']:<10,} {result['faces']:<10,} {result['load_time']:<8.3f} {result['performance']}")
    
    # Рекомендации
    print("\n" + "=" * 60)
    print("💡 РЕКОМЕНДАЦИИ ПО ВЫБОРУ МОДЕЛИ")
    print("=" * 60)
    
    working_models = [r for r in results if r['vertices'] > 0]
    
    if working_models:
        # Находим самую быструю модель
        fastest = min(working_models, key=lambda x: x['load_time'])
        print(f"🚀 Самая быстрая: {fastest['name']} ({fastest['load_time']:.3f} сек)")
        
        # Находим самую детальную модель
        most_detailed = max(working_models, key=lambda x: x['vertices'])
        print(f"🎨 Самая детальная: {most_detailed['name']} ({most_detailed['vertices']:,} вершин)")
        
        # Находим оптимальную модель (баланс детализации и производительности)
        optimal = min(working_models, key=lambda x: x['vertices'] * x['load_time'])
        print(f"⚖️  Оптимальная: {optimal['name']} (баланс детализации и производительности)")
    
    print("\n🎯 Рекомендации по использованию:")
    print("   • Для демонстрации: hand_optimized.obj")
    print("   • Для разработки: hand_simple.obj") 
    print("   • Для множества роботов: hand_ultra_simple.obj")
    print("   • Для презентаций: hand_auto_optimized.obj")
    print("   • Для максимальной детализации: 1758706684_68d3bbfcdbb32.obj")
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    main()
