import logging
import math
import numpy as np
from typing import List, Tuple, Dict, Any
from core.parser_txt import RobotConfig, Operation, ScenarioTxt
from core.assigner import assign_operations

# Настройка логгера для модуля планирования
logger = logging.getLogger("ROBOTY.planner")

def check_kinematics(robot: RobotConfig, point: Tuple[float, float, float]) -> bool:
    """
    Проверяет достижимость точки TCP с учетом ограничений суставов.
    Простейшая модель: если точка в пределах досягаемости по XYZ, считаем достижимой.
    Для реального робота требуется обратная кинематика.
    """
    base = robot.base_xyz
    max_reach = 0
    for lim in robot.joint_limits:
        max_reach += abs(lim[1] - lim[0])  # упрощенно: сумма диапазонов
    dist = math.sqrt(sum((p - b) ** 2 for p, b in zip(point, base)))
    return dist <= max_reach

def trapezoidal_velocity_profile(distance: float, vmax: float, amax: float) -> Tuple[float, float, float]:
    """
    Вычисляет параметры трапецеидального профиля скорости.
    
    Returns:
        (t_accel, t_const, t_total) - время разгона, постоянной скорости, общее время
    """
    t_accel = vmax / amax
    s_accel = 0.5 * amax * t_accel ** 2
    
    if 2 * s_accel >= distance:
        # Треугольный профиль (недостаточно расстояния для достижения vmax)
        t_accel = math.sqrt(distance / amax)
        t_const = 0.0
        t_total = 2 * t_accel
    else:
        # Трапецеидальный профиль
        s_const = distance - 2 * s_accel
        t_const = s_const / vmax
        t_total = 2 * t_accel + t_const
    
    return t_accel, t_const, t_total

def generate_trajectory_waypoints(start: Tuple[float, float, float], 
                                end: Tuple[float, float, float], 
                                vmax: float, 
                                amax: float, 
                                t_start: float,
                                num_points: int = 10) -> List[Tuple[float, float, float, float]]:
    """
    Генерирует waypoints для траектории с трапецеидальным профилем скорости.
    
    Returns:
        Список waypoints: (t, x, y, z)
    """
    distance = math.sqrt(sum((e - s) ** 2 for s, e in zip(start, end)))
    
    if distance < 1e-6:  # Точки совпадают
        return [(t_start, *start)]
    
    t_accel, t_const, t_total = trapezoidal_velocity_profile(distance, vmax, amax)
    
    waypoints = []
    direction = [(e - s) / distance for s, e in zip(start, end)]
    
    for i in range(num_points + 1):
        t_rel = (i / num_points) * t_total
        t_abs = t_start + t_rel
        
        # Вычисляем пройденное расстояние
        if t_rel <= t_accel:
            # Фаза разгона
            s = 0.5 * amax * t_rel ** 2
        elif t_rel <= t_accel + t_const:
            # Фаза постоянной скорости
            s = 0.5 * amax * t_accel ** 2 + vmax * (t_rel - t_accel)
        else:
            # Фаза торможения
            t_brake = t_rel - t_accel - t_const
            s = 0.5 * amax * t_accel ** 2 + vmax * t_const + vmax * t_brake - 0.5 * amax * t_brake ** 2
        
        # Вычисляем позицию
        x = start[0] + s * direction[0]
        y = start[1] + s * direction[1]
        z = start[2] + s * direction[2]
        
        waypoints.append((t_abs, x, y, z))
    
    return waypoints

