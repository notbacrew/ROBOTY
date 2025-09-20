import logging
import math
from typing import List, Tuple
from core.parser_txt import ScenarioTxt, Operation, RobotConfig

# Настройка логгера для модуля назначения
logger = logging.getLogger("ROBOTY.assigner")

def calculate_operation_cost(robot: RobotConfig, operation: Operation) -> float:
    """
    Вычисляет стоимость выполнения операции роботом.
    Учитывает расстояние до операции и характеристики робота.
    """
    # Расстояние от базы робота до точки pick
    dist_to_pick = math.sqrt(sum((p - b) ** 2 for p, b in zip(operation.pick_xyz, robot.base_xyz)))
    
    # Расстояние от pick до place
    dist_pick_to_place = math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(operation.place_xyz, operation.pick_xyz)))
    
    # Общее расстояние
    total_dist = dist_to_pick + dist_pick_to_place
    
    # Время выполнения с учетом максимальной скорости
    if isinstance(robot.vmax, list):
        max_speed = min(robot.vmax) if robot.vmax else 1.0
    else:
        max_speed = float(robot.vmax) if robot.vmax else 1.0
    time_cost = total_dist / max_speed + operation.t_hold
    
    return time_cost

def assign_operations_round_robin(scenario: ScenarioTxt) -> List[List[Operation]]:
    """
    Простейший алгоритм назначения: по очереди распределяет операции между роботами.
    Улучшенная версия с детальным логированием.
    """
    K = len(scenario.robots)
    assignments = [[] for _ in range(K)]
    
    for i, op in enumerate(scenario.operations):
        robot_idx = i % K  # по кругу
        assignments[robot_idx].append(op)
        logger.debug(f"Операция {i} назначена роботу {robot_idx}")
    
    logger.info(f"Распределено {len(scenario.operations)} операций между {K} роботами")
    
    # Выводим детальную статистику
    for i, ops in enumerate(assignments):
        logger.info(f"Робот {i}: {len(ops)} операций")
    
    return assignments

def assign_operations_balanced(scenario: ScenarioTxt) -> List[List[Operation]]:
    """
    Алгоритм назначения с балансировкой нагрузки.
    Назначает операции роботам с наименьшей текущей нагрузкой.
    Улучшенная версия с гарантией минимального количества операций на робота.
    """
    K = len(scenario.robots)
    assignments = [[] for _ in range(K)]
    robot_loads = [0.0] * K  # текущая нагрузка каждого робота
    
    # Если операций меньше чем роботов, сначала назначаем по одной операции каждому роботу
    if len(scenario.operations) <= K:
        logger.warning(f"Операций ({len(scenario.operations)}) меньше или равно количеству роботов ({K})")
        for i, op in enumerate(scenario.operations):
            assignments[i].append(op)
            robot_loads[i] += calculate_operation_cost(scenario.robots[i], op)
            logger.debug(f"Операция {i} назначена роботу {i} (принудительное назначение)")
        return assignments
    
    # Основной алгоритм балансировки
    for i, op in enumerate(scenario.operations):
        # Вычисляем стоимость операции для каждого робота
        costs = []
        for j, robot in enumerate(scenario.robots):
            cost = calculate_operation_cost(robot, op)
            total_cost = robot_loads[j] + cost
            costs.append((total_cost, j))
        
        # Выбираем робота с минимальной общей нагрузкой
        _, best_robot_idx = min(costs)
        assignments[best_robot_idx].append(op)
        
        # Обновляем нагрузку выбранного робота
        operation_cost = calculate_operation_cost(scenario.robots[best_robot_idx], op)
        robot_loads[best_robot_idx] += operation_cost
        
        logger.debug(f"Операция {i} назначена роботу {best_robot_idx} (нагрузка: {robot_loads[best_robot_idx]:.2f})")
    
    # Проверяем, что все роботы получили хотя бы одну операцию
    empty_robots = [i for i, ops in enumerate(assignments) if not ops]
    if empty_robots:
        logger.warning(f"Роботы {empty_robots} не получили операций. Применяем дополнительное распределение.")
        
        # Находим роботов с наибольшей нагрузкой
        max_load_robots = []
        max_load = max(robot_loads)
        for i, load in enumerate(robot_loads):
            if load == max_load:
                max_load_robots.append(i)
        
        # Перераспределяем операции от перегруженных роботов к незагруженным
        for empty_robot in empty_robots:
            if max_load_robots:
                # Берем робота с максимальной нагрузкой
                source_robot = max_load_robots[0]
                if len(assignments[source_robot]) > 1:  # Только если у него больше одной операции
                    # Перемещаем последнюю операцию
                    moved_op = assignments[source_robot].pop()
                    assignments[empty_robot].append(moved_op)
                    
                    # Обновляем нагрузки
                    moved_cost = calculate_operation_cost(scenario.robots[source_robot], moved_op)
                    robot_loads[source_robot] -= moved_cost
                    robot_loads[empty_robot] += moved_cost
                    
                    logger.debug(f"Операция перемещена от робота {source_robot} к роботу {empty_robot}")
    
    logger.info(f"Распределено {len(scenario.operations)} операций с балансировкой нагрузки")
    logger.info(f"Итоговые нагрузки роботов: {[f'{load:.2f}' for load in robot_loads]}")
    
    # Выводим детальную статистику
    for i, (ops, load) in enumerate(zip(assignments, robot_loads)):
        logger.info(f"Робот {i}: {len(ops)} операций, нагрузка {load:.2f}")
    
    return assignments

