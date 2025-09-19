import json
from dataclasses import dataclass, field
from typing import List, Tuple

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
def parse_input(path: str) -> Scenario:
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
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    robots = [
        Robot(
            id=r["id"],
            base_xyz=tuple(r["base_xyz"]),
            joint_limits=[tuple(lim) for lim in r["joint_limits"]],
            vmax=r["vmax"],
            amax=r["amax"],
            tool_clearance=r["tool_clearance"]
        )
        for r in data["robots"]
    ]

    operations = [
        Operation(
            id=o["id"],
            pick_xyz=tuple(o["pick_xyz"]),
            place_xyz=tuple(o["place_xyz"]),
            t_hold=o["t_hold"]
        )
        for o in data["operations"]
    ]

    return Scenario(
        robots=robots,
        safe_dist=data["safe_dist"],
        operations=operations
    )

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