import matplotlib.pyplot as plt
import json

with open('data/example_schedule.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def plot_trajectories(robots):
    # Можно использовать ту же реализацию, что и show_visualization
    show_visualization(robots)

def load_output_file(filepath):
    robots = []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    robot = None
    for line in lines:
        if line.startswith("Robot"):
            if robot:
                robots.append(robot)
            robot = {'waypoints': []}
        elif line.strip() and not line.startswith("Makespan"):
            parts = line.strip().split()
            if len(parts) == 4:
                t, x, y, z = map(float, parts)
                robot['waypoints'].append((x, y, z))
    if robot:
        robots.append(robot)
    return robots

def show_visualization(robots):
    for idx, robot in enumerate(robots):
        if robot['waypoints']:
            xs, ys, zs = zip(*robot['waypoints'])
            plt.plot(xs, ys, label=f'Robot {idx+1}')         # добавлен label
            plt.scatter(xs, ys, label=f'Points {idx+1}')     # добавлен label
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Robot Trajectories')
    plt.legend()
    plt.grid()
    plt.show()

