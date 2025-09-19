def save_plan_to_txt(filename, makespan, robots_waypoints):
    """
    Сохраняет план в текстовый файл в формате ТЗ.
    filename: путь к файлу
    makespan: общее время выполнения (мс)
    robots_waypoints: список кортежей (robot_id, waypoints)
    waypoints: список (t, x, y, z)
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"{makespan:.2f}\n")
        for robot_id, waypoints in robots_waypoints:
            f.write(f"R{robot_id} {len(waypoints)}\n")
            for wp in waypoints:
                t, x, y, z = wp
                f.write(f"{t:.2f} {x:.3f} {y:.3f} {z:.3f}\n")
import re
from typing import List, Tuple

class RobotConfig:
    def __init__(self, base_xyz, joint_limits, vmax, amax, tool_clearance):
        self.base_xyz = base_xyz
        self.joint_limits = joint_limits
        self.vmax = vmax
        self.amax = amax
        self.tool_clearance = tool_clearance

class Operation:
    def __init__(self, pick_xyz, place_xyz, t_hold):
        self.pick_xyz = pick_xyz
        self.place_xyz = place_xyz
        self.t_hold = t_hold

class ScenarioTxt:
    def __init__(self, robots, safe_dist, operations):
        self.robots = robots
        self.safe_dist = safe_dist
        self.operations = operations


def parse_txt_input(path: str) -> ScenarioTxt:
    with open(path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    # 1. K N
    K, N = map(int, lines[0].split())
    idx = 1

    # 2. Координаты оснований
    base_xyz = []
    for _ in range(K):
        base_xyz.append(tuple(map(float, lines[idx].split())))
        idx += 1

    # 3. Ограничения суставов
    joint_limits = []
    vmax = []
    amax = []
    for _ in range(6):
        parts = lines[idx].split()
        joint_limits.append((float(parts[0]), float(parts[1])))
        vmax.append(float(parts[2]))
        amax.append(float(parts[3]))
        idx += 1

    # 4. Tool_clearance и Safe_dist
    tool_clearance, safe_dist = map(float, lines[idx].split())
    idx += 1

    # 5. Операции
    operations = []
    for _ in range(N):
        parts = lines[idx].split()
        pick_xyz = tuple(map(float, parts[0:3]))
        place_xyz = tuple(map(float, parts[3:6]))
        t_hold = float(parts[6])
        operations.append(Operation(pick_xyz, place_xyz, t_hold))
        idx += 1

    robots = []
    for i in range(K):
        robots.append(RobotConfig(
            base_xyz=base_xyz[i],
            joint_limits=joint_limits,
            vmax=vmax,
            amax=amax,
            tool_clearance=tool_clearance
        ))

    return ScenarioTxt(robots=robots, safe_dist=safe_dist, operations=operations)
