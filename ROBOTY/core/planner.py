import matplotlib.pyplot as plt


def run_planner(scenario):
    # пока возвращаем фиктивный результат
    return {"makespan": 0, "robots": []}


def run_planner_algorithm(input_data):
    # TODO: реализовать алгоритмы распределения
    # Пример: возвращает фиктивный план
    return {"plan": "example_plan", "input": input_data}


def assign_operations(K, operations):
    # Жадное распределение: назначаем операцию роботу с минимальным текущим временем
    robot_ops = [[] for _ in range(K)]
    robot_times = [0] * K
    for op in operations:
        # Оценка времени операции: расстояние + время pick/place
        pick, place, t = op['pick'], op['place'], op['t']
        move_time = sum([(a - b) ** 2 for a, b in zip(pick, place)]) ** 0.5 / 100  # v_max=100
        total_time = move_time + t
        idx = robot_times.index(min(robot_times))
        robot_ops[idx].append(op)
        robot_times[idx] += total_time
    return robot_ops


def check_joint_limits(point, joints):
    # joints — список кортежей для одного робота
    for i in range(3):
        j_min, j_max, *_ = joints[i]
        if not (j_min <= point[i] <= j_max):
            return False
    return True


def generate_waypoints(robot_ops, joints, v_max=100, a_max=200):
    waypoints = []
    for robot_idx, ops in enumerate(robot_ops):
        wp = []
        time = 0
        # Получаем суставы только для текущего робота
        robot_joints = joints[robot_idx] if len(joints) > robot_idx else joints[0]
        for op in ops:
            pick = op['pick']
            place = op['place']
            # Проверка достижимости
            if not check_joint_limits(pick, robot_joints) or not check_joint_limits(place, robot_joints):
                continue
            t_move = sum([(a - b) ** 2 for a, b in zip(pick, place)]) ** 0.5 / v_max
            wp.append({'pos': pick, 'time': time})
            time += t_move
            wp.append({'pos': place, 'time': time})
            time += op['t']
        waypoints.append(wp)
    return waypoints