import plotly.graph_objects as go

def show_visualization(plan):
    """
    Визуализация траекторий роботов.
    На вход подаётся объект плана.
    """
    data = plan  # теперь план — это уже объект, а не путь

    fig = go.Figure()

    # Для каждого робота рисуем траекторию и зоны безопасности
    for robot in data["robots"]:
        xs = [p["x"] + robot["base_xyz"][0] for p in robot["trajectory"]]
        ys = [p["y"] + robot["base_xyz"][1] for p in robot["trajectory"]]
        zs = [p["z"] + robot["base_xyz"][2] for p in robot["trajectory"]]

        fig.add_trace(go.Scatter3d(
            x=xs, y=ys, z=zs,
            mode="lines+markers",
            name=f"Robot {robot['id']}",
            line=dict(width=4),
            marker=dict(size=4)
        ))

        # Отрисовка сфер безопасности вокруг каждого waypoint
        if "tool_clearance" in robot:
            for x, y, z in zip(xs, ys, zs):
                fig.add_trace(go.Scatter3d(
                    x=[x], y=[y], z=[z],
                    mode="markers",
                    marker=dict(
                        size=robot["tool_clearance"]*20,  # масштаб
                        color="rgba(200,100,100,0.2)"
                    ),
                    showlegend=False
                ))

    # Индикация нарушений safe_dist (упрощённо)
    if "safe_dist" in data:
        # Проверяем все пары точек
        for i, r1 in enumerate(data["robots"]):
            for j, r2 in enumerate(data["robots"]):
                if i >= j:
                    continue
                for p1 in r1["trajectory"]:
                    for p2 in r2["trajectory"]:
                        x1 = p1["x"] + r1["base_xyz"][0]
                        y1 = p1["y"] + r1["base_xyz"][1]
                        z1 = p1["z"] + r1["base_xyz"][2]
                        x2 = p2["x"] + r2["base_xyz"][0]
                        y2 = p2["y"] + r2["base_xyz"][1]
                        z2 = p2["z"] + r2["base_xyz"][2]
                        dist = ((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2)**0.5
                        min_dist = data["safe_dist"] + r1.get("tool_clearance",0) + r2.get("tool_clearance",0)
                        if dist < min_dist:
                            fig.add_trace(go.Scatter3d(
                                x=[x1, x2],
                                y=[y1, y2],
                                z=[z1, z2],
                                mode="lines",
                                line=dict(color="red", width=8, dash="dot"),
                                name="Collision!"
                            ))

    # Добавим подпись makespan
    makespan = data.get("makespan", None)
    if makespan is not None:
        fig.update_layout(
            title=f"Robot Trajectories (makespan = {makespan:.2f} sec)"
        )
    else:
        fig.update_layout(title="Robot Trajectories")

    fig.update_layout(
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z"
        ),
        margin=dict(l=0, r=0, b=0, t=30)
    )

    fig.show()
