from core.parser_txt import RobotConfig, Operation
import math

def check_kinematics(robot: RobotConfig, point: tuple) -> bool:
    """
    Проверяет достижимость точки TCP с учетом ограничений суставов.
    Простейшая модель: если точка в пределах досягаемости по XYZ, считаем достижимой.
    Для реального робота требуется обратная кинематика.
    """
    # Пример: ограничение по радиусу
    base = robot.base_xyz
    max_reach = 0
    for lim in robot.joint_limits:
        max_reach += abs(lim[1] - lim[0])  # упрощенно: сумма диапазонов
    dist = math.sqrt(sum((p - b) ** 2 for p, b in zip(point, base)))
    return dist <= max_reach
import math
from core.parser_txt import RobotConfig, Operation
import math

def linear_trajectory(start, end, vmax, amax, t_start):
    """
    Строит линейную траекторию между двумя точками с учетом ограничений скорости и ускорения.
    Возвращает список waypoints: (t, x, y, z)
    """
    dist = math.sqrt(sum((e - s) ** 2 for s, e in zip(start, end)))
    t_accel = vmax / amax
    s_accel = 0.5 * amax * t_accel ** 2
    if 2 * s_accel > dist:
        t_total = math.sqrt(2 * dist / amax)
    else:
        s_const = dist - 2 * s_accel
        t_const = s_const / vmax
        t_total = 2 * t_accel + t_const
    return [
        (t_start, *start),
        (t_start + t_total, *end)
    ]

def plan_robot_trajectory(robot: RobotConfig, operations, t0=0.0):
    """
    Формирует последовательность waypoints для робота с временными метками.
    """
    waypoints = []
    curr_pos = robot.base_xyz
    curr_time = t0
    vmax = min(robot.vmax)
    amax = min(robot.amax)
    for op in operations:
        wp1 = linear_trajectory(curr_pos, op.pick_xyz, vmax, amax, curr_time)
        waypoints.extend(wp1)
        curr_time = waypoints[-1][0]
        curr_time += op.t_hold
        wp2 = linear_trajectory(op.pick_xyz, op.place_xyz, vmax, amax, curr_time)
        waypoints.extend(wp2)
        curr_time = waypoints[-1][0]
        curr_time += op.t_hold
        curr_pos = op.place_xyz
    return waypoints
def run_planner(scenario):
    # пока возвращаем фиктивный результат
    return {"makespan": 0, "robots": []}


def run_planner_algorithm(input_data):
    # TODO: реализовать алгоритмы распределения
    # Пример: возвращает фиктивный план для визуализации
    # Формируем структуру, ожидаемую визуализатором
    robots = []
    for robot in input_data.robots:
        # Пример: строим фиктивную траекторию
        trajectory = [
            {"x": robot.base_xyz[0], "y": robot.base_xyz[1], "z": robot.base_xyz[2]},
            {"x": robot.base_xyz[0]+1, "y": robot.base_xyz[1]+1, "z": robot.base_xyz[2]}
        ]
        robots.append({
            "id": robot.id,
            "trajectory": trajectory
        })
    return {
        "robots": robots,
        "makespan": 1.0
    }