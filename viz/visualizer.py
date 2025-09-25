import logging
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, Any, List, Tuple

# Настройка логгера для модуля визуализации
logger = logging.getLogger("ROBOTY.visualizer")
try:
    from core.mesh_loader import load_obj, load_hand_definition
except Exception:
    load_obj = None
    load_hand_definition = None

def _interpolate_position(trajectory: List[Dict[str, Any]], t: float) -> Tuple[float, float, float]:
    """
    Линейная интерполяция позиции TCP по времени t.
    Возвращает последнюю известную точку, если t вне диапазона.
    """
    if not trajectory:
        return (0.0, 0.0, 0.0)
    if t <= trajectory[0]["t"]:
        p = trajectory[0]
        return (p["x"], p["y"], p["z"])
    if t >= trajectory[-1]["t"]:
        p = trajectory[-1]
        return (p["x"], p["y"], p["z"])
    for i in range(len(trajectory) - 1):
        p1 = trajectory[i]
        p2 = trajectory[i + 1]
        if p1["t"] <= t <= p2["t"]:
            dt = p2["t"] - p1["t"]
            alpha = 0.0 if dt == 0 else (t - p1["t"]) / dt
            x = p1["x"] + alpha * (p2["x"] - p1["x"]) 
            y = p1["y"] + alpha * (p2["y"] - p1["y"]) 
            z = p1["z"] + alpha * (p2["z"] - p1["z"]) 
            return (x, y, z)
    p = trajectory[-1]
    return (p["x"], p["y"], p["z"])

def _arm_segments(base: Tuple[float, float, float], tcp: Tuple[float, float, float], segments: int = 4, bulge: float = 0.15, model: str = "curved") -> List[Tuple[float, float, float]]:
    """
    Упрощенная модель манипулятора с «локтем»: базовая линия base→tcp,
    сочленения формируют небольшую дугу (bulge) перпендикулярно направлению.
    Возвращает список точек суставов (включая base и tcp).
    """
    bx, by, bz = base
    tx, ty, tz = tcp
    v = np.array([tx - bx, ty - by, tz - bz], dtype=float)
    norm_v = np.linalg.norm(v)
    if norm_v == 0:
        return [base, tcp]
    v_dir = v / norm_v
    up = np.array([0.0, 0.0, 1.0])
    side = np.cross(v_dir, up)
    if np.linalg.norm(side) < 1e-6:
        up = np.array([0.0, 1.0, 0.0])
        side = np.cross(v_dir, up)
    side_dir = side / (np.linalg.norm(side) + 1e-12)
    points: List[Tuple[float, float, float]] = []
    for i in range(segments + 1):
        a = i / segments
        base_point = np.array([bx, by, bz]) + a * v
        if model == "straight":
            p = base_point
        elif model == "double":
            # две выпуклости (двойной локоть)
            offset_mag = bulge * (np.sin(np.pi * a) + 0.5 * np.sin(2 * np.pi * a))
            p = base_point + offset_mag * side_dir
        else:
            # curved (один локоть)
            offset_mag = bulge * np.sin(np.pi * a)
            p = base_point + offset_mag * side_dir
        points.append((float(p[0]), float(p[1]), float(p[2])))
    return points

def _cube_edges(center: Tuple[float, float, float], size: float) -> Tuple[List[float], List[float], List[float]]:
    """
    Генерирует координаты рёбер куба (как линии) для Scatter3d.
    Возвращает списки x, y, z с None-разделителями между рёбрами.
    """
    cx, cy, cz = center
    s = size / 2.0
    v = [
        (cx - s, cy - s, cz - s), (cx + s, cy - s, cz - s), (cx + s, cy + s, cz - s), (cx - s, cy + s, cz - s),
        (cx - s, cy - s, cz + s), (cx + s, cy - s, cz + s), (cx + s, cy + s, cz + s), (cx - s, cy + s, cz + s),
    ]
    edges = [
        (0,1),(1,2),(2,3),(3,0),
        (4,5),(5,6),(6,7),(7,4),
        (0,4),(1,5),(2,6),(3,7),
    ]
    xs: List[float] = []
    ys: List[float] = []
    zs: List[float] = []
    for a, b in edges:
        xs += [v[a][0], v[b][0], None]
        ys += [v[a][1], v[b][1], None]
        zs += [v[a][2], v[b][2], None]
    return xs, ys, zs

def _box_mesh(center: Tuple[float, float, float], size: Tuple[float, float, float], color: str = "#2E86DE") -> go.Mesh3d:
    """Создает Mesh3d прямоугольного параллелепипеда (звено руки)."""
    cx, cy, cz = center
    sx, sy, sz = size
    dx, dy, dz = sx/2.0, sy/2.0, sz/2.0
    # 8 вершин
    x = [cx-dx, cx+dx, cx+dx, cx-dx, cx-dx, cx+dx, cx+dx, cx-dx]
    y = [cy-dy, cy-dy, cy+dy, cy+dy, cy-dy, cy-dy, cy+dy, cy+dy]
    z = [cz-dz, cz-dz, cz-dz, cz-dz, cz+dz, cz+dz, cz+dz, cz+dz]
    # 12 треугольников
    i = [0, 0, 0, 1, 1, 2, 4, 4, 5, 0, 2, 6]
    j = [1, 3, 4, 2, 5, 3, 5, 7, 6, 4, 6, 7]
    k = [2, 2, 5, 3, 6, 7, 6, 6, 7, 7, 7, 4]
    return go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, color=color, opacity=0.5)

