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

def parse_input_file(filepath):
    if filepath.endswith('.json'):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        K = len(data.get('robots', []))
        # Извлекаем joints для каждого робота, если есть
        joints = []
        for robot in data.get('robots', []):
            robot_joints = []
            for joint in robot.get('joints', []):
                # joint — это словарь, преобразуем в кортеж (min, max, v_max, a_max)
                robot_joints.append((
                    joint.get('min', 0),
                    joint.get('max', 0),
                    joint.get('v_max', 0),
                    joint.get('a_max', 0)
                ))
            joints.append(robot_joints)
        operations = []
        for op in data.get('operations', []):
            operations.append({
                'pick': tuple(op['pick']),
                'place': tuple(op['place']),
                't': op['t']
            })
        return {
            'K': K,
            'N': len(operations),
            'bases': [tuple(r['base']) for r in data.get('robots', [])],
            'joints': joints,  # теперь это список списков кортежей
            'tool_clearance': data.get('tool_clearance', 50),
            'safe_dist': data.get('safe_dist', 100),
            'operations': operations
        }
    else:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        K, N = map(int, lines[0].split())
        bases = []
        for i in range(K):
            bases.append(tuple(map(float, lines[1 + i].split())))
        joints = []
        for i in range(6):
            joints.append(tuple(map(float, lines[1 + K + i].split())))
        tool_clearance, safe_dist = map(float, lines[1 + K + 6].split())
        operations = []
        for i in range(N):
            parts = lines[1 + K + 7 + i].split()
            pick = tuple(map(float, parts[:3]))
            place = tuple(map(float, parts[3:6]))
            t = float(parts[6])
            operations.append({'pick': pick, 'place': place, 't': t})
        return {
            'K': K,
            'N': N,
            'bases': bases,
            'joints': [joints],  # для совместимости с JSON-структурой
            'tool_clearance': tool_clearance,
            'safe_dist': safe_dist,
            'operations': operations
        }

# Unit-test
def test_parse_input_file():
    import tempfile
    content = """2 2
0 0 0
100 0 0
-170 170 120 300
-120 120 120 300
-170 170 120 300
-120 120 120 300
-170 170 120 300
-120 120 120 300
50 100
100 200 300 400 500 600 500
150 250 350 450 550 650 600
"""
    with tempfile.NamedTemporaryFile('w+', delete=False) as f:
        f.write(content)
        f.flush()
        result = parse_input_file(f.name)
        assert result['K'] == 2
        assert result['N'] == 2
        assert len(result['bases']) == 2
        assert len(result['joints']) == 6
        assert len(result['operations']) == 2
    print("Parser test passed.")

if __name__ == "__main__":
    test_parse_input_file()

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