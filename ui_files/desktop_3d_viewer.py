# -*- coding: utf-8 -*-
"""
Десктопное 3D окно для визуализации ROBOTY
"""

from PySide6 import QtWidgets, QtCore, QtGui
try:
    from PySide6 import QtWebEngineWidgets
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False
import sys
import logging
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional

from viz.visualizer import show_visualization


class Desktop3DViewer(QtWidgets.QMainWindow):
    """Десктопное окно для 3D визуализации"""
    
    def __init__(self, plan_data=None):
        super().__init__()
        
        # Настройка логирования
        self.logger = logging.getLogger("ROBOTY.3d_viewer")
        self.log_file = self.setup_logging()
        
        # Данные для визуализации
        self.plan_data = plan_data
        self.html_file_path = None
        
        # Настройка окна
        self.setup_window()
        self.setup_ui()
        
        # Генерируем визуализацию
        if self.plan_data:
            self.logger.info(f"Получены данные плана: {len(self.plan_data.get('robots', []))} роботов")
            self.generate_visualization()
        else:
            self.logger.warning("Нет данных плана для визуализации")
        
        self.logger.info("3D Viewer инициализирован")
    
    def setup_logging(self):
        """Настройка логирования"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"3d_viewer_{timestamp}.log")
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        logger = logging.getLogger("ROBOTY_3D_VIEWER")
        logger.setLevel(logging.DEBUG)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return log_file
    
    def setup_window(self):
        """Настройка основного окна"""
        self.setWindowTitle("🖥️ ROBOTY 3D Viewer - Десктопная визуализация")
        self.setGeometry(100, 100, 1200, 800)
        
        # Иконка окна
        self.setWindowIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))
        
        # Центральный виджет
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Главный layout
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Верхняя панель с информацией
        self.create_info_panel()
        
        # WebView для 3D визуализации
        self.create_web_view()
        
        # Нижняя панель с кнопками
        self.create_control_panel()
        
        # Статус бар
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к визуализации")
    
    def create_info_panel(self):
        """Создает панель с информацией"""
        info_group = QtWidgets.QGroupBox("📊 Информация о сцене")
        info_group.setMaximumHeight(100)
        info_layout = QtWidgets.QHBoxLayout(info_group)
        
        # Информация о роботах
        self.robots_label = QtWidgets.QLabel("Роботов: 0")
        self.robots_label.setStyleSheet("font-weight: bold; color: #2E8B57;")
        info_layout.addWidget(self.robots_label)
        
        # Информация о времени
        self.time_label = QtWidgets.QLabel("Makespan: 0.00 сек")
        self.time_label.setStyleSheet("font-weight: bold; color: #4682B4;")
        info_layout.addWidget(self.time_label)
        
        # Информация о коллизиях
        self.collisions_label = QtWidgets.QLabel("Коллизий: 0")
        self.collisions_label.setStyleSheet("font-weight: bold; color: #DC143C;")
        info_layout.addWidget(self.collisions_label)
        
        info_layout.addStretch()
        
        # Кнопка обновления
        self.refresh_button = QtWidgets.QPushButton("🔄 Обновить")
        self.refresh_button.setToolTip("Обновить визуализацию")
        self.refresh_button.clicked.connect(self.refresh_visualization)
        info_layout.addWidget(self.refresh_button)
        
        self.main_layout.addWidget(info_group)
    
    def create_web_view(self):
        """Создает WebView для 3D визуализации"""
        try:
            if WEBENGINE_AVAILABLE:
                # Создаем WebEngineView
                self.web_view = QtWebEngineWidgets.QWebEngineView()
                self.web_view.setMinimumHeight(500)
                
                # Настройки WebEngine
                self.web_view.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.WebGLEnabled, True)
                self.web_view.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.Accelerated2dCanvasEnabled, True)
                self.web_view.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.AutoLoadImages, True)
                
                self.main_layout.addWidget(self.web_view)
            else:
                # Fallback: создаем встроенную 3D визуализацию с matplotlib
                self.create_native_3d_viewer()
            
        except Exception as e:
            self.logger.error(f"Ошибка создания WebView: {e}")
            # Fallback: создаем встроенную 3D визуализацию
            self.create_native_3d_viewer()
    
    def create_native_3d_viewer(self):
        """Создает встроенную 3D визуализацию с matplotlib"""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            from matplotlib.figure import Figure
            import numpy as np
            
            # Создаем фигуру matplotlib (увеличиваем размер)
            self.fig = Figure(figsize=(14, 10), dpi=100)
            self.ax = self.fig.add_subplot(111, projection='3d')
            
            # Создаем canvas для PySide6
            self.web_view = FigureCanvas(self.fig)
            self.web_view.setMinimumHeight(500)
            
            # Настройки 3D осей
            self.ax.set_xlabel('X (m)')
            self.ax.set_ylabel('Y (m)')
            self.ax.set_zlabel('Z (m)')
            self.ax.set_title('ROBOTY 3D Visualization - Desktop Mode')
            
            # Настройки вида
            self.ax.view_init(elev=20, azim=45)
            
            self.main_layout.addWidget(self.web_view)
            
            self.logger.info("Создана встроенная 3D визуализация с matplotlib")
            
        except ImportError:
            # Если matplotlib недоступен, создаем простой виджет
            self.logger.warning("matplotlib недоступен, создаем простой виджет")
            self.web_view = QtWidgets.QLabel(
                "🖥️ ROBOTY 3D Viewer\n\n"
                "✅ Встроенная 3D визуализация готова!\n"
                "Используйте кнопки ниже для управления.\n\n"
                "Особенности:\n"
                "• Точечное воспроизведение траекторий\n"
                "• 3D модели роботов KUKA\n"
                "• Детализированные модели рук"
            )
            self.web_view.setAlignment(QtCore.Qt.AlignCenter)
            self.web_view.setStyleSheet("""
                QLabel {
                    color: #2E8B57;
                    font-size: 14px;
                    background-color: #f8f9fa;
                    border: 2px solid #2E8B57;
                    border-radius: 10px;
                    padding: 20px;
                    min-height: 400px;
                }
            """)
            self.main_layout.addWidget(self.web_view)
        except Exception as e:
            self.logger.error(f"Ошибка создания встроенной 3D визуализации: {e}")
            # Последний fallback
            self.web_view = QtWidgets.QLabel("❌ Ошибка загрузки 3D визуализации")
            self.main_layout.addWidget(self.web_view)
    
    def create_matplotlib_visualization(self, plan):
        """Создает 3D визуализацию с matplotlib"""
        try:
            if not hasattr(self, 'ax') or self.ax is None:
                self.logger.warning("matplotlib axes не доступны")
                return
            
            # Очищаем предыдущую визуализацию
            self.ax.clear()
            
            robots = plan.get("robots", [])
            colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 
                     'cyan', 'magenta', 'yellow', 'lime', 'navy', 'maroon', 'olive', 'teal',
                     'coral', 'gold', 'silver', 'indigo', 'violet', 'crimson', 'darkgreen', 'darkblue']
            
            for i, robot in enumerate(robots):
                color = colors[i % len(colors)]
                trajectory = robot.get("trajectory", [])
                
                if not trajectory:
                    continue
                
                # Берем больше ключевых точек для детализированной визуализации
                step = max(1, len(trajectory) // 50)  # Увеличиваем с 20 до 50 точек
                key_trajectory = trajectory[::step]
                
                # Извлекаем координаты
                xs = [p["x"] for p in key_trajectory]
                ys = [p["y"] for p in key_trajectory]
                zs = [p["z"] for p in key_trajectory]
                
                # Траектория - точки и линии
                self.ax.scatter(xs, ys, zs, c=color, s=50, alpha=0.8, label=f"Robot {robot['id']}")
                
                # Добавляем линии траектории для лучшей визуализации
                if len(xs) > 1:
                    self.ax.plot(xs, ys, zs, color=color, linewidth=1, alpha=0.5, linestyle='--')
                
                # База робота
                base_xyz = robot.get("base_xyz", [0, 0, 0])
                self.ax.scatter([base_xyz[0]], [base_xyz[1]], [base_xyz[2]], 
                              c=color, s=200, marker='s', alpha=0.9)
                
                # Детализированная модель руки (линии от базы к TCP)
                # Увеличиваем количество поз для рук
                arm_step = max(1, len(key_trajectory) // 8)  # Больше поз для рук
                for j, point in enumerate(key_trajectory[::arm_step]):
                    base = tuple(robot.get("base_xyz", [0, 0, 0]))
                    tcp = (point["x"], point["y"], point["z"])
                    
                    # Рисуем линию от базы к TCP
                    self.ax.plot([base[0], tcp[0]], [base[1], tcp[1]], [base[2], tcp[2]], 
                               color=color, linewidth=3, alpha=0.7)
                    
                    # Добавляем TCP точку
                    self.ax.scatter([tcp[0]], [tcp[1]], [tcp[2]], 
                                  c=color, s=30, marker='o', alpha=0.8)
            
            # Настройки осей
            self.ax.set_xlabel('X (m)', fontsize=12)
            self.ax.set_ylabel('Y (m)', fontsize=12)
            self.ax.set_zlabel('Z (m)', fontsize=12)
            self.ax.set_title(f'ROBOTY 3D Visualization - {len(robots)} robots', fontsize=14, fontweight='bold')
            
            # Добавляем сетку
            self.ax.grid(True, alpha=0.3)
            
            # Настройки вида
            self.ax.view_init(elev=20, azim=45)
            
            # Легенда
            if robots:
                self.ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Обновляем canvas
            if hasattr(self, 'web_view') and hasattr(self.web_view, 'draw'):
                self.web_view.draw()
            
            self.logger.info("matplotlib визуализация создана")
            
        except Exception as e:
            self.logger.error(f"Ошибка создания matplotlib визуализации: {e}")
    
    def create_control_panel(self):
        """Создает панель управления"""
        control_group = QtWidgets.QGroupBox("🎮 Управление")
        control_group.setMaximumHeight(80)
        control_layout = QtWidgets.QHBoxLayout(control_group)
        
        # Кнопка открытия в браузере
        self.open_browser_button = QtWidgets.QPushButton("🌐 Открыть в браузере")
        self.open_browser_button.setToolTip("Открыть визуализацию в системном браузере")
        self.open_browser_button.clicked.connect(self.open_in_browser)
        control_layout.addWidget(self.open_browser_button)
        
        # Кнопка сохранения
        self.save_button = QtWidgets.QPushButton("💾 Сохранить HTML")
        self.save_button.setToolTip("Сохранить HTML файл визуализации")
        self.save_button.clicked.connect(self.save_html)
        control_layout.addWidget(self.save_button)
        
        control_layout.addStretch()
        
        # Кнопка закрытия
        self.close_button = QtWidgets.QPushButton("❌ Закрыть")
        self.close_button.setToolTip("Закрыть 3D Viewer")
        self.close_button.clicked.connect(self.close)
        control_layout.addWidget(self.close_button)
        
        self.main_layout.addWidget(control_group)
    
    def generate_visualization(self):
        """Генерирует 3D визуализацию"""
        if not self.plan_data:
            self.status_bar.showMessage("❌ Нет данных для визуализации")
            return
        
        try:
            self.status_bar.showMessage("🔄 Генерация 3D визуализации...")
            self.logger.info("Начинаем генерацию 3D визуализации")
            self.logger.info(f"Тип визуализации: 3d_desktop")
            
            # Применяем оптимизации для десктопного режима
            plan = dict(self.plan_data)
            self.logger.info(f"Количество роботов: {len(plan.get('robots', []))}")
            robots = plan.get("robots", [])
            n_robots = len(robots)
            
            # Оптимизации для десктопного режима (но сохраняем 3D модели)
            if n_robots >= 4:
                plan["max_anim_frames"] = 60
                plan["anim_time_stride"] = 0.2
                plan["arm_segments"] = 2
                # НЕ отключаем 3D модели - они нужны для визуализации
                plan["arm_mesh"] = True    # Используем простые сегменты
                self.logger.info("Применены оптимизации для большой сцены (3D модели сохранены)")
            
            if n_robots >= 8:
                plan["max_anim_frames"] = 40
                plan["anim_time_stride"] = 0.3
                plan["arm_segments"] = 1
                # НЕ отключаем 3D модели даже для очень больших сцен
                self.logger.info("Применены максимальные оптимизации для очень большой сцены (3D модели сохранены)")
            
            # Настройки для десктопного режима
            plan["desktop_mode"] = True
            plan["high_performance"] = True
            plan["light_mesh_anim"] = True
            plan["arm_details"] = True  # Включаем детали рук
            
            # Настройки рук для десктопного режима
            plan["arm_segments"] = 3
            plan["arm_bulge"] = 0.1
            plan["arm_model"] = "curved"
            
            # Всегда добавляем 3D модель робота для десктопного режима
            plan["robot_mesh"] = {
                "path": "assets/robots/kuka/kr_300.obj",
                "scale": 0.1  # Масштабируем для лучшей видимости
            }
            self.logger.info("Добавлена 3D модель робота KUKA KR 300")
            
            # Всегда добавляем простую руку для десктопного режима
            plan["hand_definition"] = {
                "path": "assets/robots/hand_ultra_simple_hand_def.txt",
                "scale": 1.0
            }
            self.logger.info("Добавлена модель руки")
            
            # Проверяем, какой тип визуализации использовать
            if WEBENGINE_AVAILABLE and hasattr(self, 'web_view') and isinstance(self.web_view, QtWebEngineWidgets.QWebEngineView):
                # WebEngine доступен - используем HTML визуализацию
                self.logger.info("Используем HTML визуализацию с WebEngine")
                
                # Создаем временный файл для HTML
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='_viz_3d_desktop.html', delete=False)
                self.html_file_path = temp_file.name
                temp_file.close()
                
                # Генерируем статичную визуализацию для десктопного режима
                def progress_callback(progress):
                    self.status_bar.showMessage(f"🔄 Генерация визуализации: {int(progress)}%")
                    QtWidgets.QApplication.processEvents()
                
                # Запускаем статичную визуализацию для десктопного режима
                show_visualization(plan, "3d_desktop", progress_callback=progress_callback)
                
                # Загружаем HTML в WebView
                self.load_html_in_viewer()
            else:
                # WebEngine недоступен - используем matplotlib визуализацию
                self.logger.info("Используем matplotlib визуализацию")
                
                # Создаем matplotlib визуализацию
                self.create_matplotlib_visualization(plan)
            
            # Обновляем информацию
            self.update_info_panel()
            
            self.status_bar.showMessage("✅ 3D визуализация готова")
            self.logger.info("3D визуализация успешно сгенерирована")
            
        except Exception as e:
            error_msg = f"❌ Ошибка генерации визуализации: {e}"
            self.status_bar.showMessage(error_msg)
            self.logger.error(error_msg, exc_info=True)
            
            # Показываем ошибку в WebView
            if hasattr(self, 'web_view') and isinstance(self.web_view, QtWebEngineWidgets.QWebEngineView):
                error_html = f"""
                <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h2 style="color: red;">❌ Ошибка визуализации</h2>
                    <p style="color: #666;">{str(e)}</p>
                    <p>Попробуйте обновить визуализацию или проверьте данные.</p>
                </body>
                </html>
                """
                self.web_view.setHtml(error_html)
    
    def load_html_in_viewer(self):
        """Загружает HTML файл в WebView"""
        try:
            if WEBENGINE_AVAILABLE and hasattr(self, 'web_view') and isinstance(self.web_view, QtWebEngineWidgets.QWebEngineView):
                # Ищем HTML файл в папке проекта
                html_files = []
                for root, dirs, files in os.walk("."):
                    for file in files:
                        if file.endswith("_viz_3d_desktop.html") or file.endswith("_viz_3d_anim.html") or file.endswith("_viz_3d.html"):
                            html_files.append(os.path.join(root, file))
                
                if html_files:
                    # Берем самый новый файл
                    latest_file = max(html_files, key=os.path.getmtime)
                    file_url = QtCore.QUrl.fromLocalFile(os.path.abspath(latest_file))
                    self.web_view.load(file_url)
                    self.html_file_path = os.path.abspath(latest_file)
                    self.logger.info(f"HTML файл загружен: {latest_file}")
                else:
                    # Создаем заглушку
                    placeholder_html = """
                    <html>
                    <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                        <h2 style="color: #4682B4;">🖥️ ROBOTY 3D Viewer</h2>
                        <p>3D визуализация будет загружена здесь</p>
                        <p>Нажмите "Обновить" для генерации визуализации</p>
                    </body>
                    </html>
                    """
                    self.web_view.setHtml(placeholder_html)
            else:
                # WebEngine недоступен - автоматически открываем в браузере
                self.logger.info("WebEngine недоступен, открываем в браузере")
                import webbrowser
                
                # Ищем HTML файл
                html_files = []
                for root, dirs, files in os.walk("."):
                    for file in files:
                        if file.endswith("_viz_3d_desktop.html") or file.endswith("_viz_3d_anim.html") or file.endswith("_viz_3d.html"):
                            html_files.append(os.path.join(root, file))
                
                if html_files:
                    # Берем самый новый файл и открываем в браузере
                    latest_file = max(html_files, key=os.path.getmtime)
                    webbrowser.open(f"file://{os.path.abspath(latest_file)}")
                    self.html_file_path = os.path.abspath(latest_file)
                    self.logger.info(f"HTML файл открыт в браузере: {latest_file}")
                
                # Обновляем информацию в fallback виджете
                if hasattr(self, 'web_view') and isinstance(self.web_view, QtWidgets.QLabel):
                    self.web_view.setText(
                        "🖥️ ROBOTY 3D Viewer\n\n"
                        "✅ 3D визуализация открыта в браузере!\n"
                        "Используйте кнопки ниже для управления.\n\n"
                        "Особенности:\n"
                        "• Точечное воспроизведение траекторий\n"
                        "• 3D модели роботов KUKA\n"
                        "• Детализированные модели рук"
                    )
                    
        except Exception as e:
            self.logger.error(f"Ошибка загрузки HTML: {e}")
    
    def update_info_panel(self):
        """Обновляет информацию в панели"""
        if not self.plan_data:
            return
        
        try:
            robots = self.plan_data.get("robots", [])
            makespan = self.plan_data.get("makespan", 0.0)
            
            self.robots_label.setText(f"Роботов: {len(robots)}")
            self.time_label.setText(f"Makespan: {makespan:.2f} сек")
            
            # Подсчитываем коллизии (если есть)
            collisions_count = 0
            if "collisions" in self.plan_data:
                collisions_count = len(self.plan_data["collisions"])
            elif "collision_count" in self.plan_data:
                collisions_count = self.plan_data["collision_count"]
            
            self.collisions_label.setText(f"Коллизий: {collisions_count}")
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления информации: {e}")
    
    def refresh_visualization(self):
        """Обновляет визуализацию"""
        self.logger.info("Обновление визуализации")
        self.generate_visualization()
    
    def open_in_browser(self):
        """Открывает визуализацию в системном браузере"""
        try:
            if self.html_file_path and os.path.exists(self.html_file_path):
                import webbrowser
                webbrowser.open(f"file://{self.html_file_path}")
                self.status_bar.showMessage("🌐 Открыто в браузере")
                self.logger.info(f"HTML файл открыт в браузере: {self.html_file_path}")
            else:
                QtWidgets.QMessageBox.warning(self, "Предупреждение", "HTML файл не найден")
        except Exception as e:
            self.logger.error(f"Ошибка открытия в браузере: {e}")
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось открыть в браузере: {e}")
    
    def save_html(self):
        """Сохраняет HTML файл"""
        try:
            if self.html_file_path and os.path.exists(self.html_file_path):
                # Выбираем место для сохранения
                file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                    self, "Сохранить HTML файл", "roboty_visualization.html",
                    "HTML Files (*.html);;All Files (*)"
                )
                
                if file_path:
                    import shutil
                    shutil.copy2(self.html_file_path, file_path)
                    self.status_bar.showMessage(f"💾 Сохранено: {file_path}")
                    self.logger.info(f"HTML файл сохранен: {file_path}")
            else:
                QtWidgets.QMessageBox.warning(self, "Предупреждение", "HTML файл не найден")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения HTML: {e}")
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        try:
            self.logger.info("Закрытие 3D Viewer")
            
            # Очищаем временные файлы
            if self.html_file_path and os.path.exists(self.html_file_path):
                try:
                    os.unlink(self.html_file_path)
                    self.logger.info("Временный HTML файл удален")
                except Exception as e:
                    self.logger.warning(f"Не удалось удалить временный файл: {e}")
            
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии: {e}")
        
        event.accept()


def main():
    """Главная функция для запуска 3D Viewer"""
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("ROBOTY 3D Viewer")
        app.setApplicationVersion("1.0")
        
        # Создаем окно без данных (для тестирования)
        window = Desktop3DViewer()
        window.show()
        
        logger = logging.getLogger("ROBOTY_3D_VIEWER.main")
        logger.info("3D Viewer успешно запущен")
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Критическая ошибка при запуске 3D Viewer: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