def _oriented_box_mesh(p1: Tuple[float, float, float], p2: Tuple[float, float, float], thickness: float, color: str = "#2E86DE") -> go.Mesh3d:
    """
    Строит ориентированный Mesh3d прямоугольного звена между p1 и p2
    с квадратным сечением thickness x thickness.
    """
    a = np.array(p1, dtype=float)
    b = np.array(p2, dtype=float)
    u = b - a
    L = np.linalg.norm(u)
    if L == 0:
        center = a
        return _box_mesh((float(center[0]), float(center[1]), float(center[2])), (thickness, thickness, thickness), color=color)
    u_dir = u / L
    # Выбираем опорный вектор неколлинеарный u_dir
    ref = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(u_dir, ref)) > 0.95:
        ref = np.array([0.0, 1.0, 0.0])
    v_dir = np.cross(u_dir, ref)
    v_norm = np.linalg.norm(v_dir)
    if v_norm == 0:
        v_dir = np.array([0.0, 1.0, 0.0])
        v_norm = 1.0
    v_dir = v_dir / v_norm
    w_dir = np.cross(u_dir, v_dir)

    center = (a + b) / 2.0
    hu = L / 2.0
    hv = thickness / 2.0
    hw = thickness / 2.0

    # 8 вершин: \pm u, \pm v, \pm w относительно центра
    corners = []
    for su in (-1, 1):
        for sv in (-1, 1):
            for sw in (-1, 1):
                p = center + su * hu * u_dir + sv * hv * v_dir + sw * hw * w_dir
                corners.append(p)
    # Индексация вершин для удобства
    # corners order (u,v,w): (-,-,-),( -,-,+),( -,+,-),( -,+,+),( +,-,-),( +,-,+),( +,+,-),( +,+,+)
    x = [float(p[0]) for p in corners]
    y = [float(p[1]) for p in corners]
    z = [float(p[2]) for p in corners]

    # Треугольники (12) по индексам 0..7
    i = [0, 0, 0, 1, 1, 2, 4, 4, 5, 3, 2, 6]
    j = [1, 2, 4, 3, 5, 3, 5, 6, 7, 7, 6, 7]
    k = [2, 4, 6, 2, 6, 7, 6, 7, 7, 2, 7, 4]

    return go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, color=color, opacity=0.65)

def _oriented_cylinder_mesh(p1: Tuple[float, float, float], p2: Tuple[float, float, float], radius: float, color: str = "#2E86DE", segments: int = 16) -> go.Mesh3d:
    """
    Создает ориентированный цилиндр Mesh3d между точками p1 и p2 с заданным радиусом.
    """
    a = np.array(p1, dtype=float)
    b = np.array(p2, dtype=float)
    axis = b - a
    L = np.linalg.norm(axis)
    if L == 0:
        # Деградация в сферу малого радиуса
        return _box_mesh((float(a[0]), float(a[1]), float(a[2])), (radius, radius, radius), color=color)
    axis_dir = axis / L

    # Базис вокруг оси
    ref = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(axis_dir, ref)) > 0.95:
        ref = np.array([0.0, 1.0, 0.0])
    v = np.cross(axis_dir, ref)
    v /= (np.linalg.norm(v) + 1e-12)
    w = np.cross(axis_dir, v)

    # Кольца по окружности на концах цилиндра
    theta = np.linspace(0, 2 * np.pi, segments, endpoint=False)
    circle = np.cos(theta)[:, None] * v + np.sin(theta)[:, None] * w
    ring1 = a + radius * circle
    ring2 = b + radius * circle

    # Вершины
    vertices = np.vstack([ring1, ring2])
    x = vertices[:, 0].tolist()
    y = vertices[:, 1].tolist()
    z = vertices[:, 2].tolist()

    # Треугольники боковой поверхности
    i_idx = []
    j_idx = []
    k_idx = []
    for k in range(segments):
        k_next = (k + 1) % segments
        # нижнее кольцо k -> верхнее k -> нижнее k+1
        i_idx += [k, k, k + segments]
        j_idx += [k + segments, k_next, k_next + segments]
        k_idx += [k_next + segments, k_next + segments, k_next]

    return go.Mesh3d(x=x, y=y, z=z, i=i_idx, j=j_idx, k=k_idx, color=color, opacity=0.75)

def _sphere_mesh(center: Tuple[float, float, float], radius: float, color: str = "#2E86DE", u_segments: int = 16, v_segments: int = 16) -> go.Mesh3d:
    """Создает сферу Mesh3d в указанном центре и радиусе."""
    cx, cy, cz = center
    u = np.linspace(0, 2 * np.pi, u_segments)
    v = np.linspace(0, np.pi, v_segments)
    x = (cx + radius * np.outer(np.cos(u), np.sin(v))).ravel()
    y = (cy + radius * np.outer(np.sin(u), np.sin(v))).ravel()
    z = (cz + radius * np.outer(np.ones_like(u), np.cos(v))).ravel()
    i_idx = []
    j_idx = []
    k_idx = []
    for a in range(u_segments - 1):
        for b in range(v_segments - 1):
            p1 = a * v_segments + b
            p2 = (a + 1) * v_segments + b
            p3 = p1 + 1
            p4 = p2 + 1
            i_idx += [p1, p1]
            j_idx += [p2, p3]
            k_idx += [p4, p4]
    return go.Mesh3d(x=x.tolist(), y=y.tolist(), z=z.tolist(), i=i_idx, j=j_idx, k=k_idx, color=color, opacity=0.9)

