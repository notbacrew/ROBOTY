import logging
from typing import Dict, Any, List


logger = logging.getLogger("ROBOTY.safety")


def _insert_pause_into_trajectory(trajectory: List[Dict[str, Any]], pause_time: float, pause_duration: float) -> List[Dict[str, Any]]:
    """
    Вставляет паузу в траекторию в момент времени pause_time и сдвигает
    все последующие точки на pause_duration. Если точной точки нет, добавляет
    точку, интерполируя между соседними.
    """
    if not trajectory:
        return trajectory

    # Найдем позицию для вставки
    index_for_insert = None
    for idx, wp in enumerate(trajectory):
        if wp["t"] >= pause_time:
            index_for_insert = idx
            break

    # Если пауза позже последней точки, просто продлеваем финальную точку
    if index_for_insert is None:
        last = trajectory[-1].copy()
        # Вставляем дубликат с тем же положением на момент паузы
        pause_wp = {"t": pause_time, "x": last["x"], "y": last["y"], "z": last["z"]}
        # Затем точку после паузы
        after_wp = {"t": pause_time + pause_duration, "x": last["x"], "y": last["y"], "z": last["z"]}
        shifted = []
        shifted.extend(trajectory)
        shifted.append(pause_wp)
        shifted.append(after_wp)
        return shifted

    # Определим положение на момент паузы
    if trajectory[index_for_insert]["t"] == pause_time or index_for_insert == 0:
        # Точное совпадение или пауза перед первой точкой
        pause_pos = trajectory[index_for_insert]
        pause_wp = {"t": pause_time, "x": pause_pos["x"], "y": pause_pos["y"], "z": pause_pos["z"]}
    else:
        before_wp = trajectory[index_for_insert - 1]
        after_wp = trajectory[index_for_insert]
        t1 = before_wp["t"]
        t2 = after_wp["t"]
        if t2 == t1:
            alpha = 0.0
        else:
            alpha = (pause_time - t1) / (t2 - t1)
        x = before_wp["x"] + alpha * (after_wp["x"] - before_wp["x"])
        y = before_wp["y"] + alpha * (after_wp["y"] - before_wp["y"])
        z = before_wp["z"] + alpha * (after_wp["z"] - before_wp["z"])
        pause_wp = {"t": pause_time, "x": x, "y": y, "z": z}

    # Собираем новую траекторию: до паузы + сама пауза (двойная точка) + сдвиг
    new_traj: List[Dict[str, Any]] = []
    # До места вставки (точки раньше pause_time) — без изменений
    for wp in trajectory:
        if wp["t"] < pause_time:
            new_traj.append(wp)
        else:
            break

    # Вставляем точку паузы и точку после паузы
    new_traj.append(pause_wp)
    after_pause_wp = {"t": pause_time + pause_duration, "x": pause_wp["x"], "y": pause_wp["y"], "z": pause_wp["z"]}
    new_traj.append(after_pause_wp)

    # Оставшиеся точки со сдвигом по времени
    for wp in trajectory:
        if wp["t"] >= pause_time:
            shifted_wp = {"t": wp["t"] + pause_duration, "x": wp["x"], "y": wp["y"], "z": wp["z"]}
            new_traj.append(shifted_wp)

    return new_traj


def enforce_online_safety(plan: Dict[str, Any], time_step: float = 0.05, pause_duration: float = 0.5) -> Dict[str, Any]:
    """
    Добавляет паузы в траектории роботов в моменты потенциальных столкновений,
    чтобы обеспечить остановку манипуляторов.

    Возвращает новый "безопасный" план. Исходный план не изменяется.
    """
    try:
        from core.collision import check_collisions_detailed
    except Exception as e:
        logger.error(f"Не удалось импортировать модуль коллизий: {e}")
        return plan

    logger.info("Применяем онлайн-безопасность: вставка пауз при коллизиях")

    # Клонируем план поверхностно
    safe_plan: Dict[str, Any] = {k: v for k, v in plan.items()}
    safe_plan["robots"] = [
        {
            **robot,
            "trajectory": [
                {"t": wp.get("t", 0.0), "x": wp.get("x", 0.0), "y": wp.get("y", 0.0), "z": wp.get("z", 0.0)}
                for wp in robot.get("trajectory", [])
            ],
        }
        for robot in plan.get("robots", [])
    ]

    collisions = check_collisions_detailed(safe_plan, time_step=time_step)
    if not collisions:
        logger.info("Столкновений не обнаружено — модификации не требуются")
        return safe_plan

    # Сгруппируем столкновения по времени (берем первые события для минимального вмешательства)
    processed_times = set()
    for col in collisions:
        # Квантование времени, чтобы избежать повторов из-за шага
        t_key = round(col.time / time_step) * time_step
        if t_key in processed_times:
            continue
        processed_times.add(t_key)

        # На этой отметке времени ставим паузу обоим роботам-участникам
        r1_id = col.robot1_id
        r2_id = col.robot2_id
        for robot in safe_plan["robots"]:
            if robot["id"] in (r1_id, r2_id):
                robot["trajectory"] = _insert_pause_into_trajectory(robot["trajectory"], pause_time=col.time, pause_duration=pause_duration)
                logger.debug(f"Добавлена пауза {pause_duration:.2f}s роботу {robot['id']} в t={col.time:.2f}s")

    # Пересчитываем makespan как максимальное время среди всех траекторий
    max_t = 0.0
    for robot in safe_plan["robots"]:
        if robot["trajectory"]:
            max_t = max(max_t, max(wp["t"] for wp in robot["trajectory"]))
    safe_plan["makespan"] = max_t

    logger.info("Онлайн-безопасность применена: паузы вставлены")
    return safe_plan


