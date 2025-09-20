import json
import logging
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# Настройка логгера для модуля парсинга
logger = logging.getLogger("ROBOTY.parser")

# ---- ОПИСАНИЕ СТРУКТУР ----
@dataclass
class Robot:
    id: int
    base_xyz: Tuple[float, float, float]
    joint_limits: List[Tuple[float, float]]   # [(J1_min, J1_max), ..., (J6_min, J6_max)]
    vmax: List[float]                         # макс. скорость суставов
    amax: List[float]                         # макс. ускорение суставов
    tool_clearance: float

@dataclass
class Operation:
    id: int
    pick_xyz: Tuple[float, float, float]
    place_xyz: Tuple[float, float, float]
    t_hold: float

@dataclass
class Scenario:
    robots: List[Robot]
    safe_dist: float
    operations: List[Operation]

# ---- ПАРСЕР ВХОДА ----
def parse_input(path: str) -> Optional[Scenario]:
    """
    Загружает входной JSON-файл и возвращает объект Scenario.
    Формат JSON:
    {
      "robots": [
        {
          "id": 1,
          "base_xyz": [0,0,0],
          "joint_limits": [[-180,180], [-90,90], ...],
          "vmax": [1,1,1,1,1,1],
          "amax": [2,2,2,2,2,2],
          "tool_clearance": 0.1
        }
      ],
      "safe_dist": 0.5,
      "operations": [
        {
          "id": 1,
          "pick_xyz": [0.5,0.2,0.1],
          "place_xyz": [0.7,0.3,0.2],
          "t_hold": 1.0
        }
      ]
    }
    """
    try:
        logger.info(f"Начинаем загрузку файла: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Файл {path} успешно загружен")
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка разбора JSON в файле {path}: {e}")
        raise ValueError(f"Некорректный формат JSON: {e}")
    except OSError as e:
        logger.error(f"Не удалось открыть файл {path}: {e}")
        raise FileNotFoundError(f"Файл не найден или недоступен: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при загрузке файла {path}: {e}")
        raise

    try:
        # Валидация и парсинг роботов
        if "robots" not in data:
            raise ValueError("Отсутствует секция 'robots' в JSON")
        
        robots = []
        for i, r in enumerate(data["robots"]):
            try:
                # Проверяем и нормализуем vmax и amax
                vmax = r["vmax"]
                amax = r["amax"]
                
                # Если это числа, преобразуем в списки
                if isinstance(vmax, (int, float)):
                    vmax = [float(vmax)] * 6
                elif isinstance(vmax, list) and len(vmax) != 6:
                    # Дополняем до 6 элементов если нужно
                    while len(vmax) < 6:
                        vmax.append(vmax[-1] if vmax else 1.0)
                
                if isinstance(amax, (int, float)):
                    amax = [float(amax)] * 6
                elif isinstance(amax, list) and len(amax) != 6:
                    # Дополняем до 6 элементов если нужно
                    while len(amax) < 6:
                        amax.append(amax[-1] if amax else 2.0)
                
                robot = Robot(
                    id=r["id"],
                    base_xyz=tuple(r["base_xyz"]),
                    joint_limits=[tuple(lim) for lim in r["joint_limits"]],
                    vmax=vmax,
                    amax=amax,
                    tool_clearance=r["tool_clearance"]
                )
                robots.append(robot)
                logger.debug(f"Робот {r['id']} успешно загружен")
            except KeyError as e:
                logger.error(f"Отсутствует обязательное поле {e} для робота {i}")
                raise ValueError(f"Некорректные данные робота {i}: отсутствует поле {e}")
            except Exception as e:
                logger.error(f"Ошибка при загрузке робота {i}: {e}")
                raise

        # Валидация и парсинг операций
        if "operations" not in data:
            raise ValueError("Отсутствует секция 'operations' в JSON")
            
        operations = []
        for i, o in enumerate(data["operations"]):
            try:
                operation = Operation(
                    id=o["id"],
                    pick_xyz=tuple(o["pick_xyz"]),
                    place_xyz=tuple(o["place_xyz"]),
                    t_hold=o.get("t_hold", 0.0)
                )
                operations.append(operation)
                logger.debug(f"Операция {o['id']} успешно загружена")
            except KeyError as e:
                logger.error(f"Отсутствует обязательное поле {e} для операции {i}")
                raise ValueError(f"Некорректные данные операции {i}: отсутствует поле {e}")
            except Exception as e:
                logger.error(f"Ошибка при загрузке операции {i}: {e}")
                raise

        safe_dist = data.get("safe_dist", 0.0)
        logger.info(f"Загружено {len(robots)} роботов и {len(operations)} операций")

        return Scenario(
            robots=robots,
            safe_dist=safe_dist,
            operations=operations
        )
    except Exception as e:
        logger.error(f"Ошибка при парсинге данных: {e}")
        raise

def parse_input_file(path):
    # Обертка для совместимости с импортом
    return parse_input(path)

# ---- ЗАПИСЬ РЕЗУЛЬТАТА ----
def save_output(path: str, schedule: dict):
    """
    Сохраняет расписание в JSON.
    Ожидается формат:
    {
      "makespan": 12.5,
      "robots": [
        {
          "id": 1,
          "trajectory": [
            {"t":0.0, "x":0.1, "y":0.2, "z":0.3},
            {"t":1.0, "x":0.2, "y":0.3, "z":0.5}
          ]
        }
      ]
    }
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(schedule, f, indent=2, ensure_ascii=False)