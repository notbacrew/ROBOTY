from PySide6 import QtWidgets
import sys
import logging
import os
from datetime import datetime
from ui_files.main_window import Ui_MainWindow
from core.parser import parse_input_file
from core.planner import run_planner_algorithm
from core.collision import check_collisions, check_collisions_detailed, get_collision_summary
from viz.visualizer import show_visualization
from core.parser_txt import RobotConfig, Operation
import math

# Настройка системы логирования
def setup_logging():
    """Настройка системы логирования для приложения"""
    # Создаем директорию для логов если её нет
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Формируем имя файла с текущей датой
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"roboty_{timestamp}.log")
    
    # Настройка форматирования
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Настройка корневого логгера
    root_logger = logging.getLogger("ROBOTY")
    root_logger.setLevel(logging.DEBUG)
    
    # Обработчик для файла
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчики
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Настройка логгеров для модулей
    for module_name in ["parser", "parser_txt", "assigner", "planner", "collision", "visualizer"]:
        module_logger = logging.getLogger(f"ROBOTY.{module_name}")
        module_logger.setLevel(logging.DEBUG)
    
    return log_file

class MainApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Настройка логирования
        self.log_file = setup_logging()
        self.logger = logging.getLogger("ROBOTY.main")
        self.logger.info("Запуск приложения ROBOTY")
        
        # Подключение сигналов
        self.pushButton_load.clicked.connect(self.load_file)
        self.pushButton_run.clicked.connect(self.run_planner)
        self.pushButton_viz.clicked.connect(self.open_visualizer)
        self.pushButton_save.clicked.connect(self.save_result)
        
        # Инициализация данных
        self.input_data = None
        self.plan = None
        
        # Вывод информации о логах
        self.textLog.append(f"Логирование настроено. Файл логов: {self.log_file}")
        self.logger.info("Интерфейс инициализирован")

    def save_result(self):
        """Сохранение результата планирования"""
        if not self.plan:
            self.textLog.append("Нет плана для сохранения. Сначала запустите планировщик.")
            self.logger.warning("Попытка сохранения без плана")
            return
        
        self.logger.info("Начинаем сохранение результата")
        
        # Создаем папку для результатов если её нет
        import os
        results_dir = os.path.join(os.path.dirname(__file__), "outputs", "results")
        os.makedirs(results_dir, exist_ok=True)
        
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Сохранить результат", results_dir, 
            "Text Files (*.txt);;JSON Files (*.json)"
        )
        
        if path:
            try:
                if path.endswith('.json'):
                    # Сохранение в JSON формате
                    import json
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump(self.plan, f, indent=2, ensure_ascii=False)
                    self.logger.info(f"План сохранен в JSON: {path}")
                else:
                    # Сохранение в TXT формате
                    from core.parser_txt import save_plan_to_txt
                    robots_waypoints = []
                    for robot in self.plan["robots"]:
                        waypoints = []
                        for wp in robot["trajectory"]:
                            t = wp.get("t", 0.0)
                            x = wp.get("x", 0.0)
                            y = wp.get("y", 0.0)
                            z = wp.get("z", 0.0)
                            waypoints.append((t, x, y, z))
                        robots_waypoints.append((robot["id"], waypoints))
                    
                    makespan = self.plan.get("makespan", 0.0)
                    save_plan_to_txt(path, makespan, robots_waypoints)
                    self.logger.info(f"План сохранен в TXT: {path}")
                
                self.textLog.append(f"Результат сохранён: {path}")
                
            except Exception as e:
                error_msg = f"Ошибка сохранения: {e}"
                self.textLog.append(error_msg)
                self.logger.error(error_msg, exc_info=True)

    def load_file(self):
        """Загрузка входного файла"""
        self.logger.info("Начинаем загрузку файла")
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Выберите входной файл", "data/",
            "JSON Files (*.json);;Text Files (*.txt);;All Files (*)"
        )
        
        if path:
            self.textLog.append(f"Загружен файл: {path}")
            self.logger.info(f"Загружаем файл: {path}")
            
            try:
                self.input_data = parse_input_file(path)
                self.textLog.append("Файл успешно распарсен.")
                self.logger.info("Файл успешно загружен и распарсен")
                
                # Выводим краткую информацию о загруженных данных
                if hasattr(self.input_data, 'robots'):
                    self.textLog.append(f"Загружено роботов: {len(self.input_data.robots)}")
                if hasattr(self.input_data, 'operations'):
                    self.textLog.append(f"Загружено операций: {len(self.input_data.operations)}")
                    
            except Exception as e:
                error_msg = f"Ошибка парсинга: {e}"
                self.textLog.append(error_msg)
                self.logger.error(error_msg, exc_info=True)

    def run_planner(self):
        """Запуск планировщика"""
        self.logger.info("Запуск планировщика")
        self.textLog.append("Запуск планировщика...")
        
        if not self.input_data:
            self.textLog.append("Нет входных данных. Сначала загрузите файл.")
            self.logger.warning("Попытка запуска планировщика без данных")
            return
        
        try:
            self.plan = run_planner_algorithm(self.input_data)
            self.textLog.append("Планировщик завершил работу.")
            self.logger.info("Планировщик успешно завершил работу")
            
            # Выводим информацию о плане
            makespan = self.plan.get("makespan", 0.0)
            self.textLog.append(f"Makespan: {makespan:.2f} сек")
            
            # Проверяем коллизии
            self.textLog.append("Проверка коллизий...")
            collisions = check_collisions_detailed(self.plan)
            
            if collisions:
                self.textLog.append(f"Обнаружено {len(collisions)} коллизий!")
                summary = get_collision_summary(collisions)
                self.textLog.append(f"Затронуто роботов: {summary['affected_robots']}")
                self.logger.warning(f"Обнаружено {len(collisions)} коллизий")
            else:
                self.textLog.append("Коллизий не обнаружено.")
                self.logger.info("Коллизий не обнаружено")
                
        except Exception as e:
            error_msg = f"Ошибка планировщика: {e}"
            self.textLog.append(error_msg)
            self.logger.error(error_msg, exc_info=True)

    def open_visualizer(self):
        """Открытие визуализатора"""
        self.logger.info("Открытие визуализатора")
        self.textLog.append("Открытие визуализатора...")
        
        if not self.plan:
            self.textLog.append("Нет плана для визуализации. Сначала запустите планировщик.")
            self.logger.warning("Попытка визуализации без плана")
            return
        
        try:
            # Добавляем индикатор прогресса
            self.textLog.append("Создание визуализации...")
            self.textLog.repaint()  # Принудительное обновление интерфейса
            
            show_visualization(self.plan)
            self.textLog.append("✅ Визуализация завершена.")
            self.textLog.append("📁 HTML файл создан в папке ROBOTY")
            self.textLog.append("🌐 Откройте файл в браузере для просмотра")
            self.logger.info("Визуализация успешно завершена")
        except Exception as e:
            error_msg = f"❌ Ошибка визуализации: {e}"
            self.textLog.append(error_msg)
            self.textLog.append("💡 Попробуйте запустить планировщик заново")
            self.logger.error(error_msg, exc_info=True)

if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("ROBOTY")
        app.setApplicationVersion("1.0")
        
        window = MainApp()
        window.show()
        
        # Логирование успешного запуска
        logger = logging.getLogger("ROBOTY.main")
        logger.info("Приложение успешно запущено")
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Критическая ошибка при запуске приложения: {e}")
        sys.exit(1)