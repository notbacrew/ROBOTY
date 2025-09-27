# -*- coding: utf-8 -*-
"""
Десктопное приложение ROBOTY с оптимизациями для больших нагрузок
"""

from PySide6 import QtWidgets, QtCore, QtGui
import sys
import logging
import os
import multiprocessing
import gc
from datetime import datetime
from typing import Dict, Any, Optional
import numpy as np

# Попытка импорта psutil с fallback
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil не установлен. Некоторые функции мониторинга будут недоступны.")

from ui_files.main_window_improved import Ui_MainWindow
from ui_files.input_generator_dialog import InputGeneratorDialog
from ui_files.styles_final import get_light_style, get_dark_style
from core.parser import parse_input_file
from core.planner import run_planner_algorithm
from core.collision import check_collisions, check_collisions_detailed, get_collision_summary
from viz.visualizer import show_visualization
from core.safety import enforce_online_safety
from core.parser_txt import RobotConfig, Operation
from core.performance_optimizer import (
    apply_performance_optimizations, 
    get_system_performance_info,
    optimize_for_scene,
    monitor_memory,
    cleanup_performance_resources
)


class PerformanceMonitor:
    """Монитор производительности системы"""
    
    def __init__(self):
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.process_count = 0
        self.last_update = datetime.now()
    
    def update(self):
        """Обновляет метрики производительности"""
        try:
            if PSUTIL_AVAILABLE:
                self.cpu_usage = psutil.cpu_percent(interval=0.1)
                self.memory_usage = psutil.virtual_memory().percent
                self.process_count = len(psutil.pids())
            else:
                # Fallback значения без psutil
                self.cpu_usage = 0.0
                self.memory_usage = 0.0
                self.process_count = 0
            self.last_update = datetime.now()
        except Exception:
            pass
    
    def get_system_info(self) -> Dict[str, Any]:
        """Возвращает информацию о системе"""
        if PSUTIL_AVAILABLE:
            memory = psutil.virtual_memory()
            return {
                "cpu_cores": multiprocessing.cpu_count(),
                "cpu_usage": self.cpu_usage,
                "memory_total": memory.total,
                "memory_available": memory.available,
                "memory_usage": self.memory_usage,
                "process_count": self.process_count
            }
        else:
            # Fallback без psutil
            return {
                "cpu_cores": multiprocessing.cpu_count(),
                "cpu_usage": 0.0,
                "memory_total": 0,
                "memory_available": 0,
                "memory_usage": 0.0,
                "process_count": 0
            }


class OptimizedWorker(QtCore.QObject):
    """Оптимизированный воркер для тяжелых вычислений"""
    
    finished = QtCore.Signal(dict)
    error = QtCore.Signal(str)
    progress = QtCore.Signal(int)
    memory_warning = QtCore.Signal(str)
    
    def __init__(self, input_data, assignment_method, genetic_params=None):
        super().__init__()
        self.input_data = input_data
        self.assignment_method = assignment_method
        self.genetic_params = genetic_params or {}
        self.monitor = PerformanceMonitor()
    
    @QtCore.Slot()
    def run(self):
        """Выполняет планирование с мониторингом ресурсов"""
        try:
            # Принудительная сборка мусора перед началом
            gc.collect()
            
            # Мониторинг памяти с использованием нового модуля
            memory_info = monitor_memory()
            if memory_info.get('system_memory_percent', 0) > 80:
                self.memory_warning.emit(f"Высокое использование памяти: {memory_info['system_memory_percent']:.1f}%")
            
            self.progress.emit(10)
            
            # Выполняем планирование
            if self.assignment_method == "genetic":
                from core.genetic_algorithm import assign_operations_genetic
                assignments = assign_operations_genetic(
                    self.input_data, 
                    self.genetic_params.get('population_size', 50), 
                    self.genetic_params.get('generations', 100)
                )
                
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
                plan = {
                    "robots": robot_plans,
                    "makespan": makespan,
                    "safe_dist": self.input_data.safe_dist,
                    "assignment_method": self.assignment_method
                }
            else:
                plan = run_planner_algorithm(self.input_data, self.assignment_method)
            
            self.progress.emit(70)
            
            # Проверка коллизий с оптимизацией
            collisions = check_collisions_detailed(plan)
            if collisions:
                plan = enforce_online_safety(plan, time_step=0.05, pause_duration=0.6)
            
            self.progress.emit(90)
            
            # Финальная сборка мусора
            gc.collect()
            
            self.progress.emit(100)
            self.finished.emit(plan)
            
        except Exception as e:
            self.error.emit(str(e))


