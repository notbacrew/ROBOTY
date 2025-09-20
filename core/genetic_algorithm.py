import logging
import random
import math
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
from core.parser_txt import ScenarioTxt, RobotConfig, Operation

# Настройка логгера для модуля генетического алгоритма
logger = logging.getLogger("ROBOTY.genetic_algorithm")

@dataclass
class GeneticIndividual:
    """Индивид в генетическом алгоритме - представляет назначение операций роботам"""
    assignments: List[List[int]]  # Список операций для каждого робота
    fitness: float = 0.0
    makespan: float = 0.0

class GeneticAlgorithm:
    """Генетический алгоритм для оптимизации назначения операций роботам"""
    
    def __init__(self, population_size: int = 50, generations: int = 100, 
                 mutation_rate: float = 0.1, crossover_rate: float = 0.8):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.population: List[GeneticIndividual] = []
        self.best_individual: GeneticIndividual = None
        
        logger.info(f"Инициализирован генетический алгоритм: популяция={population_size}, поколения={generations}")
    
    def initialize_population(self, scenario: ScenarioTxt) -> None:
        """Инициализация начальной популяции случайными назначениями"""
        num_robots = len(scenario.robots)
        num_operations = len(scenario.operations)
        
        self.population = []
        
        for _ in range(self.population_size):
            # Случайное назначение операций роботам
            assignments = [[] for _ in range(num_robots)]
            operation_indices = list(range(num_operations))
            random.shuffle(operation_indices)
            
            for i, op_idx in enumerate(operation_indices):
                robot_idx = random.randint(0, num_robots - 1)
                assignments[robot_idx].append(op_idx)
            
            individual = GeneticIndividual(assignments=assignments)
            self.population.append(individual)
        
        logger.debug(f"Инициализирована популяция из {self.population_size} индивидов")
    
    def evaluate_fitness(self, individual: GeneticIndividual, scenario: ScenarioTxt) -> float:
        """Вычисляет приспособленность индивида (чем меньше makespan, тем лучше)"""
        try:
            # Создаем назначения операций для роботов
            robot_assignments = [[] for _ in range(len(scenario.robots))]
            
            for robot_idx, operation_indices in enumerate(individual.assignments):
                for op_idx in operation_indices:
                    if op_idx < len(scenario.operations):
                        robot_assignments[robot_idx].append(scenario.operations[op_idx])
            
            # Вычисляем makespan (максимальное время выполнения)
            max_time = 0.0
            
            for robot, operations in zip(scenario.robots, robot_assignments):
                robot_time = self._calculate_robot_time(robot, operations)
                max_time = max(max_time, robot_time)
            
            individual.makespan = max_time
            
            # Приспособленность - обратно пропорциональна makespan
            # Добавляем небольшое значение чтобы избежать деления на ноль
            fitness = 1.0 / (max_time + 0.001)
            individual.fitness = fitness
            
            return fitness
            
        except Exception as e:
            logger.error(f"Ошибка при вычислении приспособленности: {e}")
            individual.fitness = 0.0
            individual.makespan = float('inf')
            return 0.0
    
    def _calculate_robot_time(self, robot: RobotConfig, operations: List[Operation]) -> float:
        """Вычисляет время выполнения операций роботом"""
        if not operations:
            return 0.0
        
        total_time = 0.0
        current_pos = robot.base_xyz
        
        # Получаем максимальную скорость робота
        if isinstance(robot.vmax, list):
            max_speed = min(robot.vmax) if robot.vmax else 1.0
        else:
            max_speed = float(robot.vmax) if robot.vmax else 1.0
        
        for op in operations:
            # Время движения к точке pick
            dist_to_pick = math.sqrt(sum((p - c) ** 2 for p, c in zip(op.pick_xyz, current_pos)))
            time_to_pick = dist_to_pick / max_speed
            
            # Время движения от pick к place
            dist_pick_to_place = math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(op.place_xyz, op.pick_xyz)))
            time_pick_to_place = dist_pick_to_place / max_speed
            
            # Общее время операции
            operation_time = time_to_pick + time_pick_to_place + op.t_hold
            total_time += operation_time
            
            # Обновляем текущую позицию
            current_pos = op.place_xyz
        
        return total_time
    
    def selection(self) -> List[GeneticIndividual]:
        """Турнирная селекция"""
        tournament_size = 3
        selected = []
        
        for _ in range(self.population_size):
            # Выбираем случайных индивидов для турнира
            tournament = random.sample(self.population, min(tournament_size, len(self.population)))
            # Выбираем лучшего из турнира
            winner = max(tournament, key=lambda x: x.fitness)
            selected.append(winner)
        
        return selected
    
    def crossover(self, parent1: GeneticIndividual, parent2: GeneticIndividual, 
                  scenario: ScenarioTxt) -> Tuple[GeneticIndividual, GeneticIndividual]:
        """Одноточечное скрещивание"""
        if random.random() > self.crossover_rate:
            return parent1, parent2
        
        num_robots = len(scenario.robots)
        num_operations = len(scenario.operations)
        
        # Создаем потомков
        child1_assignments = [[] for _ in range(num_robots)]
        child2_assignments = [[] for _ in range(num_robots)]
        
        # Собираем все операции из родителей
        parent1_ops = set()
        parent2_ops = set()
        
        for robot_ops in parent1.assignments:
            parent1_ops.update(robot_ops)
        
        for robot_ops in parent2.assignments:
            parent2_ops.update(robot_ops)
        
        # Проверяем, что все операции присутствуют
        all_ops = set(range(num_operations))
        missing_ops = all_ops - parent1_ops
        if missing_ops:
            logger.warning(f"В родителе 1 отсутствуют операции: {missing_ops}")
            for op in missing_ops:
                parent1.assignments[0].append(op)
        
        missing_ops = all_ops - parent2_ops
        if missing_ops:
            logger.warning(f"В родителе 2 отсутствуют операции: {missing_ops}")
            for op in missing_ops:
                parent2.assignments[0].append(op)
        
        # Одноточечное скрещивание
        crossover_point = random.randint(0, num_robots - 1)
        
        for i in range(num_robots):
            if i < crossover_point:
                child1_assignments[i] = parent1.assignments[i].copy()
                child2_assignments[i] = parent2.assignments[i].copy()
            else:
                child1_assignments[i] = parent2.assignments[i].copy()
                child2_assignments[i] = parent1.assignments[i].copy()
        
        child1 = GeneticIndividual(assignments=child1_assignments)
        child2 = GeneticIndividual(assignments=child2_assignments)
        
        return child1, child2
    
    def mutation(self, individual: GeneticIndividual, scenario: ScenarioTxt) -> None:
        """Мутация - перемещение случайной операции между роботами"""
        if random.random() > self.mutation_rate:
            return
        
        num_robots = len(scenario.robots)
        num_operations = len(scenario.operations)
        
        # Выбираем случайную операцию для перемещения
        all_operations = []
        for robot_idx, ops in enumerate(individual.assignments):
            for op_idx in ops:
                if op_idx < num_operations:
                    all_operations.append((robot_idx, op_idx))
        
        if not all_operations:
            return
        
        source_robot, op_to_move = random.choice(all_operations)
        
        # Удаляем операцию из исходного робота
        if op_to_move in individual.assignments[source_robot]:
            individual.assignments[source_robot].remove(op_to_move)
        
        # Добавляем операцию к случайному роботу
        target_robot = random.randint(0, num_robots - 1)
        individual.assignments[target_robot].append(op_to_move)
        
        # Сбрасываем приспособленность
        individual.fitness = 0.0
    
    def evolve(self, scenario: ScenarioTxt) -> GeneticIndividual:
        """Основной цикл эволюции"""
        logger.info("Начинаем эволюцию генетического алгоритма")
        
        # Инициализация популяции
        self.initialize_population(scenario)
        
        # Оценка начальной популяции
        for individual in self.population:
            self.evaluate_fitness(individual, scenario)
        
        # Находим лучшего индивида
        self.best_individual = max(self.population, key=lambda x: x.fitness)
        
        # Основной цикл эволюции
        for generation in range(self.generations):
            # Селекция
            selected = self.selection()
            
            # Создание нового поколения
            new_population = []
            
            # Элитизм - сохраняем лучшего индивида
            new_population.append(GeneticIndividual(
                assignments=[ops.copy() for ops in self.best_individual.assignments],
                fitness=self.best_individual.fitness,
                makespan=self.best_individual.makespan
            ))
            
            # Скрещивание и мутация
            while len(new_population) < self.population_size:
                parent1 = random.choice(selected)
                parent2 = random.choice(selected)
                
                child1, child2 = self.crossover(parent1, parent2, scenario)
                
                # Мутация
                self.mutation(child1, scenario)
                self.mutation(child2, scenario)
                
                # Оценка потомков
                self.evaluate_fitness(child1, scenario)
                self.evaluate_fitness(child2, scenario)
                
                new_population.extend([child1, child2])
            
            # Обрезаем популяцию до нужного размера
            new_population = new_population[:self.population_size]
            self.population = new_population
            
            # Обновляем лучшего индивида
            current_best = max(self.population, key=lambda x: x.fitness)
            if current_best.fitness > self.best_individual.fitness:
                self.best_individual = current_best
            
            # Логирование прогресса
            if generation % 10 == 0 or generation == self.generations - 1:
                logger.info(f"Поколение {generation}: лучшая приспособленность = {self.best_individual.fitness:.6f}, "
                           f"makespan = {self.best_individual.makespan:.2f}")
        
        logger.info(f"Эволюция завершена. Лучший makespan: {self.best_individual.makespan:.2f}")
        return self.best_individual

