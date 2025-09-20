import logging
import math
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass

# Настройка логгера для модуля проверки коллизий
logger = logging.getLogger("ROBOTY.collision")

@dataclass
class CollisionInfo:
    """Информация о коллизии"""
    robot1_id: int
    robot2_id: int
    time: float
    position1: Tuple[float, float, float]
    position2: Tuple[float, float, float]
    distance: float
    min_required_distance: float

def interpolate_position(trajectory: List[Dict[str, Any]], time: float) -> Optional[Tuple[float, float, float]]:
    """
    Интерполирует позицию робота в заданное время.
    
    Args:
        trajectory: Список waypoints с полями t, x, y, z
        time: Время для интерполяции
    
    Returns:
        Позиция (x, y, z) или None если время вне диапазона
    """
    if not trajectory:
        return None
    
    # Находим ближайшие waypoints
    before_wp = None
    after_wp = None
    
    for wp in trajectory:
        if wp["t"] <= time:
            before_wp = wp
        if wp["t"] >= time and after_wp is None:
            after_wp = wp
            break
    
    # Если время до первого waypoint
    if before_wp is None:
        return (after_wp["x"], after_wp["y"], after_wp["z"])
    
    # Если время после последнего waypoint
    if after_wp is None:
        return (before_wp["x"], before_wp["y"], before_wp["z"])
    
    # Если время точно совпадает с waypoint
    if before_wp["t"] == time:
        return (before_wp["x"], before_wp["y"], before_wp["z"])
    
    # Линейная интерполяция между waypoints
    t1, t2 = before_wp["t"], after_wp["t"]
    alpha = (time - t1) / (t2 - t1)
    
    x = before_wp["x"] + alpha * (after_wp["x"] - before_wp["x"])
    y = before_wp["y"] + alpha * (after_wp["y"] - before_wp["y"])
    z = before_wp["z"] + alpha * (after_wp["z"] - before_wp["z"])
    
    return (x, y, z)

def calculate_distance(pos1: Tuple[float, float, float], pos2: Tuple[float, float, float]) -> float:
    """Вычисляет евклидово расстояние между двумя точками"""
    return math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(pos1, pos2)))

def get_time_range(plan: Dict[str, Any]) -> Tuple[float, float]:
    """
    Определяет временной диапазон плана.
    
    Returns:
        (start_time, end_time)
    """
    start_time = float('inf')
    end_time = 0.0
    
    for robot in plan["robots"]:
        if robot["trajectory"]:
            robot_start = min(wp["t"] for wp in robot["trajectory"])
            robot_end = max(wp["t"] for wp in robot["trajectory"])
            start_time = min(start_time, robot_start)
            end_time = max(end_time, robot_end)
    
    return start_time, end_time

def check_collisions_detailed(plan: Dict[str, Any], time_step: float = 0.1) -> List[CollisionInfo]:
    """
    Детальная проверка коллизий с возвратом информации о всех столкновениях.
    
    Args:
        plan: План выполнения с траекториями роботов
        time_step: Шаг времени для проверки
    
    Returns:
        Список информации о коллизиях
    """
    logger.info("Начинаем детальную проверку коллизий")
    
    collisions = []
    robots = plan["robots"]
    safe_dist = plan.get("safe_dist", 0.0)
    
    if len(robots) < 2:
        logger.info("Недостаточно роботов для проверки коллизий")
        return collisions
    
    # Определяем временной диапазон
    start_time, end_time = get_time_range(plan)
    if start_time == float('inf'):
        logger.warning("Не удалось определить временной диапазон")
        return collisions
    
    logger.debug(f"Проверяем коллизии в диапазоне времени: {start_time:.2f} - {end_time:.2f}")
    
    # Проверяем коллизии на каждом временном шаге
    current_time = start_time
    while current_time <= end_time:
        positions = []
        
        # Получаем позиции всех роботов в текущее время
        for robot in robots:
            pos = interpolate_position(robot["trajectory"], current_time)
            if pos is not None:
                positions.append((robot["id"], pos, robot.get("tool_clearance", 0.0)))
        
        # Проверяем все пары роботов
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                robot1_id, pos1, clearance1 = positions[i]
                robot2_id, pos2, clearance2 = positions[j]
                
                distance = calculate_distance(pos1, pos2)
                min_required_distance = safe_dist + clearance1 + clearance2
                
                if distance < min_required_distance:
                    collision = CollisionInfo(
                        robot1_id=robot1_id,
                        robot2_id=robot2_id,
                        time=current_time,
                        position1=pos1,
                        position2=pos2,
                        distance=distance,
                        min_required_distance=min_required_distance
                    )
                    collisions.append(collision)
                    logger.warning(f"Коллизия: роботы {robot1_id} и {robot2_id} в {current_time:.2f}s, "
                                 f"расстояние: {distance:.3f}, требуется: {min_required_distance:.3f}")
        
        current_time += time_step
    
    if collisions:
        logger.error(f"Обнаружено {len(collisions)} коллизий")
    else:
        logger.info("Коллизий не обнаружено")
    
    return collisions

