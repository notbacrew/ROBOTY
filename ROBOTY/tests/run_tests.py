#!/usr/bin/env python3
"""
Скрипт для запуска всех тестов проекта ROBOTY.
"""
import sys
import os
import unittest
import logging

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Настройка логирования для тестов
logging.basicConfig(
    level=logging.WARNING,  # Минимальный уровень для тестов
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 60)
    print("ЗАПУСК ТЕСТОВ ROBOTY")
    print("=" * 60)
    
    # Загружаем все тесты
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим результаты
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    print(f"Запущено тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Ошибок: {len(result.errors)}")
    print(f"Провалов: {len(result.failures)}")
    
    if result.failures:
        print("\nПРОВАЛЕННЫЕ ТЕСТЫ:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print("\nОШИБКИ В ТЕСТАХ:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('\\n')[-2]}")
    
    # Возвращаем код выхода
    return 0 if result.wasSuccessful() else 1

def run_specific_test(test_name):
    """Запуск конкретного теста"""
    print(f"Запуск теста: {test_name}")
    
    # Импортируем нужный модуль
    try:
        if test_name == "parser":
            from tests.test_parser import TestJsonParser, TestTxtParser
            suite = unittest.TestLoader().loadTestsFromTestCase(TestJsonParser)
            suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTxtParser))
        elif test_name == "planner":
            from tests.test_planner import TestKinematics, TestVelocityProfile, TestTrajectoryGeneration, TestRobotTrajectoryPlanning, TestMakespanCalculation, TestPlannerAlgorithm
            suite = unittest.TestSuite()
            for test_class in [TestKinematics, TestVelocityProfile, TestTrajectoryGeneration, TestRobotTrajectoryPlanning, TestMakespanCalculation, TestPlannerAlgorithm]:
                suite.addTests(unittest.TestLoader().loadTestsFromTestCase(test_class))
        elif test_name == "collision":
            from tests.test_collision import TestCollisionUtils, TestCollisionDetection, TestStaticObstacles, TestCollisionSummary
            suite = unittest.TestSuite()
            for test_class in [TestCollisionUtils, TestCollisionDetection, TestStaticObstacles, TestCollisionSummary]:
                suite.addTests(unittest.TestLoader().loadTestsFromTestCase(test_class))
        else:
            print(f"Неизвестный тест: {test_name}")
            return 1
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return 0 if result.wasSuccessful() else 1
        
    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Запуск конкретного теста
        test_name = sys.argv[1]
        exit_code = run_specific_test(test_name)
    else:
        # Запуск всех тестов
        exit_code = run_all_tests()
    
    sys.exit(exit_code)