def assign_operations_distance_based(scenario: ScenarioTxt) -> List[List[Operation]]:
    """
    Алгоритм назначения на основе минимального расстояния.
    Назначает операции роботам, которые находятся ближе всего к точке pick.
    Улучшенная версия с балансировкой.
    """
    K = len(scenario.robots)
    assignments = [[] for _ in range(K)]
    robot_positions = [robot.base_xyz for robot in scenario.robots]
    
    # Если операций меньше чем роботов, сначала назначаем по одной операции каждому роботу
    if len(scenario.operations) <= K:
        logger.warning(f"Операций ({len(scenario.operations)}) меньше или равно количеству роботов ({K})")
        for i, op in enumerate(scenario.operations):
            assignments[i].append(op)
            robot_positions[i] = op.place_xyz  # Обновляем позицию
            logger.debug(f"Операция {i} назначена роботу {i} (принудительное назначение)")
        return assignments
    
    for i, op in enumerate(scenario.operations):
        # Вычисляем расстояние от каждого робота до точки pick
        distances = []
        for j, robot_pos in enumerate(robot_positions):
            dist = math.sqrt(sum((p - r) ** 2 for p, r in zip(op.pick_xyz, robot_pos)))
            distances.append((dist, j))
        
        # Выбираем робота с минимальным расстоянием
        _, best_robot_idx = min(distances)
        assignments[best_robot_idx].append(op)
        
        # Обновляем позицию робота (упрощенно - считаем, что робот переместился к place)
        robot_positions[best_robot_idx] = op.place_xyz
        
        logger.debug(f"Операция {i} назначена роботу {best_robot_idx} (расстояние: {distances[best_robot_idx][0]:.2f})")
    
    # Проверяем, что все роботы получили хотя бы одну операцию
    empty_robots = [i for i, ops in enumerate(assignments) if not ops]
    if empty_robots:
        logger.warning(f"Роботы {empty_robots} не получили операций. Применяем дополнительное распределение.")
        
        # Находим роботов с наибольшим количеством операций
        max_ops_count = max(len(ops) for ops in assignments)
        overloaded_robots = [i for i, ops in enumerate(assignments) if len(ops) == max_ops_count]
        
        # Перераспределяем операции от перегруженных роботов к незагруженным
        for empty_robot in empty_robots:
            if overloaded_robots:
                # Берем робота с максимальным количеством операций
                source_robot = overloaded_robots[0]
                if len(assignments[source_robot]) > 1:  # Только если у него больше одной операции
                    # Перемещаем последнюю операцию
                    moved_op = assignments[source_robot].pop()
                    assignments[empty_robot].append(moved_op)
                    
                    # Обновляем позицию
                    robot_positions[empty_robot] = moved_op.place_xyz
                    
                    logger.debug(f"Операция перемещена от робота {source_robot} к роботу {empty_robot}")
    
    logger.info(f"Распределено {len(scenario.operations)} операций на основе расстояния")
    
    # Выводим детальную статистику
    for i, ops in enumerate(assignments):
        logger.info(f"Робот {i}: {len(ops)} операций")
    
    return assignments

def assign_operations(scenario: ScenarioTxt, method: str = "balanced") -> List[List[Operation]]:
    """
    Главная функция назначения операций роботам.
    
    Args:
        scenario: Сценарий с роботами и операциями
        method: Метод назначения ("round_robin", "balanced", "distance_based", "genetic")
    
    Returns:
        Список операций для каждого робота
    """
    logger.info(f"Начинаем назначение операций методом: {method}")
    
    if method == "round_robin":
        return assign_operations_round_robin(scenario)
    elif method == "balanced":
        return assign_operations_balanced(scenario)
    elif method == "distance_based":
        return assign_operations_distance_based(scenario)
    elif method == "genetic":
        from core.genetic_algorithm import assign_operations_genetic
        return assign_operations_genetic(scenario)
    else:
        logger.warning(f"Неизвестный метод {method}, используем balanced")
        return assign_operations_balanced(scenario)
