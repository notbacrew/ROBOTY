#!/usr/bin/env python3
import json

# Простой тест загрузки JSON
try:
    print("Загружаем JSON файл...")
    with open('data/test_scenario_10_robots.json', 'r') as f:
        data = json.load(f)
    
    print(f"Роботов в файле: {len(data['robots'])}")
    print(f"Операций в файле: {len(data['operations'])}")
    
    for i, robot in enumerate(data['robots']):
        print(f"Робот {i+1}: ID={robot['id']}, base_xyz={robot['base_xyz']}")
        
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()