def plan_robot_trajectory(robot: RobotConfig, operations: List[Operation], t0: float = 0.0) -> List[Tuple[float, float, float, float]]:
    """
    Формирует последовательность waypoints для робота с временными метками.
    """
    if not operations:
        logger.warning("Нет операций для планирования траектории")
        return [(t0, *robot.base_xyz)]
    
    waypoints = []
    curr_pos = robot.base_xyz
    curr_time = t0
    
    # Используем минимальные ограничения для безопасности
    if isinstance(robot.vmax, list):
        vmax = min(robot.vmax) if robot.vmax else 1.0
    else:
        vmax = float(robot.vmax) if robot.vmax else 1.0
    
    if isinstance(robot.amax, list):
        amax = min(robot.amax) if robot.amax else 2.0
    else:
        amax = float(robot.amax) if robot.amax else 2.0
    
    logger.debug(f"Планирование траектории для робота с {len(operations)} операциями")
    
    for i, op in enumerate(operations):
        # Проверяем кинематику
        if not check_kinematics(robot, op.pick_xyz):
            logger.warning(f"Точка pick {op.pick_xyz} недостижима для робота")
        if not check_kinematics(robot, op.place_xyz):
            logger.warning(f"Точка place {op.place_xyz} недостижима для робота")
        
        # Движение к точке pick
        pick_waypoints = generate_trajectory_waypoints(curr_pos, op.pick_xyz, vmax, amax, curr_time)
        waypoints.extend(pick_waypoints)
        curr_time = pick_waypoints[-1][0]
        
        # Время удержания в точке pick
        if op.t_hold > 0:
            curr_time += op.t_hold
            waypoints.append((curr_time, *op.pick_xyz))
        
        # Движение к точке place
        place_waypoints = generate_trajectory_waypoints(op.pick_xyz, op.place_xyz, vmax, amax, curr_time)
        waypoints.extend(place_waypoints)
        curr_time = place_waypoints[-1][0]
        
        # Время удержания в точке place
        if op.t_hold > 0:
            curr_time += op.t_hold
            waypoints.append((curr_time, *op.place_xyz))
        
        curr_pos = op.place_xyz
        logger.debug(f"Операция {i+1} запланирована, время завершения: {curr_time:.2f}")
    
    logger.info(f"Траектория робота запланирована, общее время: {curr_time:.2f}")
    return waypoints

def calculate_makespan(robot_trajectories: List[List[Tuple[float, float, float, float]]]) -> float:
    """
    Вычисляет makespan (общее время выполнения всех операций).
    """
    if not robot_trajectories:
        return 0.0
    
    max_times = []
    for trajectory in robot_trajectories:
        if trajectory:
            max_time = max(wp[0] for wp in trajectory)
            max_times.append(max_time)
    
    return max(max_times) if max_times else 0.0

def run_planner_algorithm(input_data: ScenarioTxt, assignment_method: str = "balanced") -> Dict[str, Any]:
    """
    Главная функция планировщика.
    
    Args:
        input_data: Сценарий с роботами и операциями
        assignment_method: Метод назначения операций
    
    Returns:
        Словарь с планом выполнения
    """
    logger.info("Запуск планировщика траекторий")
    
    try:
        # 1. Назначение операций роботам
        assignments = assign_operations(input_data, assignment_method)
        logger.info(f"Операции назначены методом: {assignment_method}")
        
        # 2. Планирование траекторий для каждого робота
        robot_trajectories = []
        robot_plans = []
        
        for i, (robot, operations) in enumerate(zip(input_data.robots, assignments)):
            logger.debug(f"Планирование траектории для робота {i+1} с {len(operations)} операциями")
            
            trajectory = plan_robot_trajectory(robot, operations)
            robot_trajectories.append(trajectory)
            
            # Преобразуем в формат для визуализации
            viz_trajectory = []
            for wp in trajectory:
                viz_trajectory.append({
                    "t": wp[0],
                    "x": wp[1],
                    "y": wp[2], 
                    "z": wp[3]
                })
            
            robot_plans.append({
                "id": i + 1,
                "base_xyz": robot.base_xyz,
                "trajectory": viz_trajectory,
                "tool_clearance": robot.tool_clearance,
                "operations_count": len(operations)
            })
        
        # 3. Вычисление makespan
        makespan = calculate_makespan(robot_trajectories)
        
        result = {
            "robots": robot_plans,
            "makespan": makespan,
            "safe_dist": input_data.safe_dist,
            "assignment_method": assignment_method
        }
        
        logger.info(f"Планирование завершено. Makespan: {makespan:.2f}")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка в планировщике: {e}")
        raise

def run_planner(scenario: ScenarioTxt) -> Dict[str, Any]:
    """
    Обертка для совместимости с существующим кодом.
    """
    return run_planner_algorithm(scenario)