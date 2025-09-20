from PySide6 import QtWidgets, QtCore, QtGui
import sys
import logging
import os
from datetime import datetime
from ui_files.main_window_improved import Ui_MainWindow
from ui_files.input_generator_dialog import InputGeneratorDialog
from ui_files.styles_final import get_light_style, get_dark_style, get_colors
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
        self.pushButton_clear_logs.clicked.connect(self.clear_logs)
        
        # Кнопка генерации входных данных
        try:
            self.pushButton_input_gen = QtWidgets.QPushButton("📥 Генератор входных данных")
            self.pushButton_input_gen.setObjectName("pushButton_input_gen")
            self.pushButton_input_gen.setToolTip("Создать входной файл (JSON или TXT) и загрузить его")
            if hasattr(self, 'horizontalLayout_file'):
                self.horizontalLayout_file.insertWidget(1, self.pushButton_input_gen)
            self.pushButton_input_gen.clicked.connect(self.open_input_generator)
        except Exception as e:
            self.logger.error(f"Не удалось инициализировать кнопку генератора входных данных: {e}")
        
        # Подключение сигналов для обновления интерфейса
        self.comboBox_assignment_method.currentTextChanged.connect(self.update_genetic_controls)
        
        # Инициализация данных
        self.input_data = None
        self.plan = None
        self.current_theme = 'light'  # Текущая тема
        
        # Применяем начальную тему
        self.apply_theme(self.current_theme)
        
        # Вывод информации о логах
        self.textLog.append(f"Логирование настроено. Файл логов: {self.log_file}")
        self.textLog.append(f"🎨 Текущая тема: {self.current_theme.title()}")
        self.logger.info("Интерфейс инициализирован")
        
        # Обновляем видимость элементов генетического алгоритма
        self.update_genetic_controls()
        
        # Настраиваем переключатель темы
        self.setup_theme_toggle()

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
        
        # Получаем выбранный метод
        assignment_method = self.get_assignment_method()
        self.textLog.append(f"Запуск планировщика с методом: {assignment_method}")
        
        if not self.input_data:
            self.textLog.append("❌ Нет входных данных. Сначала загрузите файл.")
            self.logger.warning("Попытка запуска планировщика без данных")
            return
        
        try:
            # Если выбран генетический алгоритм, используем специальные параметры
            if assignment_method == "genetic":
                genetic_params = self.get_genetic_parameters()
                self.textLog.append(f"🧬 Параметры генетического алгоритма:")
                self.textLog.append(f"   - Размер популяции: {genetic_params['population_size']}")
                self.textLog.append(f"   - Количество поколений: {genetic_params['generations']}")
                
                # Обновляем параметры в генетическом алгоритме
                from core.genetic_algorithm import assign_operations_genetic
                assignments = assign_operations_genetic(
                    self.input_data, 
                    genetic_params['population_size'], 
                    genetic_params['generations']
                )
                
                # Создаем план с генетическими назначениями
                from core.planner import plan_robot_trajectory, calculate_makespan
                robot_trajectories = []
                robot_plans = []
                
                for i, (robot, operations) in enumerate(zip(self.input_data.robots, assignments)):
                    trajectory = plan_robot_trajectory(robot, operations)
                    robot_trajectories.append(trajectory)
                    
                    viz_trajectory = []
                    for wp in trajectory:
                        viz_trajectory.append({
                            "t": wp[0], "x": wp[1], "y": wp[2], "z": wp[3]
                        })
                    
                    robot_plans.append({
                        "id": i + 1,
                        "base_xyz": robot.base_xyz,
                        "trajectory": viz_trajectory,
                        "tool_clearance": robot.tool_clearance,
                        "operations_count": len(operations)
                    })
                
                makespan = calculate_makespan(robot_trajectories)
                self.plan = {
                    "robots": robot_plans,
                    "makespan": makespan,
                    "safe_dist": self.input_data.safe_dist,
                    "assignment_method": assignment_method
                }
            else:
                # Используем стандартный планировщик
                self.plan = run_planner_algorithm(self.input_data, assignment_method)
            
            self.textLog.append("✅ Планировщик завершил работу.")
            self.logger.info("Планировщик успешно завершил работу")
            
            # Выводим информацию о плане
            makespan = self.plan.get("makespan", 0.0)
            self.textLog.append(f"📊 Makespan: {makespan:.2f} сек")
            
            # Проверяем коллизии
            self.textLog.append("🔍 Проверка коллизий...")
            collisions = check_collisions_detailed(self.plan)
            
            if collisions:
                self.textLog.append(f"⚠️ Обнаружено {len(collisions)} коллизий!")
                summary = get_collision_summary(collisions)
                self.textLog.append(f"🤖 Затронуто роботов: {summary['affected_robots']}")
                self.logger.warning(f"Обнаружено {len(collisions)} коллизий")
            else:
                self.textLog.append("✅ Коллизий не обнаружено.")
                self.logger.info("Коллизий не обнаружено")
                
        except Exception as e:
            error_msg = f"❌ Ошибка планировщика: {e}"
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

    def update_genetic_controls(self):
        """Обновляет видимость элементов управления генетическим алгоритмом"""
        is_genetic = self.comboBox_assignment_method.currentText().startswith("Genetic")
        self.label_genetic_population.setVisible(is_genetic)
        self.spinBox_population_size.setVisible(is_genetic)
        self.label_genetic_generations.setVisible(is_genetic)
        self.spinBox_generations.setVisible(is_genetic)

    def clear_logs(self):
        """Очистка логов"""
        self.textLog.clear()
        self.textLog.append("Логи очищены.")
        self.logger.info("Логи очищены пользователем")

    def get_assignment_method(self):
        """Возвращает выбранный метод назначения операций"""
        method_map = {
            "Round Robin (по очереди)": "round_robin",
            "Balanced (балансировка нагрузки)": "balanced",
            "Distance Based (по расстоянию)": "distance_based",
            "Genetic Algorithm (генетический)": "genetic"
        }
        return method_map.get(self.comboBox_assignment_method.currentText(), "balanced")

    def get_genetic_parameters(self):
        """Возвращает параметры генетического алгоритма"""
        return {
            "population_size": self.spinBox_population_size.value(),
            "generations": self.spinBox_generations.value()
        }

    def apply_theme(self, theme_name):
        """Применяет указанную тему глобально ко всему приложению (включая диалоги)"""
        try:
            if theme_name == 'light':
                style = get_light_style()
                self.current_theme = 'light'
            elif theme_name == 'dark':
                style = get_dark_style()
                self.current_theme = 'dark'
            else:
                style = get_light_style()
                self.current_theme = 'light'

            # Применяем стили ко всему приложению, чтобы все окна/диалоги синхронизировались
            app = QtWidgets.QApplication.instance()
            if app is not None:
                app.setStyleSheet(style)
            else:
                # fallback: применить к окну
                self.setStyleSheet(style)
            
            # Обновляем иконку переключателя темы если есть
            if hasattr(self, 'pushButton_theme_toggle'):
                if self.current_theme == 'light':
                    self.pushButton_theme_toggle.setText("🌙")
                    self.pushButton_theme_toggle.setToolTip("Переключить на темную тему")
                else:
                    self.pushButton_theme_toggle.setText("☀️")
                    self.pushButton_theme_toggle.setToolTip("Переключить на светлую тему")
            
            self.logger.info(f"Применена тема: {theme_name}")
            
        except Exception as e:
            self.logger.error(f"Ошибка применения темы {theme_name}: {e}")

    def toggle_theme(self):
        """Переключает между светлой и темной темой"""
        new_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme(new_theme)
        
        # Обновляем лог
        self.textLog.append(f"🎨 Переключено на {new_theme.title()} тему")
        self.logger.info(f"Переключение темы: {self.current_theme} -> {new_theme}")

    def open_input_generator(self):
        """Открывает окно генерации входных данных и при необходимости загружает файл"""
        try:
            dlg = InputGeneratorDialog(self)
            # Сброс локального стиля, чтобы наследовать глобальную тему приложения
            dlg.setStyleSheet("")
            if dlg.exec() == QtWidgets.QDialog.Accepted and getattr(dlg, 'saved_path', None):
                path = dlg.saved_path
                self.textLog.append(f"📥 Входной файл создан: {path}")
                self.logger.info(f"Создан входной файл: {path}")
                if getattr(dlg, 'load_into_app', False):
                    try:
                        self.input_data = parse_input_file(path)
                        self.textLog.append("✅ Входные данные загружены в приложение.")
                        if hasattr(self.input_data, 'robots'):
                            self.textLog.append(f"Загружено роботов: {len(self.input_data.robots)}")
                        if hasattr(self.input_data, 'operations'):
                            self.textLog.append(f"Загружено операций: {len(self.input_data.operations)}")
                    except Exception as e:
                        error_msg = f"Ошибка загрузки входного файла: {e}"
                        self.textLog.append(error_msg)
                        self.logger.error(error_msg, exc_info=True)
        except Exception as e:
            error_msg = f"Ошибка генератора входных данных: {e}"
            self.textLog.append(error_msg)
            self.logger.error(error_msg, exc_info=True)

    def setup_theme_toggle(self):
        """Настраивает переключатель темы"""
        # Создаем кнопку переключения темы
        self.pushButton_theme_toggle = QtWidgets.QPushButton("🌙")
        self.pushButton_theme_toggle.setProperty("class", "theme-toggle")
        self.pushButton_theme_toggle.clicked.connect(self.toggle_theme)
        self.pushButton_theme_toggle.setToolTip("Переключить тему")
        
        # Создаем отдельный контейнер для кнопки темы в правом верхнем углу
        self.theme_container = QtWidgets.QWidget()
        self.theme_layout = QtWidgets.QHBoxLayout(self.theme_container)
        self.theme_layout.setContentsMargins(0, 0, 0, 0)
        self.theme_layout.addStretch()
        self.theme_layout.addWidget(self.pushButton_theme_toggle)
        
        # Добавляем контейнер в главный layout
        self.verticalLayout_main.addWidget(self.theme_container)

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