class DesktopApp(QtWidgets.QMainWindow, Ui_MainWindow):
    """Оптимизированное десктопное приложение для больших нагрузок"""
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Настройка логирования
        self.log_file = self.setup_logging()
        self.logger = logging.getLogger("ROBOTY.desktop")
        self.logger.info("Запуск оптимизированного десктопного приложения")
        
        # Инициализация данных
        self.input_data = None
        self.plan = None
        self.current_theme = 'dark'
        self.performance_monitor = PerformanceMonitor()
        
        # Настройка UI
        self.setup_ui()
        self.apply_theme(self.current_theme)
        
        # Оптимизации для больших нагрузок
        self.setup_performance_optimizations()
        
        self.logger.info("Десктопное приложение инициализировано")
    
    def setup_logging(self):
        """Настройка системы логирования"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"desktop_app_{timestamp}.log")
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        root_logger = logging.getLogger("ROBOTY_DESKTOP")
        root_logger.setLevel(logging.DEBUG)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        return log_file
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Подключение сигналов
        self.pushButton_load.clicked.connect(self.load_file)
        self.pushButton_run.clicked.connect(self.run_planner_optimized)
        self.pushButton_viz.clicked.connect(self.open_visualizer_optimized)
        self.pushButton_save.clicked.connect(self.save_result)
        self.pushButton_clear_logs.clicked.connect(self.clear_logs)
        self.pushButton_input_gen.clicked.connect(self.open_input_generator)
        
        # Подключение действий меню
        self.actionLoad.triggered.connect(self.load_file)
        self.actionSave.triggered.connect(self.save_result)
        self.actionSaveAs.triggered.connect(self.save_result_as)
        self.actionExit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.show_about)
        
        # Обновление интерфейса
        self.comboBox_assignment_method.currentTextChanged.connect(self.update_genetic_controls)
        self.update_genetic_controls()
        
        # Настройка переключателя темы
        self.setup_theme_toggle()
        
        # Инициализация индикаторов
        if hasattr(self, 'progressBar_status'):
            self.progressBar_status.setVisible(False)
        
        # Синхронизация видимости
        if hasattr(self, 'checkBox_arm_mesh'):
            self.checkBox_arm_mesh.stateChanged.connect(self.sync_model_selector_visibility)
            self.sync_model_selector_visibility()
        
        # Хранилище фоновых задач
        self._worker_thread = None
        self._worker = None
        
        # Информация о системе
        self.textLog.append("🖥️ Десктопное приложение ROBOTY запущено")
        self.textLog.append(f"📊 Логирование: {self.log_file}")
        self.textLog.append(f"🎨 Тема: {self.current_theme.title()}")
        
        # Показываем информацию о системе
        self.show_system_info()
    
    def setup_performance_optimizations(self):
        """Настройка оптимизаций производительности"""
        try:
            # Применяем системные оптимизации
            optimizations = apply_performance_optimizations()
            
            self.textLog.append("🚀 Применены системные оптимизации:")
            for opt in optimizations.keys():
                self.textLog.append(f"   ✓ {opt}")
            
            self.logger.info(f"Применено оптимизаций: {len(optimizations)}")
            
        except Exception as e:
            self.logger.error(f"Ошибка применения оптимизаций: {e}")
            self.textLog.append(f"⚠️ Ошибка оптимизации: {e}")
    
    def show_system_info(self):
        """Показывает информацию о системе"""
        try:
            # Используем новый модуль оптимизации
            info = get_system_performance_info()
            
            if info:
                cpu_cores = info.get('cpu_cores', 0)
                memory_gb = info.get('memory_total_gb', 0)
                cpu_usage = info.get('cpu_usage', 0)
                memory_usage = info.get('memory_usage_percent', 0)
                
                self.textLog.append(f"💻 Система: {cpu_cores} ядер, {memory_gb:.1f} ГБ RAM")
                self.textLog.append(f"⚡ CPU: {cpu_usage:.1f}%, RAM: {memory_usage:.1f}%")
                self.textLog.append("🚀 Режим высокой производительности активен")
                
                # Показываем рекомендации
                from core.performance_optimizer import performance_optimizer
                recommendations = performance_optimizer.get_performance_recommendations()
                if recommendations:
                    self.textLog.append("💡 Рекомендации:")
                    for rec in recommendations:
                        self.textLog.append(f"   • {rec}")
            else:
                self.textLog.append("⚠️ Не удалось получить информацию о системе")
            
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о системе: {e}")
            self.textLog.append(f"⚠️ Ошибка получения информации о системе: {e}")
    
    def run_planner_optimized(self):
        """Оптимизированный запуск планировщика"""
        self.logger.info("Запуск оптимизированного планировщика")
        
        assignment_method = self.get_assignment_method()
        self.textLog.append(f"🚀 Запуск планировщика (оптимизированный режим): {assignment_method}")
        
        if not self.input_data:
            self.textLog.append("❌ Нет входных данных. Сначала загрузите файл.")
            return
        
        try:
            self.show_busy("Планирование в оптимизированном режиме...")
            
            # Получаем информацию о сцене для оптимизации
            n_robots = len(self.input_data.robots) if hasattr(self.input_data, 'robots') else 0
            n_operations = len(self.input_data.operations) if hasattr(self.input_data, 'operations') else 0
            
            # Применяем оптимизации для размера сцены
            scene_optimizations = optimize_for_scene(n_robots, n_operations)
            self.textLog.append(f"🎯 Оптимизация для сцены: {n_robots} роботов, {n_operations} операций")
            
            # Создаем оптимизированный воркер
            genetic_params = self.get_genetic_parameters() if assignment_method == "genetic" else None
            if genetic_params and scene_optimizations:
                # Применяем оптимизированные параметры генетического алгоритма
                genetic_params.update({
                    'population_size': scene_optimizations.get('genetic_population', genetic_params['population_size']),
                    'generations': scene_optimizations.get('genetic_generations', genetic_params['generations'])
                })
            
            self._worker_thread = QtCore.QThread(self)
            self._worker = OptimizedWorker(self.input_data, assignment_method, genetic_params)
            self._worker.moveToThread(self._worker_thread)
            
            # Подключаем сигналы
            self._worker_thread.started.connect(self._worker.run)
            self._worker.finished.connect(self.on_planning_finished)
            self._worker.error.connect(self.on_planning_error)
            self._worker.progress.connect(self.on_planning_progress)
            self._worker.memory_warning.connect(self.on_memory_warning)
            
            # Очистка при завершении
            self._worker_thread.finished.connect(self._worker.deleteLater)
            self._worker_thread.finished.connect(self._worker_thread.deleteLater)
            
            # Запускаем воркер
            self._worker_thread.start()
            
        except Exception as e:
            error_msg = f"❌ Ошибка запуска планировщика: {e}"
            self.textLog.append(error_msg)
            self.logger.error(error_msg, exc_info=True)
            self.hide_busy()
    
    @QtCore.Slot(dict)
    def on_planning_finished(self, plan):
        """Обработка завершения планирования"""
        try:
            self.plan = plan
            self.textLog.append("✅ Планировщик завершил работу (оптимизированный режим)")
            
            makespan = self.plan.get("makespan", 0.0)
            self.textLog.append(f"📊 Makespan: {makespan:.2f} сек")
            
            # Показываем статистику производительности
            self.performance_monitor.update()
            info = self.performance_monitor.get_system_info()
            self.textLog.append(f"💻 Использование ресурсов: CPU {info['cpu_usage']:.1f}%, RAM {info['memory_usage']:.1f}%")
            
            self.logger.info("Планирование успешно завершено")
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки результата планирования: {e}")
        finally:
            self.hide_busy()
    
    @QtCore.Slot(str)
    def on_planning_error(self, error_msg):
        """Обработка ошибки планирования"""
        self.textLog.append(f"❌ Ошибка планирования: {error_msg}")
        self.logger.error(f"Ошибка планирования: {error_msg}")
        self.hide_busy()
    
    @QtCore.Slot(int)
    def on_planning_progress(self, value):
        """Обработка прогресса планирования"""
        try:
            if hasattr(self, 'progressBar_status'):
                self.progressBar_status.setRange(0, 100)
                self.progressBar_status.setValue(value)
                self.progressBar_status.repaint()
            QtWidgets.QApplication.processEvents()
        except Exception:
            pass
    
    @QtCore.Slot(str)
    def on_memory_warning(self, warning_msg):
        """Обработка предупреждения о памяти"""
        self.textLog.append(f"⚠️ {warning_msg}")
        self.logger.warning(warning_msg)
    
    def open_visualizer_optimized(self):
        """Оптимизированное открытие визуализатора"""
        self.logger.info("Открытие оптимизированного визуализатора")
        
        if not self.plan:
            self.textLog.append("Нет плана для визуализации. Сначала запустите планировщик.")
            return
        
        try:
            self.show_busy("Генерация оптимизированной визуализации...")
            
            # Агрессивные оптимизации для больших сцен
            robots = self.plan.get("robots", [])
            n_robots = len(robots)
            
            # Автоматические настройки производительности
            if n_robots >= 4:
                self.plan["max_anim_frames"] = 60
                self.plan["anim_time_stride"] = 0.2
                self.plan["arm_segments"] = 2
                self.plan["robot_mesh"] = None  # Отключаем 3D модели
                self.plan["arm_mesh"] = True    # Используем простые сегменты
                self.textLog.append("🚀 Применены агрессивные оптимизации для большой сцены")
            
            if n_robots >= 8:
                self.plan["max_anim_frames"] = 40
                self.plan["anim_time_stride"] = 0.3
                self.plan["arm_segments"] = 1
                self.textLog.append("⚡ Применены максимальные оптимизации для очень большой сцены")
            
            # Запускаем визуализацию в фоне
            class OptimizedVizWorker(QtCore.QObject):
                finished = QtCore.Signal()
                error = QtCore.Signal(str)
                progress = QtCore.Signal(int)
                
                def __init__(self, plan, mode):
                    super().__init__()
                    self._plan = plan
                    self._mode = mode
                
                @QtCore.Slot()
                def run(self):
                    try:
                        def _cb(p):
                            try:
                                self.progress.emit(int(p))
                            except Exception:
                                pass
                        show_visualization(self._plan, self._mode, progress_callback=_cb)
                        self.finished.emit()
                    except Exception as e:
                        self.error.emit(str(e))
            
            # Создаем поток для визуализации
            viz_thread = QtCore.QThread(self)
            viz_worker = OptimizedVizWorker(dict(self.plan), "3d_anim")
            viz_worker.moveToThread(viz_thread)
            viz_thread.started.connect(viz_worker.run)
            
            def _on_viz_done():
                self.textLog.append("✅ Оптимизированная визуализация завершена")
                self.logger.info("Визуализация успешно завершена")
                self.hide_busy()
                viz_thread.quit()
            
            def _on_viz_err(msg: str):
                self.textLog.append(f"❌ Ошибка визуализации: {msg}")
                self.logger.error(f"Ошибка визуализации: {msg}")
                self.hide_busy()
                viz_thread.quit()
            
            viz_worker.finished.connect(_on_viz_done)
            viz_worker.progress.connect(self._on_viz_progress)
            viz_worker.error.connect(_on_viz_err)
            viz_thread.finished.connect(viz_worker.deleteLater)
            viz_thread.finished.connect(viz_thread.deleteLater)
            
            viz_thread.start()
            
        except Exception as e:
            error_msg = f"❌ Ошибка визуализации: {e}"
            self.textLog.append(error_msg)
            self.logger.error(error_msg, exc_info=True)
            self.hide_busy()
    
    @QtCore.Slot(int)
    def _on_viz_progress(self, value: int):
        """Обработка прогресса визуализации"""
        try:
            if hasattr(self, 'progressBar_bottom'):
                self.progressBar_bottom.setRange(0, 100)
                self.progressBar_bottom.setValue(value)
                self.progressBar_bottom.repaint()
            if hasattr(self, 'labelProgress_bottom'):
                self.labelProgress_bottom.setText(f"Визуализация: {value}%")
            QtWidgets.QApplication.processEvents()
        except Exception:
            pass
    
    def show_busy(self, message: str = "Загрузка..."):
        """Показывает индикатор загрузки"""
        try:
            self.statusbar.showMessage(message)
            if hasattr(self, 'progressBar_status'):
                self.progressBar_status.setRange(0, 0)
                self.progressBar_status.setVisible(True)
                self.progressBar_status.repaint()
            QtWidgets.QApplication.processEvents()
        except Exception:
            pass
    
    def hide_busy(self):
        """Скрывает индикатор загрузки"""
        try:
            self.statusbar.clearMessage()
            if hasattr(self, 'progressBar_status'):
                self.progressBar_status.setVisible(False)
                self.progressBar_status.setRange(0, 100)
        except Exception:
            pass
    
    # Остальные методы наследуются от базового класса
    def load_file(self):
        """Загрузка входного файла"""
        self.logger.info("Загрузка файла в десктопном приложении")
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Выберите входной файл", "data/",
            "JSON Files (*.json);;Text Files (*.txt);;All Files (*)"
        )
        
        if path:
            self.textLog.append(f"📂 Загружен файл: {path}")
            try:
                self.input_data = parse_input_file(path)
                self.textLog.append("✅ Файл успешно загружен")
                
                if hasattr(self.input_data, 'robots'):
                    self.textLog.append(f"🤖 Роботов: {len(self.input_data.robots)}")
                if hasattr(self.input_data, 'operations'):
                    self.textLog.append(f"⚙️ Операций: {len(self.input_data.operations)}")
                    
            except Exception as e:
                error_msg = f"❌ Ошибка загрузки: {e}"
                self.textLog.append(error_msg)
                self.logger.error(error_msg, exc_info=True)
    
    def save_result(self):
        """Сохранение результата"""
        if not self.plan:
            self.textLog.append("Нет плана для сохранения")
            return
        
        results_dir = os.path.join(os.path.dirname(__file__), "..", "outputs", "results")
        os.makedirs(results_dir, exist_ok=True)
        
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Сохранить результат", results_dir, 
            "Text Files (*.txt);;JSON Files (*.json)"
        )
        
        if path:
            try:
                if path.endswith('.json'):
                    import json
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump(self.plan, f, indent=2, ensure_ascii=False)
                else:
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
                
                self.textLog.append(f"💾 Результат сохранен: {path}")
                self.logger.info(f"Результат сохранен: {path}")
                
            except Exception as e:
                error_msg = f"❌ Ошибка сохранения: {e}"
                self.textLog.append(error_msg)
                self.logger.error(error_msg, exc_info=True)
    
    def clear_logs(self):
        """Очистка логов"""
        self.textLog.clear()
        self.textLog.append("🗑️ Логи очищены")
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
    
    def update_genetic_controls(self):
        """Обновляет видимость элементов управления генетическим алгоритмом"""
        is_genetic = self.comboBox_assignment_method.currentText().startswith("Genetic")
        self.label_genetic_population.setVisible(is_genetic)
        self.spinBox_population_size.setVisible(is_genetic)
        self.label_genetic_generations.setVisible(is_genetic)
        self.spinBox_generations.setVisible(is_genetic)
    
    def sync_model_selector_visibility(self):
        """Синхронизация видимости селектора модели"""
        try:
            is_on = bool(self.get_arm_mesh_enabled()) if hasattr(self, 'get_arm_mesh_enabled') else False
            if hasattr(self, 'label_robot_model'):
                self.label_robot_model.setVisible(is_on)
            if hasattr(self, 'comboBox_robot_model'):
                self.comboBox_robot_model.setVisible(is_on)
        except Exception:
            pass
    
    def get_arm_mesh_enabled(self):
        """Возвращает состояние флага 3D меша"""
        return self.checkBox_arm_mesh.isChecked()
    
    def apply_theme(self, theme_name):
        """Применяет тему"""
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

            app = QtWidgets.QApplication.instance()
            if app is not None:
                app.setStyleSheet(style)
            else:
                self.setStyleSheet(style)
            
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
        """Переключает тему"""
        new_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme(new_theme)
        self.textLog.append(f"🎨 Переключено на {new_theme.title()} тему")
    
    def setup_theme_toggle(self):
        """Настраивает переключатель темы"""
        self.pushButton_theme_toggle = QtWidgets.QPushButton("🌙")
        self.pushButton_theme_toggle.setProperty("class", "theme-toggle")
        self.pushButton_theme_toggle.clicked.connect(self.toggle_theme)
        self.pushButton_theme_toggle.setToolTip("Переключить тему")
        
        self.theme_container = QtWidgets.QWidget()
        self.theme_layout = QtWidgets.QHBoxLayout(self.theme_container)
        self.theme_layout.setContentsMargins(0, 0, 0, 0)
        self.theme_layout.addStretch()
        self.theme_layout.addWidget(self.pushButton_theme_toggle)
        
        self.verticalLayout_main.addWidget(self.theme_container)
    
    def open_input_generator(self):
        """Открывает генератор входных данных"""
        try:
            dlg = InputGeneratorDialog(self)
            if hasattr(self, 'current_theme'):
                if self.current_theme == 'dark':
                    from ui_files.styles_final import get_dark_style
                    dlg.setStyleSheet(get_dark_style())
                else:
                    from ui_files.styles_final import get_light_style
                    dlg.setStyleSheet(get_light_style())
            
            if dlg.exec() == QtWidgets.QDialog.Accepted and getattr(dlg, 'saved_path', None):
                path = dlg.saved_path
                self.textLog.append(f"📥 Входной файл создан: {path}")
                if getattr(dlg, 'load_into_app', False):
                    try:
                        self.input_data = parse_input_file(path)
                        self.textLog.append("✅ Входные данные загружены")
                    except Exception as e:
                        self.textLog.append(f"❌ Ошибка загрузки: {e}")
        except Exception as e:
            self.textLog.append(f"❌ Ошибка генератора: {e}")
    
    def save_result_as(self):
        """Сохраняет результат с выбором имени"""
        try:
            if self.plan is None:
                QtWidgets.QMessageBox.warning(self, "Предупреждение", "Нет данных для сохранения")
                return
            
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Сохранить результат планирования", "", 
                "JSON файлы (*.json);;Все файлы (*)"
            )
            
            if file_path:
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.plan, f, indent=2, ensure_ascii=False)
                
                self.textLog.append(f"💾 Результат сохранен: {file_path}")
                self.logger.info(f"Результат сохранен: {file_path}")
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")
            self.logger.error(f"Ошибка сохранения файла: {e}")
    
    def show_about(self):
        """Показывает информацию о программе"""
        try:
            about_text = """
            <div style="font-family: Arial, sans-serif; line-height: 1.6;">
                <h2 style="color: #FF6B35; margin-bottom: 20px;">🖥️ ROBOTY Desktop v1.0.0</h2>
                <h3 style="color: #4682B4; margin-bottom: 15px;">Оптимизированное десктопное приложение</h3>
                
                <p style="font-size: 14px; color: #666; margin-bottom: 20px;">
                    <strong>Высокопроизводительная версия</strong> для работы с большими нагрузками 
                    и сложными многороботными системами.
                </p>
                
                <div style="background: #fff3e0; padding: 15px; border-radius: 8px; margin: 15px 0;">
                    <h4 style="color: #FF6B35; margin-top: 0;">🚀 Оптимизации производительности:</h4>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li><strong>Мониторинг ресурсов:</strong> CPU, RAM, процессы</li>
                        <li><strong>Агрессивная сборка мусора:</strong> Оптимизация памяти</li>
                        <li><strong>Многопоточность:</strong> Фоновые вычисления</li>
                        <li><strong>Автоматические настройки:</strong> Под размер сцены</li>
                        <li><strong>Приоритет процесса:</strong> Повышенная производительность</li>
                    </ul>
                </div>
                
                <div style="background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 15px 0;">
                    <h4 style="color: #4682B4; margin-top: 0;">⚙️ Технические особенности:</h4>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li><strong>NumPy оптимизации:</strong> Максимальная скорость вычислений</li>
                        <li><strong>Умная визуализация:</strong> Адаптивные настройки качества</li>
                        <li><strong>Предупреждения памяти:</strong> Контроль ресурсов</li>
                        <li><strong>Прогресс-бары:</strong> Детальная обратная связь</li>
                    </ul>
                </div>
                
                <div style="border-top: 2px solid #FF6B35; padding-top: 15px; margin-top: 20px;">
                    <p style="margin: 5px 0;"><strong>👥 Разработчик:</strong> ROBOTY Team</p>
                    <p style="margin: 5px 0;"><strong>🖥️ Версия:</strong> Desktop Optimized</p>
                    <p style="margin: 5px 0;"><strong>📄 Лицензия:</strong> MIT License</p>
                </div>
            </div>
            """
            
            QtWidgets.QMessageBox.about(self, "О программе ROBOTY Desktop", about_text)
            self.logger.info("Открыто окно 'О программе'")
            
        except Exception as e:
            self.logger.error(f"Ошибка при показе диалога 'О программе': {e}")
    
    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        try:
            self.logger.info("Закрытие десктопного приложения")
            
            # Очищаем ресурсы
            cleanup_performance_resources()
            
            # Останавливаем фоновые потоки
            if hasattr(self, '_worker_thread') and self._worker_thread and self._worker_thread.isRunning():
                self._worker_thread.quit()
                self._worker_thread.wait()
            
            self.logger.info("Десктопное приложение закрыто")
            
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии приложения: {e}")
        
        event.accept()


def main():
    """Главная функция для запуска десктопного приложения"""
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("ROBOTY Desktop")
        app.setApplicationVersion("1.0")
        
        window = DesktopApp()
        window.show()
        
        logger = logging.getLogger("ROBOTY_DESKTOP.main")
        logger.info("Десктопное приложение успешно запущено")
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Критическая ошибка при запуске десктопного приложения: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
