import math

def check_collisions(robots_waypoints, safe_dist, tool_clearance):
    """
    Проверяет коллизии между всеми роботами на каждом временном шаге.
    robots_waypoints: список списков waypoints [(t, x, y, z)] для каждого робота
    Возвращает True, если есть коллизии, иначе False
    """
    # Собираем все временные метки
    all_times = set()
    for waypoints in robots_waypoints:
        for wp in waypoints:
            all_times.add(wp[0])
    times = sorted(all_times)
    # Для каждого момента времени проверяем расстояния
    for t in times:
        positions = []
        for waypoints in robots_waypoints:
            # Находим ближайший waypoint по времени
            pos = min(waypoints, key=lambda wp: abs(wp[0] - t))[1:4]
            positions.append(pos)
        # Проверяем пары
        for i in range(len(positions)):
            for j in range(i+1, len(positions)):
                dist = math.sqrt(sum((positions[i][k] - positions[j][k]) ** 2 for k in range(3)))
                min_dist = safe_dist + 2 * tool_clearance
                if dist < min_dist:
                    return True  # есть коллизия
    return False
def check_collisions(plan):
    # TODO: реализовать реальную проверку коллизий
    # Пример: всегда возвращает False (нет коллизий)
    return False
