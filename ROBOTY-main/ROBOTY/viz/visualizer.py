import plotly.graph_objects as go

def show_visualization(plan):
    """
    Визуализация траекторий роботов.
    На вход подаётся объект плана.
    """
    data = plan  # теперь план — это уже объект, а не путь

    fig = go.Figure()

    # Для каждого робота рисуем траекторию
    for robot in data["robots"]:
        xs = [p["x"] for p in robot["trajectory"]]
        ys = [p["y"] for p in robot["trajectory"]]
        zs = [p["z"] for p in robot["trajectory"]]

        fig.add_trace(go.Scatter3d(
            x=xs, y=ys, z=zs,
            mode="lines+markers",
            name=f"Robot {robot['id']}",
            line=dict(width=4),
            marker=dict(size=4)
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