def assign_operations_genetic(scenario: ScenarioTxt, 
                            population_size: int = 50, 
                            generations: int = 100) -> List[List[Operation]]:
    """
    Назначение операций роботам с помощью генетического алгоритма.
    
    Args:
        scenario: Сценарий с роботами и операциями
        population_size: Размер популяции
        generations: Количество поколений
    
    Returns:
        Список операций для каждого робота
    """
    logger.info("Запуск генетического алгоритма для назначения операций")
    
    try:
        # Создаем и запускаем генетический алгоритм
        ga = GeneticAlgorithm(population_size=population_size, generations=generations)
        best_individual = ga.evolve(scenario)
        
        # Преобразуем результат в нужный формат
        robot_assignments = [[] for _ in range(len(scenario.robots))]
        
        for robot_idx, operation_indices in enumerate(best_individual.assignments):
            for op_idx in operation_indices:
                if op_idx < len(scenario.operations):
                    robot_assignments[robot_idx].append(scenario.operations[op_idx])
        
        logger.info(f"Генетический алгоритм завершен. Найдено назначение с makespan = {best_individual.makespan:.2f}")
        
        return robot_assignments
        
    except Exception as e:
        logger.error(f"Ошибка в генетическом алгоритме: {e}")
        # Fallback к сбалансированному назначению
        logger.info("Используем сбалансированное назначение как fallback")
        from core.assigner import assign_operations_balanced
        return assign_operations_balanced(scenario)
