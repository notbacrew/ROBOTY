from typing import List
from core.parser_txt import ScenarioTxt, Operation

def assign_operations(scenario: ScenarioTxt) -> List[List[Operation]]:
    """
    Простейший алгоритм назначения: по очереди распределяет операции между роботами,
    чтобы минимизировать простой и сбалансировать нагрузку.
    Возвращает список операций для каждого робота.
    """
    K = len(scenario.robots)
    N = len(scenario.operations)
    assignments = [[] for _ in range(K)]
    for i, op in enumerate(scenario.operations):
        robot_idx = i % K  # по кругу
        assignments[robot_idx].append(op)
    return assignments
