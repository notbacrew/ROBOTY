def save_plan_to_txt(filename, makespan, robots_waypoints):
    """
    Сохраняет план в текстовый файл в формате ТЗ с комментариями для удобства чтения.
    filename: путь к файлу
    makespan: общее время выполнения (мс)
    robots_waypoints: список кортежей (robot_id, waypoints)
    waypoints: список (t, x, y, z)
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Результаты планирования роботов\n")
        f.write("# Makespan (общее время выполнения всех операций, мс):\n")
        f.write(f"{makespan:.2f}\n\n")
        for robot_id, waypoints in robots_waypoints:
            f.write(f"# Робот R{robot_id}, количество точек маршрута = {len(waypoints)}\n")
            f.write("# Формат: t (мс)   X   Y   Z\n")
            f.write(f"R{robot_id} {len(waypoints)}\n")
            for wp in waypoints:
                t, x, y, z = wp
                f.write(f"t={t:.2f}ms   x={x:.3f}   y={y:.3f}   z={z:.3f}\n")
            f.write("\n")
import re
import logging
from typing import List, Tuple, Optional

# Настройка логгера для модуля парсинга TXT
logger = logging.getLogger("ROBOTY.parser_txt")

class RobotConfig:
    def __init__(self, base_xyz, joint_limits, vmax, amax, tool_clearance, robot_id=None):
        self.id = robot_id if robot_id is not None else 1  # ID робота
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


def parse_txt_input(path: str) -> Optional[ScenarioTxt]:
    """
    Парсит TXT файл в формате ТЗ с обработкой ошибок.
    Формат:
    K N
    J1_x J1_y J1_z
    ...
    Tool_clearance Safe_dist
    Px_pick Py_pick Pz_pick Px_place Py_place Pz_place t_i
    ...
    """
    try:
        logger.info(f"Начинаем загрузку TXT файла: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        
        if not lines:
            raise ValueError("Файл пуст или содержит только комментарии")
        
        logger.debug(f"Загружено {len(lines)} строк из файла")
        
        # 1. K N
        try:
            K, N = map(int, lines[0].split())
            logger.debug(f"Количество роботов: {K}, операций: {N}")
        except (ValueError, IndexError) as e:
            logger.error(f"Ошибка в первой строке (K N): {e}")
            raise ValueError("Некорректный формат первой строки. Ожидается: K N")
        
        if K <= 0 or N < 0:
            raise ValueError(f"Некорректные значения: K={K}, N={N}")
        
        idx = 1

        # 2. Координаты оснований
        base_xyz = []
        for i in range(K):
            if idx >= len(lines):
                raise ValueError(f"Недостаточно строк для координат оснований. Ожидается {K} строк")
            try:
                coords = tuple(map(float, lines[idx].split()))
                if len(coords) != 3:
                    raise ValueError(f"Координаты должны содержать 3 значения (x, y, z)")
                base_xyz.append(coords)
                logger.debug(f"Основание робота {i+1}: {coords}")
            except ValueError as e:
                logger.error(f"Ошибка в строке {idx+1} (координаты основания {i+1}): {e}")
                raise ValueError(f"Некорректные координаты основания робота {i+1}")
            idx += 1

        # 3. Ограничения суставов (6 суставов)
        joint_limits = []
        vmax = []
        amax = []
        for i in range(6):
            if idx >= len(lines):
                raise ValueError(f"Недостаточно строк для ограничений суставов. Ожидается 6 строк")
            try:
                parts = lines[idx].split()
                if len(parts) != 4:
                    raise ValueError(f"Строка должна содержать 4 значения: min, max, vmax, amax")
                joint_limits.append((float(parts[0]), float(parts[1])))
                vmax.append(float(parts[2]))
                amax.append(float(parts[3]))
                logger.debug(f"Сустав {i+1}: limits={joint_limits[-1]}, vmax={vmax[-1]}, amax={amax[-1]}")
            except ValueError as e:
                logger.error(f"Ошибка в строке {idx+1} (сустав {i+1}): {e}")
                raise ValueError(f"Некорректные параметры сустава {i+1}")
            idx += 1

        # 4. Tool_clearance и Safe_dist
        if idx >= len(lines):
            raise ValueError("Отсутствует строка с Tool_clearance и Safe_dist")
        try:
            tool_clearance, safe_dist = map(float, lines[idx].split())
            if tool_clearance < 0 or safe_dist < 0:
                raise ValueError("Tool_clearance и Safe_dist должны быть неотрицательными")
            logger.debug(f"Tool_clearance: {tool_clearance}, Safe_dist: {safe_dist}")
        except ValueError as e:
            logger.error(f"Ошибка в строке {idx+1} (Tool_clearance Safe_dist): {e}")
            raise ValueError("Некорректные значения Tool_clearance или Safe_dist")
        idx += 1

        # 5. Операции
        operations = []
        for i in range(N):
            if idx >= len(lines):
                raise ValueError(f"Недостаточно строк для операций. Ожидается {N} строк")
            try:
                parts = lines[idx].split()
                if len(parts) != 7:
                    raise ValueError(f"Строка операции должна содержать 7 значений")
                pick_xyz = tuple(map(float, parts[0:3]))
                place_xyz = tuple(map(float, parts[3:6]))
                t_hold = float(parts[6])
                if t_hold < 0:
                    raise ValueError("Время удержания не может быть отрицательным")
                operations.append(Operation(pick_xyz, place_xyz, t_hold))
                logger.debug(f"Операция {i+1}: pick={pick_xyz}, place={place_xyz}, t_hold={t_hold}")
            except ValueError as e:
                logger.error(f"Ошибка в строке {idx+1} (операция {i+1}): {e}")
                raise ValueError(f"Некорректные данные операции {i+1}")
            idx += 1

        # Создание конфигураций роботов
        robots = []
        for i in range(K):
            robots.append(RobotConfig(
                base_xyz=base_xyz[i],
                joint_limits=joint_limits,
                vmax=vmax,
                amax=amax,
                tool_clearance=tool_clearance,
                robot_id=i + 1  # ID робота (начиная с 1)
            ))

        logger.info(f"Успешно загружено {K} роботов и {N} операций из TXT файла")
        return ScenarioTxt(robots=robots, safe_dist=safe_dist, operations=operations)
        
    except OSError as e:
        logger.error(f"Не удалось открыть файл {path}: {e}")
        raise FileNotFoundError(f"Файл не найден или недоступен: {e}")
    except Exception as e:
        logger.error(f"Ошибка при парсинге TXT файла {path}: {e}")
        raise
