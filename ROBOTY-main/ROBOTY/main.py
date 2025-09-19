from PySide6 import QtWidgets
import sys
from ui_files.main_window import Ui_MainWindow
from core.parser import parse_input_file
from core.planner import run_planner_algorithm
from core.collision import check_collisions
from viz.visualizer import show_visualization

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

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())