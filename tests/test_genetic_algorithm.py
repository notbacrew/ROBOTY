#!/usr/bin/env python3
"""
Тесты для генетического алгоритма
"""
import unittest
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.genetic_algorithm import GeneticAlgorithm, assign_operations_genetic
from core.parser_txt import ScenarioTxt, RobotConfig, Operation

class TestGeneticAlgorithm(unittest.TestCase):
    """Тесты для генетического алгоритма"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        # Создаем простой сценарий для тестирования
        self.robots = [
            RobotConfig(
                base_xyz=(0, 0, 0),
                joint_limits=[(-180, 180), (-90, 90), (-90, 90)],
                vmax=1.0,
                amax=2.0,
                tool_clearance=0.1
            ),
            RobotConfig(
                base_xyz=(1, 0, 0),
                joint_limits=[(-180, 180), (-90, 90), (-90, 90)],
                vmax=1.2,
                amax=2.5,
                tool_clearance=0.15
            )
        ]
        
        self.operations = [
            Operation(
                pick_xyz=(0.5, 1, 0),
                place_xyz=(1.5, 1, 0.5),
                t_hold=0.5
            ),
            Operation(
                pick_xyz=(0.3, 0.5, 0),
                place_xyz=(1.3, 0.5, 0.3),
                t_hold=0.8
            )
        ]
        
        self.scenario = ScenarioTxt(
            robots=self.robots,
            safe_dist=0.3,
            operations=self.operations
        )
    
    def test_genetic_algorithm_initialization(self):
        """Тест инициализации генетического алгоритма"""
        ga = GeneticAlgorithm(population_size=20, generations=10)
        
        self.assertEqual(ga.population_size, 20)
        self.assertEqual(ga.generations, 10)
        self.assertEqual(ga.mutation_rate, 0.1)
        self.assertEqual(ga.crossover_rate, 0.8)
        self.assertIsNone(ga.best_individual)
    
    def test_population_initialization(self):
        """Тест инициализации популяции"""
        ga = GeneticAlgorithm(population_size=10, generations=5)
        ga.initialize_population(self.scenario)
        
        self.assertEqual(len(ga.population), 10)
        
        # Проверяем, что все операции назначены
        all_operations = set()
        for individual in ga.population:
            for robot_ops in individual.assignments:
                all_operations.update(robot_ops)
        
        expected_operations = set(range(len(self.operations)))
        self.assertEqual(all_operations, expected_operations)
    
    def test_fitness_evaluation(self):
        """Тест оценки приспособленности"""
        ga = GeneticAlgorithm(population_size=5, generations=2)
        ga.initialize_population(self.scenario)
        
        # Оцениваем приспособленность первого индивида
        individual = ga.population[0]
        fitness = ga.evaluate_fitness(individual, self.scenario)
        
        self.assertGreater(fitness, 0)
        self.assertGreater(individual.makespan, 0)
        self.assertEqual(individual.fitness, fitness)
    
    def test_genetic_algorithm_evolution(self):
        """Тест эволюции генетического алгоритма"""
        ga = GeneticAlgorithm(population_size=10, generations=5)
        best_individual = ga.evolve(self.scenario)
        
        self.assertIsNotNone(best_individual)
        self.assertGreater(best_individual.fitness, 0)
        self.assertGreater(best_individual.makespan, 0)
    
    def test_assign_operations_genetic(self):
        """Тест функции назначения операций генетическим алгоритмом"""
        assignments = assign_operations_genetic(self.scenario, population_size=10, generations=5)
        
        # Проверяем структуру результата
        self.assertEqual(len(assignments), len(self.robots))
        
        # Проверяем, что все операции назначены
        all_assigned_operations = set()
        for robot_ops in assignments:
            for op in robot_ops:
                # Используем индекс операции для идентификации
                op_index = self.operations.index(op)
                all_assigned_operations.add(op_index)
        
        expected_operations = set(range(len(self.operations)))
        self.assertEqual(all_assigned_operations, expected_operations)
    
    def test_genetic_algorithm_with_different_parameters(self):
        """Тест генетического алгоритма с разными параметрами"""
        # Тест с малыми параметрами
        ga_small = GeneticAlgorithm(population_size=5, generations=2)
        best_small = ga_small.evolve(self.scenario)
        
        # Тест с большими параметрами
        ga_large = GeneticAlgorithm(population_size=20, generations=10)
        best_large = ga_large.evolve(self.scenario)
        
        # Оба должны работать без ошибок
        self.assertIsNotNone(best_small)
        self.assertIsNotNone(best_large)
        
        # Результат с большими параметрами должен быть не хуже
        self.assertGreaterEqual(best_large.fitness, best_small.fitness)

if __name__ == '__main__':
    unittest.main()