def _rotation_matrix_from_vectors(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Возвращает матрицу поворота, поворачивающую вектор a в вектор b (оба нормализованы)."""
    a = a / (np.linalg.norm(a) + 1e-12)
    b = b / (np.linalg.norm(b) + 1e-12)
    v = np.cross(a, b)
    c = float(np.dot(a, b))
    s = float(np.linalg.norm(v))
    if s < 1e-12:
        # Параллельные или противоположные: если противоположные — поворот на 180° вокруг ортогональной оси
        if c > 0.999999:
            return np.eye(3)
        # Найти любую ось, ортогональную a
        ref = np.array([1.0, 0.0, 0.0]) if abs(a[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
        v = np.cross(a, ref)
        v = v / (np.linalg.norm(v) + 1e-12)
        # Формула Родрига для угла pi: R = I + 2*K^2, где K — матрица перекр. произведения единичного v
        K = np.array([[0, -v[2], v[1]],[v[2], 0, -v[0]],[-v[1], v[0], 0]], dtype=float)
        return np.eye(3) + 2.0 * (K @ K)
    # Формула Родрига: R = I + K*sin + K^2*(1-cos)
    vx, vy, vz = v
    K = np.array([[0, -vz, vy],[vz, 0, -vx],[-vy, vx, 0]], dtype=float)
    R = np.eye(3) + K + K @ K * ((1 - c) / (s * s + 1e-12))
    return R

def _transform_mesh_vertices(xs: List[float], ys: List[float], zs: List[float], R: np.ndarray, t: Tuple[float, float, float]) -> Tuple[List[float], List[float], List[float]]:
    """Применяет поворот R и перенос t к вершинам меша."""
    V = np.vstack([np.asarray(xs, dtype=float), np.asarray(ys, dtype=float), np.asarray(zs, dtype=float)])  # 3xN
    Vp = (R @ V).T + np.asarray(t, dtype=float)  # Nx3
    return Vp[:,0].tolist(), Vp[:,1].tolist(), Vp[:,2].tolist()

def create_3d_visualization(plan: Dict[str, Any]) -> go.Figure:
    """
    Создает 3D визуализацию траекторий роботов с зонами безопасности и коллизиями.
    """
    logger.info("Создание 3D визуализации траекторий")
    
    fig = go.Figure()
    robots = plan["robots"]
    safe_dist = plan.get("safe_dist", 0.0)
    
    # Цвета для роботов
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
    
    # Для каждого робота рисуем траекторию
    for i, robot in enumerate(robots):
        color = colors[i % len(colors)]
        trajectory = robot["trajectory"]
        
        if not trajectory:
            logger.warning(f"Робот {robot['id']} не имеет траектории")
            continue
        
        # Извлекаем координаты
        xs = [p["x"] for p in trajectory]
        ys = [p["y"] for p in trajectory]
        zs = [p["z"] for p in trajectory]
        ts = [p["t"] for p in trajectory]
        
        # Траектория
        fig.add_trace(go.Scatter3d(
            x=xs, y=ys, z=zs,
            mode="lines+markers",
            name=f"Robot {robot['id']}",
            line=dict(width=6, color=color),
            marker=dict(size=4, color=color),
            hovertemplate=f"<b>Robot {robot['id']}</b><br>" +
                         "X: %{x:.3f}<br>" +
                         "Y: %{y:.3f}<br>" +
                         "Z: %{z:.3f}<br>" +
                         "Time: %{customdata:.2f}s<extra></extra>",
            customdata=ts
        ))
        
        # База робота (пьедестал) — визуально более выразительный
        base_xyz = robot.get("base_xyz", [0, 0, 0])
        fig.add_trace(go.Scatter3d(
            x=[base_xyz[0]], y=[base_xyz[1]], z=[base_xyz[2]],
            mode="markers",
            name=f"Base {robot['id']}",
            marker=dict(size=10, color=color, symbol="square"),
            showlegend=False
        ))
        
        # Зоны безопасности (упрощенно - только в ключевых точках)
        tool_clearance = robot.get("tool_clearance", 0.0)
        if tool_clearance > 0:
            # Показываем зоны безопасности только в начале, середине и конце
            key_points = [0, len(trajectory)//2, -1] if len(trajectory) > 2 else [0, -1]
            for idx in key_points:
                if idx == -1:
                    idx = len(trajectory) - 1
                if idx < len(trajectory):
                    x, y, z = xs[idx], ys[idx], zs[idx]
                    fig.add_trace(go.Scatter3d(
                        x=[x], y=[y], z=[z],
                        mode="markers",
                        marker=dict(
                            size=tool_clearance * 30,  # масштаб
                            color=color,
                            opacity=0.2,
                            line=dict(width=1, color=color)
                        ),
                        name=f"Safety zone {robot['id']}" if idx == key_points[0] else "",
                        showlegend=idx == key_points[0]
                    ))
    
    # Объекты (если заданы)
    objects = plan.get("objects", [])
    for obj in objects:
        if obj.get("type", "cube") == "cube":
            center = tuple(obj.get("initial_position", [0, 0, 0]))
            size = float(obj.get("size", 0.1))
            xs, ys, zs = _cube_edges(center, size)
            fig.add_trace(go.Scatter3d(
                x=xs, y=ys, z=zs, mode="lines", name=f"Object {obj.get('id','?')}",
                line=dict(color=obj.get("color", "red"), width=6)
            ))

    # Настройка макета
    makespan = plan.get("makespan", 0.0)
    title = f"Robot Trajectories (makespan = {makespan:.2f} sec)"
    if plan.get("assignment_method"):
        title += f" - {plan['assignment_method']}"
    
    fig.update_layout(
        title=title,
        scene=dict(
            domain=dict(x=[0.35, 0.98], y=[0.15, 0.95]),
            xaxis_title="X (m)",
            yaxis_title="Y (m)",
            zaxis_title="Z (m)",
            aspectmode="cube",
            dragmode="orbit"
        ),
        margin=dict(l=0, r=0, b=0, t=50),
        template="plotly_white",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        uirevision="keep"
    )
    
    logger.info("3D визуализация создана")
    return fig

def create_2d_projection(plan: Dict[str, Any], projection: str = "xy") -> go.Figure:
    """
    Создает 2D проекцию траекторий.
    
    Args:
        plan: План выполнения
        projection: Тип проекции ("xy", "xz", "yz")
    """
    logger.info(f"Создание 2D проекции {projection}")
    
    fig = go.Figure()
    robots = plan["robots"]
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
    
    # Выбираем оси для проекции
    axis_map = {
        "xy": (0, 1, "X", "Y"),
        "xz": (0, 2, "X", "Z"),
        "yz": (1, 2, "Y", "Z")
    }
    
    if projection not in axis_map:
        raise ValueError(f"Неизвестная проекция: {projection}")
    
    axis1, axis2, label1, label2 = axis_map[projection]
    
    for i, robot in enumerate(robots):
        color = colors[i % len(colors)]
        trajectory = robot["trajectory"]
        
        if not trajectory:
            continue
        
        coords = [[p["x"], p["y"], p["z"]] for p in trajectory]
        xs = [coord[axis1] for coord in coords]
        ys = [coord[axis2] for coord in coords]
        
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="lines+markers",
            name=f"Robot {robot['id']}",
            line=dict(width=3, color=color),
            marker=dict(size=6, color=color)
        ))
        
        # База робота
        base_xyz = robot.get("base_xyz", [0, 0, 0])
        fig.add_trace(go.Scatter(
            x=[base_xyz[axis1]], y=[base_xyz[axis2]],
            mode="markers",
            name=f"Base {robot['id']}",
            marker=dict(size=10, color=color, symbol="square"),
            showlegend=False
        ))
    
    makespan = plan.get("makespan", 0.0)
    fig.update_layout(
        title=f"Robot Trajectories - {projection.upper()} Projection (makespan = {makespan:.2f} sec)",
        xaxis_title=f"{label1} (m)",
        yaxis_title=f"{label2} (m)",
        margin=dict(l=0, r=0, b=0, t=50),
        template="plotly_white"
    )
    
    return fig

def create_time_analysis(plan: Dict[str, Any]) -> go.Figure:
    """
    Создает график анализа времени выполнения для каждого робота.
    """
    logger.info("Создание анализа времени")
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Position vs Time", "Velocity vs Time"),
        vertical_spacing=0.1
    )
    
    robots = plan["robots"]
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
    
    for i, robot in enumerate(robots):
        color = colors[i % len(colors)]
        trajectory = robot["trajectory"]
        
        if not trajectory:
            continue
        
        times = [p["t"] for p in trajectory]
        xs = [p["x"] for p in trajectory]
        ys = [p["y"] for p in trajectory]
        zs = [p["z"] for p in trajectory]
        
        # Позиция по времени
        fig.add_trace(go.Scatter(
            x=times, y=xs,
            mode="lines+markers",
            name=f"Robot {robot['id']} X",
            line=dict(color=color, width=2),
            marker=dict(size=4)
        ), row=1, col=1)
        
        # Вычисляем скорость (упрощенно)
        if len(trajectory) > 1:
            velocities = []
            for j in range(1, len(trajectory)):
                dt = times[j] - times[j-1]
                if dt > 0:
                    dx = xs[j] - xs[j-1]
                    dy = ys[j] - ys[j-1]
                    dz = zs[j] - zs[j-1]
                    velocity = np.sqrt(dx**2 + dy**2 + dz**2) / dt
                    velocities.append(velocity)
                else:
                    velocities.append(0)
            
            # Добавляем первую точку
            velocities.insert(0, 0)
            
            fig.add_trace(go.Scatter(
                x=times, y=velocities,
                mode="lines+markers",
                name=f"Robot {robot['id']} Speed",
                line=dict(color=color, width=2),
                marker=dict(size=4)
            ), row=2, col=1)
    
    fig.update_layout(
        title="Time Analysis",
        height=600,
        margin=dict(l=0, r=0, b=0, t=50),
        template="plotly_white"
    )
    
    fig.update_xaxes(title_text="Time (s)", row=2, col=1)
    fig.update_yaxes(title_text="Position (m)", row=1, col=1)
    fig.update_yaxes(title_text="Speed (m/s)", row=2, col=1)
    
    return fig

def show_visualization(plan: Dict[str, Any], visualization_type: str = "3d", progress_callback=None):
    """
    Главная функция визуализации.
    
    Args:
        plan: План выполнения
        visualization_type: Тип визуализации ("3d", "2d_xy", "2d_xz", "2d_yz", "time")
    """
    logger.info(f"Запуск визуализации типа: {visualization_type}")
    
    try:
        if visualization_type == "3d":
            fig = create_3d_visualization(plan)
        elif visualization_type.startswith("2d_"):
            projection = visualization_type.split("_")[1]
            fig = create_2d_projection(plan, projection)
        elif visualization_type == "time":
            fig = create_time_analysis(plan)
        elif visualization_type == "3d_anim":
            # Реал-тайм анимация с использованием кадров по времени
            logger.info("Создание 3D анимации траекторий")
            base_fig = create_3d_visualization({**plan, "robots": []})
            if callable(progress_callback):
                try:
                    progress_callback(5)
                except Exception:
                    pass

            # Подготовка данных по роботам
            robots = plan.get("robots", [])
            colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']

            # Собираем уникальные отметки времени
            time_stride = float(plan.get("anim_time_stride", 0.0))
            if time_stride > 0 and robots:
                t_min = min(wp["t"] for r in robots for wp in r.get("trajectory", []) if r.get("trajectory"))
                t_max = max(wp["t"] for r in robots for wp in r.get("trajectory", []) if r.get("trajectory"))
                n = int(np.ceil((t_max - t_min) / time_stride))
                times = [t_min + i * time_stride for i in range(n + 1)]
            else:
                times: List[float] = sorted({wp["t"] for r in robots for wp in r.get("trajectory", [])})
            if not times:
                raise ValueError("Нет точек траектории для анимации")

            # Ускоряем воспроизведение: даунсэмплим количество кадров
            max_frames = int(plan.get("max_anim_frames", 300))
            if len(times) > max_frames and max_frames > 0:
                step = int(np.ceil(len(times) / max_frames))
                times = times[::step]
            if callable(progress_callback):
                try:
                    progress_callback(10)
                except Exception:
                    pass

            # Начальные следы (плейсхолдеры) — важно: порядок и количество должны совпадать с кадрами
            # 1) TCP траектории (по роботу)
            for i, robot in enumerate(robots):
                color = colors[i % len(colors)]
                base_fig.add_trace(go.Scatter3d(x=[], y=[], z=[], mode="lines+markers",
                                                name=f"Robot {robot['id']}",
                                                line=dict(width=6, color=color),
                                                marker=dict(size=4, color=color)))

            # 2) Рука как линии (по роботу)
            for i, robot in enumerate(robots):
                base_fig.add_trace(go.Scatter3d(x=[], y=[], z=[], mode="lines",
                                                name=f"Arm R{robot['id']}",
                                                line=dict(width=8, color=colors[i % len(colors)]),
                                                showlegend=True))

            # Загрузка внешних мешей роботов (если задано в плане)
            robot_mesh_cfg = plan.get("robot_mesh")
            robot_mesh_data = None
            if load_obj is not None and isinstance(robot_mesh_cfg, dict):
                path = robot_mesh_cfg.get("path")
                scale = float(robot_mesh_cfg.get("scale", 1.0))
                if isinstance(path, str):
                    mesh = load_obj(path, scale)
                    if mesh is not None:
                        robot_mesh_data = mesh  # (xs, ys, zs, is, js, ks)

            # Пользовательское описание руки/хватателя из внешнего файла (облегчённый формат)
            hand_def = None
            hand_cfg = plan.get("hand_definition")
            if load_hand_definition is not None and isinstance(hand_cfg, dict):
                hpath = hand_cfg.get("path")
                hscale = float(hand_cfg.get("scale", 1.0))
                if isinstance(hpath, str):
                    hand_def = load_hand_definition(hpath, hscale)

            # 3D меш-рука (пер-сегментные боксы/цилиндры)
            use_mesh_arm = bool(plan.get("arm_mesh", False))
            arm_style = str(plan.get("arm_style", "box"))  # box|realistic
            mesh_arm_counts = []  # сколько Mesh3d на робота
            if use_mesh_arm:
                for i, robot in enumerate(robots):
                    segs = int(plan.get("arm_segments", 5))
                    cnt = max(2, segs)
                    mesh_arm_counts.append(cnt)
                    for _ in range(cnt):
                        # Добавляем пустой меш-заготовку на каждый сегмент
                        if arm_style == "realistic":
                            placeholder = _oriented_cylinder_mesh(tuple(robot.get("base_xyz", [0,0,0])), tuple(robot.get("base_xyz", [0,0,0])), radius=0.001, color=colors[i % len(colors)], segments=14)
                        else:
                            placeholder = _box_mesh(tuple(robot.get("base_xyz", [0,0,0])), (0.001, 0.001, 0.001), color=colors[i % len(colors)])
                        placeholder.update(opacity=0.0, showlegend=False, name=f"ArmMesh R{robot.get('id')}")
                        base_fig.add_trace(placeholder)
                    # Дополнительные плейсхолдеры: плечо, локоть, запястье (сферы) и простая хваталка (2 элемента)
                    for _ in range(5):
                        sph = _sphere_mesh(tuple(robot.get("base_xyz", [0,0,0])), radius=0.001, color=colors[i % len(colors)])
                        sph.update(opacity=0.0, showlegend=False, name=f"ArmDetail R{robot.get('id')}")
                        base_fig.add_trace(sph)
            else:
                mesh_arm_counts = [0 for _ in robots]

            # Если хотим заменить «двигающуюся дугу» реальной моделью руки — готовим плейсхолдеры меша (по одному на робота)
            use_robot_mesh = robot_mesh_data is not None
            replace_arc_with_model = bool(use_robot_mesh)
            if use_robot_mesh and replace_arc_with_model:
                xs0, ys0, zs0, is0, js0, ks0 = robot_mesh_data
                # Берем первый момент времени для инициализации позы
                t0 = times[0]
                for i, robot in enumerate(robots):
                    base = tuple(robot.get("base_xyz", [0, 0, 0]))
                    tcp0 = _interpolate_position(robot.get("trajectory", []), t0)
                    from_dir = np.array([0.0, 0.0, 1.0], dtype=float)
                    to_vec = np.array([tcp0[0] - base[0], tcp0[1] - base[1], tcp0[2] - base[2]], dtype=float)
                    if np.linalg.norm(to_vec) < 1e-9:
                        R0 = np.eye(3)
                    else:
                        R0 = _rotation_matrix_from_vectors(from_dir, to_vec)
                    txs, tys, tzs = _transform_mesh_vertices(xs0, ys0, zs0, R0, base)
                    placeholder = go.Mesh3d(x=txs, y=tys, z=tzs, i=is0, j=js0, k=ks0,
                                            color=colors[i % len(colors)], opacity=0.6,
                                            name=f"RobotMesh R{robot.get('id')}", showlegend=False)
                    base_fig.add_trace(placeholder)
            objects = plan.get("objects", [])
            for obj in objects:
                base_fig.add_trace(go.Scatter3d(x=[], y=[], z=[], mode="lines",
                                                name=f"Object {obj.get('id','?')}",
                                                line=dict(color=obj.get("color", "red"), width=6)))

            frames = []
            frames_no_arms = []
            for idx, t in enumerate(times):
                frame_data = []
                frame_data_no_arms = []
                for i, robot in enumerate(robots):
                    xs = [p["x"] for p in robot["trajectory"] if p["t"] <= t]
                    ys = [p["y"] for p in robot["trajectory"] if p["t"] <= t]
                    zs = [p["z"] for p in robot["trajectory"] if p["t"] <= t]
                    tcp_trace = go.Scatter3d(x=xs, y=ys, z=zs, mode="lines+markers",
                                             line=dict(width=6, color=colors[i % len(colors)]),
                                             marker=dict(size=4, color=colors[i % len(colors)]),
                                             name=f"Robot {robots[i].get('id')}")
                    frame_data.append(tcp_trace)
                    # Для no_arms — TCP тот же
                    frame_data_no_arms.append(tcp_trace)

                # Манипулятор: звенья base→tcp
                for i, robot in enumerate(robots):
                    base = tuple(robot.get("base_xyz", [0, 0, 0]))
                    tcp = _interpolate_position(robot.get("trajectory", []), t)
                    if replace_arc_with_model and use_robot_mesh:
                        # Поворачиваем и переносим пользовательский меш так, чтобы его ось Z смотрела на TCP
                        try:
                            xs0, ys0, zs0, is_, js_, ks_ = robot_mesh_data
                            from_dir = np.array([0.0, 0.0, 1.0], dtype=float)
                            to_vec = np.array([tcp[0] - base[0], tcp[1] - base[1], tcp[2] - base[2]], dtype=float)
                            if np.linalg.norm(to_vec) < 1e-9:
                                R = np.eye(3)
                            else:
                                R = _rotation_matrix_from_vectors(from_dir, to_vec)
                            txs, tys, tzs = _transform_mesh_vertices(xs0, ys0, zs0, R, base)
                            arm_mesh = go.Mesh3d(x=txs, y=tys, z=tzs, i=is_, j=js_, k=ks_,
                                                 color=colors[i % len(colors)], opacity=0.65,
                                                 name=f"ArmMesh R{robot.get('id')}", showlegend=False)
                            frame_data.append(arm_mesh)
                            frame_data_no_arms.append(arm_mesh)
                        except Exception as heavy_err:
                            # Фоллбэк: рисуем лёгкую линию вместо меша в этом кадре
                            xs_l = [base[0], tcp[0]]
                            ys_l = [base[1], tcp[1]]
                            zs_l = [base[2], tcp[2]]
                            arm_trace = go.Scatter3d(x=xs_l, y=ys_l, z=zs_l, mode="lines",
                                                     line=dict(width=6, color=colors[i % len(colors)]),
                                                     name=f"Arm R{robot.get('id')}", showlegend=False)
                            frame_data.append(arm_trace)
                            # В no_arms — ничего не добавляем
                    else:
                        segs = int(plan.get("arm_segments", 5))
                        arm_model = str(plan.get("arm_model", "curved"))
                        joints = _arm_segments(base, tcp, segments=max(2, segs), bulge=float(plan.get("arm_bulge", 0.18)), model=arm_model)
                        xs_l = []
                        ys_l = []
                        zs_l = []
                        for j in range(len(joints) - 1):
                            xs_l += [joints[j][0], joints[j+1][0], None]
                            ys_l += [joints[j][1], joints[j+1][1], None]
                            zs_l += [joints[j][2], joints[j+1][2], None]
                        arm_trace = go.Scatter3d(x=xs_l, y=ys_l, z=zs_l, mode="lines",
                                                 line=dict(width=8, color=colors[i % len(colors)]),
                                                 name=f"Arm R{robot.get('id')}",
                                                 showlegend=False)
                        frame_data.append(arm_trace)
                        no_arm_trace = arm_trace.to_plotly_json(); no_arm_trace["opacity"] = 0.0
                        frame_data_no_arms.append(go.Scatter3d(**{k: v for k, v in no_arm_trace.items() if k != "type"}))

                    # Mesh-представление (боксы/цилиндры по сегментам) — используем только если НЕ заменяем реальной моделью
                    if use_mesh_arm and not replace_arc_with_model:
                        thickness = float(plan.get("arm_thickness", 0.06))
                        for j in range(len(joints) - 1):
                            p1 = (joints[j][0], joints[j][1], joints[j][2])
                            p2 = (joints[j+1][0], joints[j+1][1], joints[j+1][2])
                            if arm_style == "realistic":
                                mesh = _oriented_cylinder_mesh(p1, p2, radius=thickness * 0.5, color=colors[i % len(colors)], segments=14)
                            else:
                                mesh = _oriented_box_mesh(p1, p2, thickness=thickness, color=colors[i % len(colors)])
                            mesh.update(name=f"ArmMesh R{robot.get('id')}", showlegend=False)
                            frame_data.append(mesh)
                            # Соответствующий слот для no_arms: тот же меш с opacity=0
                            mesh_no = mesh.to_plotly_json()
                            mesh_no["opacity"] = 0.0
                            frame_data_no_arms.append(go.Mesh3d(**{k: v for k, v in mesh_no.items() if k not in ("type",)}))
                        # Если есть внешний hand_definition — рисуем детальный хвататель как линии
                        if hand_def is not None:
                            verts = hand_def.get('vertices', [])
                            segs_idx = hand_def.get('segments', [])
                            if verts and segs_idx:
                                # трансформ: привязываем к TCP и ориентируем по последнему звену (упрощенно: перенос без вращения)
                                dx, dy, dz = tcp
                                hx = []; hy = []; hz = []
                                for a_idx, b_idx in segs_idx:
                                    if 0 <= a_idx < len(verts) and 0 <= b_idx < len(verts):
                                        ax, ay, az = verts[a_idx]
                                        bx, by, bz = verts[b_idx]
                                        hx += [ax + dx, bx + dx, None]
                                        hy += [ay + dy, by + dy, None]
                                        hz += [az + dz, bz + dz, None]
                                frame_data.append(go.Scatter3d(x=hx, y=hy, z=hz, mode="lines", line=dict(width=6, color=colors[i % len(colors)]), name=f"Gripper R{robot.get('id')}", showlegend=False))
                                frame_data_no_arms.append(go.Scatter3d(x=hx, y=hy, z=hz, mode="lines", line=dict(width=0, color=colors[i % len(colors)]), name=f"Gripper R{robot.get('id')}", showlegend=False))
                        # Узлы: плечо, локоть, запястье
                        if len(joints) >= 3:
                            shoulder = joints[0]
                            elbow = joints[len(joints)//2]
                            wrist = joints[-2]
                            sph_r = thickness * 0.9
                            for center in (shoulder, elbow, wrist):
                                sph = _sphere_mesh(center, sph_r, color=colors[i % len(colors)])
                                frame_data.append(sph)
                                sph_no = sph.to_plotly_json(); sph_no["opacity"] = 0.0
                                frame_data_no_arms.append(go.Mesh3d(**{k: v for k, v in sph_no.items() if k != "type"}))
                        # Простая хваталка: две тонкие пластины у TCP
                        tcp_arr = np.array(tcp, dtype=float)
                        prev_arr = np.array(joints[-2], dtype=float)
                        dir_vec = tcp_arr - prev_arr
                        n = np.linalg.norm(dir_vec)
                        if n > 1e-9:
                            dir_vec = dir_vec / n
                        else:
                            dir_vec = np.array([1.0, 0.0, 0.0])
                        ref = np.array([0.0, 0.0, 1.0])
                        side = np.cross(dir_vec, ref)
                        if np.linalg.norm(side) < 1e-6:
                            ref = np.array([0.0, 1.0, 0.0])
                            side = np.cross(dir_vec, ref)
                        side = side / (np.linalg.norm(side) + 1e-12)
                        gap = thickness * 0.6
                        plate_len = thickness * 2.0
                        plate_th = thickness * 0.25
                        p_left1 = tuple(tcp_arr + side * gap)
                        p_left2 = tuple(tcp_arr + side * gap + dir_vec * plate_len)
                        p_right1 = tuple(tcp_arr - side * gap)
                        p_right2 = tuple(tcp_arr - side * gap + dir_vec * plate_len)
                        left_plate = _oriented_box_mesh(p_left1, p_left2, thickness=plate_th, color=colors[i % len(colors)])
                        right_plate = _oriented_box_mesh(p_right1, p_right2, thickness=plate_th, color=colors[i % len(colors)])
                        left_plate.update(showlegend=False); right_plate.update(showlegend=False)
                        frame_data.append(left_plate); frame_data.append(right_plate)
                        lp_no = left_plate.to_plotly_json(); lp_no["opacity"] = 0.0
                        rp_no = right_plate.to_plotly_json(); rp_no["opacity"] = 0.0
                        frame_data_no_arms.append(go.Mesh3d(**{k: v for k, v in lp_no.items() if k != "type"}))
                        frame_data_no_arms.append(go.Mesh3d(**{k: v for k, v in rp_no.items() if k != "type"}))
                    else:
                        # Если меш-рука отключена, но плейсхолдеры были не добавлены — ничего не добавляем и в кадрах
                        pass

                    # Внешний меш уже добавлен статически выше, не добавляем в каждый кадр, чтобы избежать зависаний

                # Объекты: перенос с TCP, если в carry_intervals
                for obj in objects:
                    size = float(obj.get("size", 0.1))
                    center = tuple(obj.get("initial_position", [0, 0, 0]))
                    # Расширенная логика переноса: carry_schedule или carry_intervals
                    schedule = obj.get("carry_schedule")
                    current_carrier_id = None
                    if isinstance(schedule, list) and schedule:
                        for item in schedule:
                            by = item.get("by")
                            interval = item.get("interval", [])
                            if isinstance(interval, list) and len(interval) == 2 and interval[0] <= t <= interval[1] and by is not None:
                                robot = next((r for r in robots if r.get("id") == by), None)
                                if robot is not None:
                                    center = _interpolate_position(robot.get("trajectory", []), t)
                                    current_carrier_id = by
                                break
                    else:
                        carried_by = obj.get("carried_by")
                        intervals = obj.get("carry_intervals", [])
                        if carried_by is not None:
                            for iv in intervals:
                                if len(iv) == 2 and iv[0] <= t <= iv[1]:
                                    robot = next((r for r in robots if r.get("id") == carried_by), None)
                                    if robot is not None:
                                        center = _interpolate_position(robot.get("trajectory", []), t)
                                        current_carrier_id = carried_by
                                    break
                    xs, ys, zs = _cube_edges(center, size)
                    obj_trace = go.Scatter3d(x=xs, y=ys, z=zs, mode="lines",
                                             line=dict(color=obj.get("color", "red"), width=6))
                    frame_data.append(obj_trace)
                    frame_data_no_arms.append(obj_trace)
                    # Подсветка TCP текущего носителя и подпись
                    if current_carrier_id is not None:
                        carrier = next((r for r in robots if r.get("id") == current_carrier_id), None)
                        if carrier is not None:
                            tcp = _interpolate_position(carrier.get("trajectory", []), t)
                            frame_data.append(go.Scatter3d(x=[tcp[0]], y=[tcp[1]], z=[tcp[2]],
                                                           mode="markers+text",
                                                           marker=dict(size=6, color="yellow"),
                                                           text=[f"R{current_carrier_id}"], textposition="top center",
                                                           name=f"Carrier R{current_carrier_id}", showlegend=False))
                frames.append(go.Frame(data=frame_data, name=f"t={t:.2f}|arms"))
                frames_no_arms.append(go.Frame(data=frame_data_no_arms, name=f"t={t:.2f}|noarms"))
                if callable(progress_callback):
                    # 10..95% в процессе подготовки кадров
                    pct = 10 + int(85 * (idx + 1) / max(1, len(times)))
                    try:
                        progress_callback(min(95, max(10, pct)))
                    except Exception:
                        pass

            base_fig.update(frames=frames + frames_no_arms)
            if callable(progress_callback):
                try:
                    progress_callback(97)
                except Exception:
                    pass
            # Кнопки Play/Pause и слайдеры (время и скорость)
            steps = []
            for t in times:
                label = f"t={t:.2f}"
                steps.append({
                    "method": "animate",
                    "label": label,
                    "args": [[f"{label}|arms"], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}]
                })
            base_fig.update_layout(
                updatemenus=[
                    {
                        "type": "buttons",
                        "showactive": True,
                        "x": 0.02,
                        "y": 0.95,
                        "direction": "left",
                        "pad": {"r": 10, "t": 5},
                        "buttons": [
                            {"label": "▶ Старт", "method": "animate", "args": [None, {"frame": {"duration": 80, "redraw": True}, "fromcurrent": True, "mode": "immediate"}]},
                            {"label": "⏸ Пауза", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}]},
                        ]
                    },
                    {
                        "type": "buttons",
                        "showactive": True,
                        # Правее и ниже, чтобы не перекрывать первую группу
                        "x": 0.22,
                        "y": 0.88,
                        "direction": "left",
                        "pad": {"r": 10, "t": 5},
                        "buttons": [
                            {"label": "С руками", "method": "animate", "args": [[ [f"t={t:.2f}|arms" for t in times] ], {"frame": {"duration": 80, "redraw": True}, "mode": "immediate"}]},
                            {"label": "Без рук", "method": "animate", "args": [[ [f"t={t:.2f}|noarms" for t in times] ], {"frame": {"duration": 80, "redraw": True}, "mode": "immediate"}]}
                        ]
                    }
                ],
                # Первый слайдер — по времени
                sliders=[{
                    "active": 0,
                    "currentvalue": {"prefix": "t=", "suffix": "", "visible": True},
                    "pad": {"t": 30},
                    "steps": steps,
                    "x": 0.02,
                    "y": 0.02
                },
                # Второй слайдер — скорость анимации (frame duration)
                {
                    "active": 3,
                    "currentvalue": {"prefix": "Speed: ", "suffix": " ms/frame", "visible": True},
                    "pad": {"t": 10},
                    "steps": [
                        {"label": "200", "method": "animate", "args": [None, {"frame": {"duration": 200, "redraw": True}, "fromcurrent": True, "mode": "immediate"}]},
                        {"label": "120", "method": "animate", "args": [None, {"frame": {"duration": 120, "redraw": True}, "fromcurrent": True, "mode": "immediate"}]},
                        {"label": "80",  "method": "animate", "args": [None, {"frame": {"duration": 80,  "redraw": True}, "fromcurrent": True, "mode": "immediate"}]},
                        {"label": "60",  "method": "animate", "args": [None, {"frame": {"duration": 60,  "redraw": True}, "fromcurrent": True, "mode": "immediate"}]},
                        {"label": "40",  "method": "animate", "args": [None, {"frame": {"duration": 40,  "redraw": True}, "fromcurrent": True, "mode": "immediate"}]},
                        {"label": "20",  "method": "animate", "args": [None, {"frame": {"duration": 20,  "redraw": True}, "fromcurrent": True, "mode": "immediate"}]}
                    ],
                    "x": 0.02,
                    "y": 0.08
                }]
            )

            # Улучшаем UX легенды: явная подсказка и оформление
            base_fig.update_layout(
                legend_title_text="Robots (кликните для скрытия/показа)",
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.02,
                    borderwidth=1,
                    bgcolor="rgba(255,255,255,0.6)",
                    itemclick="toggle",
                    itemdoubleclick="toggleothers"
                ),
                annotations=[dict(
                    text="Подсказка: кликайте по элементам легенды, чтобы скрыть/показать роботов",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.35, y=1.06, xanchor="left", yanchor="bottom",
                    font=dict(size=12, color="#555")
                )]
            )

            fig = base_fig
        else:
            raise ValueError(f"Неизвестный тип визуализации: {visualization_type}")
        
        # Открываем как раньше через HTML, но сохраняем во временный файл и удаляем его позже
        try:
            import tempfile, os, atexit, threading, webbrowser
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f"_viz_{visualization_type}.html")
            tmp_path = tmp.name
            tmp.close()
            plotly_config = {
                "scrollZoom": True,
                "displaylogo": False,
                "displayModeBar": True,
                "staticPlot": False,
                "responsive": True
            }
            fig.write_html(tmp_path, auto_open=False, config=plotly_config)
            logger.info(f"Визуализация записана во временный файл: {tmp_path}")
            # Пытаемся открыть в браузере
            try:
                webbrowser.open(f"file://{os.path.abspath(tmp_path)}")
                logger.info("Визуализация открыта в браузере из временного файла")
            except Exception as browser_error:
                logger.warning(f"Не удалось открыть в браузере: {browser_error}")
                # Фолбэк: пробуем встроенный просмотрщик
                try:
                    fig.show(config=plotly_config)
                except Exception:
                    pass

            # План удаления: на выходе процесса и таймером через 5 минут
            def _safe_unlink(path: str):
                try:
                    if os.path.exists(path):
                        os.unlink(path)
                        logger.info(f"Временный файл визуализации удалён: {path}")
                except Exception as e_del:
                    logger.warning(f"Не удалось удалить временный файл: {e_del}")

            atexit.register(_safe_unlink, tmp_path)
            threading.Timer(300.0, _safe_unlink, args=(tmp_path,)).start()

            if callable(progress_callback):
                try:
                    progress_callback(100)
                except Exception:
                    pass
        except Exception as err:
            logger.error(f"Ошибка показа визуализации: {err}")
            # Последняя попытка — прямой показ без файла
            try:
                fig.show(config=plotly_config)
            except Exception as show_error:
                logger.error(f"Не удалось отобразить визуализацию: {show_error}")
                raise
        
    except Exception as e:
        logger.error(f"Ошибка при создании визуализации: {e}")
        raise

def show_all_visualizations(plan: Dict[str, Any]):
    """
    Показывает все доступные типы визуализации.
    """
    logger.info("Запуск всех типов визуализации")
    
    visualizations = [
        ("3d", "3D траектории"),
        ("2d_xy", "2D проекция XY"),
        ("2d_xz", "2D проекция XZ"),
        ("2d_yz", "2D проекция YZ"),
        ("time", "Анализ времени")
    ]
    
    for viz_type, description in visualizations:
        try:
            logger.info(f"Создание визуализации: {description}")
            show_visualization(plan, viz_type)
        except Exception as e:
            logger.error(f"Ошибка при создании {description}: {e}")