def check_collisions(plan: Dict[str, Any], time_step: float = 0.1) -> bool:
    """
    Простая проверка коллизий - возвращает True если есть коллизии.
    
    Args:
        plan: План выполнения с траекториями роботов
        time_step: Шаг времени для проверки
    
    Returns:
        True если есть коллизии, False иначе
    """
    collisions = check_collisions_detailed(plan, time_step)
    return len(collisions) > 0

def check_static_obstacles(plan: Dict[str, Any], obstacles: List[Dict[str, Any]]) -> List[CollisionInfo]:
    """
    Проверяет коллизии с статическими препятствиями.
    
    Args:
        plan: План выполнения
        obstacles: Список препятствий с полями type, position, size
    
    Returns:
        Список коллизий с препятствиями
    """
    logger.info("Проверяем коллизии со статическими препятствиями")
    
    collisions = []
    
    for robot in plan["robots"]:
        for wp in robot["trajectory"]:
            robot_pos = (wp["x"], wp["y"], wp["z"])
            robot_clearance = robot.get("tool_clearance", 0.0)
            
            for obstacle in obstacles:
                if obstacle["type"] == "sphere":
                    # Сферическое препятствие
                    obs_pos = obstacle["position"]
                    obs_radius = obstacle["size"]
                    
                    distance = calculate_distance(robot_pos, obs_pos)
                    min_distance = robot_clearance + obs_radius
                    
                    if distance < min_distance:
                        collision = CollisionInfo(
                            robot1_id=robot["id"],
                            robot2_id=-1,  # -1 для препятствий
                            time=wp["t"],
                            position1=robot_pos,
                            position2=obs_pos,
                            distance=distance,
                            min_required_distance=min_distance
                        )
                        collisions.append(collision)
                        logger.warning(f"Коллизия робота {robot['id']} с препятствием в {wp['t']:.2f}s")
                
                elif obstacle["type"] == "box":
                    # Прямоугольное препятствие
                    obs_center = obstacle["position"]
                    obs_size = obstacle["size"]  # (width, height, depth)
                    
                    # Упрощенная проверка - считаем препятствие сферой с радиусом по диагонали
                    max_radius = math.sqrt(sum(s**2 for s in obs_size)) / 2
                    
                    distance = calculate_distance(robot_pos, obs_center)
                    min_distance = robot_clearance + max_radius
                    
                    if distance < min_distance:
                        collision = CollisionInfo(
                            robot1_id=robot["id"],
                            robot2_id=-1,
                            time=wp["t"],
                            position1=robot_pos,
                            position2=obs_center,
                            distance=distance,
                            min_required_distance=min_distance
                        )
                        collisions.append(collision)
                        logger.warning(f"Коллизия робота {robot['id']} с препятствием в {wp['t']:.2f}s")
    
    if collisions:
        logger.error(f"Обнаружено {len(collisions)} коллизий с препятствиями")
    else:
        logger.info("Коллизий с препятствиями не обнаружено")
    
    return collisions

def get_collision_summary(collisions: List[CollisionInfo]) -> Dict[str, Any]:
    """
    Создает сводку по коллизиям.
    
    Returns:
        Словарь со статистикой коллизий
    """
    if not collisions:
        return {
            "total_collisions": 0,
            "robot_collisions": 0,
            "obstacle_collisions": 0,
            "time_range": None,
            "affected_robots": []
        }
    
    robot_collisions = [c for c in collisions if c.robot2_id > 0]
    obstacle_collisions = [c for c in collisions if c.robot2_id == -1]
    
    times = [c.time for c in collisions]
    affected_robots = set()
    for c in collisions:
        affected_robots.add(c.robot1_id)
        if c.robot2_id > 0:
            affected_robots.add(c.robot2_id)
    
    return {
        "total_collisions": len(collisions),
        "robot_collisions": len(robot_collisions),
        "obstacle_collisions": len(obstacle_collisions),
        "time_range": (min(times), max(times)) if times else None,
        "affected_robots": sorted(list(affected_robots))
    }