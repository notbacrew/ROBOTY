import logging
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, Any, List, Tuple

# Настройка логгера для модуля визуализации
logger = logging.getLogger("ROBOTY.visualizer")

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
        
        # База робота
        base_xyz = robot.get("base_xyz", [0, 0, 0])
        fig.add_trace(go.Scatter3d(
            x=[base_xyz[0]], y=[base_xyz[1]], z=[base_xyz[2]],
            mode="markers",
            name=f"Base {robot['id']}",
            marker=dict(size=8, color=color, symbol="square"),
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
            xaxis_title="X (m)",
            yaxis_title="Y (m)",
            zaxis_title="Z (m)",
            aspectmode="cube"
        ),
        margin=dict(l=0, r=0, b=0, t=50),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
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
        margin=dict(l=0, r=0, b=0, t=50)
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
        margin=dict(l=0, r=0, b=0, t=50)
    )
    
    fig.update_xaxes(title_text="Time (s)", row=2, col=1)
    fig.update_yaxes(title_text="Position (m)", row=1, col=1)
    fig.update_yaxes(title_text="Speed (m/s)", row=2, col=1)
    
    return fig

def show_visualization(plan: Dict[str, Any], visualization_type: str = "3d"):
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

            # Начальные следы (пустые)
            for i, robot in enumerate(robots):
                color = colors[i % len(colors)]
                base_fig.add_trace(go.Scatter3d(x=[], y=[], z=[], mode="lines+markers",
                                                name=f"Robot {robot['id']}",
                                                line=dict(width=6, color=color),
                                                marker=dict(size=4, color=color)))

            # Следы для манипулятора и объектов
            for i, robot in enumerate(robots):
                base_fig.add_trace(go.Scatter3d(x=[], y=[], z=[], mode="lines",
                                                name=f"Arm {robot['id']}",
                                                line=dict(width=8, color=colors[i % len(colors)]),
                                                showlegend=False))
            objects = plan.get("objects", [])
            for obj in objects:
                base_fig.add_trace(go.Scatter3d(x=[], y=[], z=[], mode="lines",
                                                name=f"Object {obj.get('id','?')}",
                                                line=dict(color=obj.get("color", "red"), width=6)))

            frames = []
            for t in times:
                frame_data = []
                for i, robot in enumerate(robots):
                    xs = [p["x"] for p in robot["trajectory"] if p["t"] <= t]
                    ys = [p["y"] for p in robot["trajectory"] if p["t"] <= t]
                    zs = [p["z"] for p in robot["trajectory"] if p["t"] <= t]
                    frame_data.append(go.Scatter3d(x=xs, y=ys, z=zs, mode="lines+markers",
                                                   line=dict(width=6, color=colors[i % len(colors)]),
                                                   marker=dict(size=4, color=colors[i % len(colors)])))

                # Манипулятор: звенья base→tcp
                for i, robot in enumerate(robots):
                    base = tuple(robot.get("base_xyz", [0, 0, 0]))
                    tcp = _interpolate_position(robot.get("trajectory", []), t)
                    segs = int(plan.get("arm_segments", 5))
                    arm_model = str(plan.get("arm_model", "curved"))
                    joints = _arm_segments(base, tcp, segments=max(2, segs), bulge=float(plan.get("arm_bulge", 0.18)), model=arm_model)
                    xs = []
                    ys = []
                    zs = []
                    for j in range(len(joints) - 1):
                        xs += [joints[j][0], joints[j+1][0], None]
                        ys += [joints[j][1], joints[j+1][1], None]
                        zs += [joints[j][2], joints[j+1][2], None]
                    frame_data.append(go.Scatter3d(x=xs, y=ys, z=zs, mode="lines",
                                                   line=dict(width=8, color=colors[i % len(colors)])))

                # Объекты: перенос с TCP, если в carry_intervals
                for obj in objects:
                    size = float(obj.get("size", 0.1))
                    center = tuple(obj.get("initial_position", [0, 0, 0]))
                    carried_by = obj.get("carried_by")
                    intervals = obj.get("carry_intervals", [])
                    is_carried = False
                    if carried_by is not None:
                        for iv in intervals:
                            if len(iv) == 2 and iv[0] <= t <= iv[1]:
                                is_carried = True
                                break
                    if is_carried:
                        robot = next((r for r in robots if r.get("id") == carried_by), None)
                        if robot is not None:
                            center = _interpolate_position(robot.get("trajectory", []), t)
                    xs, ys, zs = _cube_edges(center, size)
                    frame_data.append(go.Scatter3d(x=xs, y=ys, z=zs, mode="lines",
                                                   line=dict(color=obj.get("color", "red"), width=6)))
                frames.append(go.Frame(data=frame_data, name=f"t={t:.2f}"))

            base_fig.update(frames=frames)
            # Кнопки Play/Pause/Speed и слайдер времени
            steps = []
            for f in base_fig.frames:
                steps.append({
                    "method": "animate",
                    "label": f.name,
                    "args": [[f.name], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}]
                })
            base_fig.update_layout(
                updatemenus=[
                    {
                        "type": "buttons",
                        "showactive": True,
                        "x": 0.02,
                        "y": 0.95,
                        "buttons": [
                            {"label": "▶ Старт", "method": "animate", "args": [None, {"frame": {"duration": 80, "redraw": True}, "fromcurrent": True}]},
                            {"label": "⏸ Пауза", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}]},
                        ]
                    },
                    {
                        "type": "buttons",
                        "showactive": True,
                        "x": 0.28,
                        "y": 0.95,
                        "buttons": [
                            {"label": "🐢 Медленно", "method": "animate", "args": [None, {"frame": {"duration": 160, "redraw": True}, "fromcurrent": True}]},
                            {"label": "⚡ Быстро", "method": "animate", "args": [None, {"frame": {"duration": 30, "redraw": True}, "fromcurrent": True}]},
                        ]
                    }
                ],
                sliders=[{
                    "active": 0,
                    "currentvalue": {"prefix": "t=", "suffix": "", "visible": True},
                    "pad": {"t": 30},
                    "steps": steps,
                    "x": 0.05,
                    "y": 0.02
                }]
            )

            fig = base_fig
        else:
            raise ValueError(f"Неизвестный тип визуализации: {visualization_type}")
        
        # Сначала сохраняем в HTML файл (более надежно)
        try:
            import os
            timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Создаем папку для визуализаций если её нет
            viz_dir = os.path.join(os.path.dirname(__file__), "..", "outputs", "visualizations")
            os.makedirs(viz_dir, exist_ok=True)
            
            html_file = os.path.join(viz_dir, f"visualization_{visualization_type}_{timestamp}.html")
            fig.write_html(html_file, auto_open=False)
            logger.info(f"Визуализация сохранена в файл: {html_file}")
            print(f"✅ Визуализация сохранена в файл: {html_file}")
            print(f"📁 Полный путь: {os.path.abspath(html_file)}")
            print("🌐 Откройте этот файл в браузере для просмотра")
            
            # Пытаемся открыть в браузере (необязательно)
            try:
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(html_file)}")
                logger.info("Визуализация открыта в браузере")
            except Exception as browser_error:
                logger.warning(f"Не удалось открыть в браузере: {browser_error}")
                print("⚠️  Не удалось автоматически открыть в браузере")
                print("   Откройте файл вручную в любом браузере")
                
        except Exception as save_error:
            logger.error(f"Не удалось сохранить визуализацию: {save_error}")
            print(f"❌ Ошибка сохранения визуализации: {save_error}")
            # Последняя попытка - показать в браузере
            try:
                fig.show()
                logger.info("Визуализация отображена в браузере")
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
