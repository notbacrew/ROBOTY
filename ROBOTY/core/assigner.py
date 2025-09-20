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
    """
    K = len(scenario.robots)
    assignments = [[] for _ in range(K)]
    
    for i, op in enumerate(scenario.operations):
        robot_idx = i % K  # по кругу
        assignments[robot_idx].append(op)
        logger.debug(f"Операция {i} назначена роботу {robot_idx}")
    
    logger.info(f"Распределено {len(scenario.operations)} операций между {K} роботами")
    return assignments

def assign_operations_balanced(scenario: ScenarioTxt) -> List[List[Operation]]:
    """
    Алгоритм назначения с балансировкой нагрузки.
    Назначает операции роботам с наименьшей текущей нагрузкой.
    """
    K = len(scenario.robots)
    assignments = [[] for _ in range(K)]
    robot_loads = [0.0] * K  # текущая нагрузка каждого робота
    
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
    
    logger.info(f"Распределено {len(scenario.operations)} операций с балансировкой нагрузки")
    logger.info(f"Итоговые нагрузки роботов: {[f'{load:.2f}' for load in robot_loads]}")
    return assignments

def assign_operations_distance_based(scenario: ScenarioTxt) -> List[List[Operation]]:
    """
    Алгоритм назначения на основе минимального расстояния.
    Назначает операции роботам, которые находятся ближе всего к точке pick.
    """
    K = len(scenario.robots)
    assignments = [[] for _ in range(K)]
    robot_positions = [robot.base_xyz for robot in scenario.robots]
    
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
    
    logger.info(f"Распределено {len(scenario.operations)} операций на основе расстояния")
    return assignments

def assign_operations(scenario: ScenarioTxt, method: str = "balanced") -> List[List[Operation]]:
    """
    Главная функция назначения операций роботам.
    
    Args:
        scenario: Сценарий с роботами и операциями
        method: Метод назначения ("round_robin", "balanced", "distance_based")
    
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
    else:
        logger.warning(f"Неизвестный метод {method}, используем balanced")
        return assign_operations_balanced(scenario)
