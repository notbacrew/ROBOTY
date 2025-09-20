import logging
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, Any, List, Tuple

# Настройка логгера для модуля визуализации
logger = logging.getLogger("ROBOTY.visualizer")

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
