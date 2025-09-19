from PySide6 import QtWidgets
import sys
from ui_files.main_window import Ui_MainWindow
from core.parser import parse_input_file
from core.planner import assign_operations, generate_waypoints
from core.collision import check_collision
from viz.visualizer import show_visualization, load_output_file

def write_output_file(filepath, waypoints):
    makespan = max(wp[-1]['time'] if wp else 0 for wp in waypoints)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Makespan: {makespan:.2f}\n")
        for idx, wp in enumerate(waypoints):
            f.write(f"Robot {idx+1}: {len(wp)} waypoints\n")
            for point in wp:
                x, y, z = point['pos']
                t = point['time']
                f.write(f"{t:.2f} {x:.2f} {y:.2f} {z:.2f}\n")
            f.write("\n")

class MainApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_load.clicked.connect(self.load_file)
        self.pushButton_run.clicked.connect(self.run_planner)
        self.pushButton_viz.clicked.connect(self.open_visualizer)
        self.input_data = None
        self.plan = None

    def load_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Выберите входной файл", "data/")
        if path:
            self.textLog.append(f"Загружен файл: {path}")
            try:
                self.input_data = parse_input_file(path)
                self.textLog.append("Файл успешно распарсен.")
            except Exception as e:
                self.textLog.append(f"Ошибка парсинга: {e}")

    def run_planner(self):
        self.textLog.append("Запуск планировщика...")
        if not self.input_data:
            self.textLog.append("Нет входных данных.")
            return
        robot_ops = assign_operations(self.input_data['K'], self.input_data['operations'])
        waypoints = generate_waypoints(robot_ops, self.input_data['joints'])
        collision_free = check_collision(waypoints, self.input_data['tool_clearance'], self.input_data['safe_dist'])
        if collision_free:
            self.textLog.append("Коллизий не обнаружено.")
        else:
            self.textLog.append("Обнаружена коллизия!")
        write_output_file('data/output.txt', waypoints)
        self.textLog.append("Результаты записаны в data/output.txt.")
        self.plan = waypoints

    def open_visualizer(self):
        try:
            robots = load_output_file('data/output.txt')
            show_visualization(robots)
        except Exception as e:
            self.textLog.append(f"Ошибка визуализации: {e}")

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainApp()
    window.show()
    app.exec()

