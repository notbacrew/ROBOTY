from PySide6 import QtWidgets
import sys
from ui_files.main_window import Ui_MainWindow
from core.parser import parse_input_file
from core.planner import run_planner_algorithm
from core.collision import check_collisions
from viz.visualizer import show_visualization
from core.parser_txt import RobotConfig, Operation
import math

class MainApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_load.clicked.connect(self.load_file)
        self.pushButton_run.clicked.connect(self.run_planner)
        self.pushButton_viz.clicked.connect(self.open_visualizer)
        self.input_data = None
        self.plan = None
        self.pushButton_save.clicked.connect(self.save_result)

    def save_result(self):
        if not self.plan:
            self.textLog.append("Нет плана для сохранения. Сначала запустите планировщик.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Сохранить результат", "result.txt", "Text Files (*.txt)")
        if path:
            try:
                # Пример: формируем структуру для сохранения
                from core.parser_txt import save_plan_to_txt
                # Предполагается, что self.plan содержит 'makespan' и 'robots' с 'trajectory'
                robots_waypoints = []
                for robot in self.plan["robots"]:
                    waypoints = []
                    self.textLog.append(str(robot["trajectory"]))
                    for i, wp in enumerate(robot["trajectory"]):
                        t = wp.get("t", float(i))
                        x = wp.get("x", 0.0)
                        y = wp.get("y", 0.0)
                        z = wp.get("z", 0.0)
                        waypoints.append((t, x, y, z))
                    robots_waypoints.append((robot["id"], waypoints))
                makespan = self.plan.get("makespan", 0.0)
                save_plan_to_txt(path, makespan, robots_waypoints)
                self.textLog.append(f"Результат сохранён: {path}")
            except Exception as e:
                self.textLog.append(f"Ошибка сохранения: {e}")

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
            self.textLog.append("Нет входных данных. Сначала загрузите файл.")
            return
        try:
            self.plan = run_planner_algorithm(self.input_data)
            self.textLog.append("Планировщик завершил работу.")
            if check_collisions(self.plan):
                self.textLog.append("Обнаружены коллизии!")
            else:
                self.textLog.append("Коллизий не обнаружено.")
        except Exception as e:
            self.textLog.append(f"Ошибка планировщика: {e}")

    def open_visualizer(self):
        self.textLog.append("Открытие визуализатора...")
        if not self.plan:
            self.textLog.append("Нет плана для визуализации. Сначала запустите планировщик.")
            return
        try:
            show_visualization(self.plan)
            self.textLog.append("Визуализация завершена.")
        except Exception as e:
            self.textLog.append(f"Ошибка визуализации: {e}")

def check_kinematics(robot: RobotConfig, point: tuple) -> bool:
    # ...код функции...
    pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())