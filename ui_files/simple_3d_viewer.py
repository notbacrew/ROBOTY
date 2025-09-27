# -*- coding: utf-8 -*-
"""
Упрощенный 3D Viewer для ROBOTY (без WebEngine)
"""

from PySide6 import QtWidgets, QtCore, QtGui
import sys
import logging
import os
import tempfile
import webbrowser
from datetime import datetime
from typing import Dict, Any, Optional

from viz.visualizer import show_visualization


class Simple3DViewer(QtWidgets.QMainWindow):
    """Упрощенный 3D Viewer без WebEngine"""
    
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
            self.generate_visualization()
        
        self.logger.info("Simple 3D Viewer инициализирован")
    
    def setup_logging(self):
        """Настройка логирования"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"simple_3d_viewer_{timestamp}.log")
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        logger = logging.getLogger("ROBOTY_SIMPLE_3D_VIEWER")
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
        self.setGeometry(100, 100, 1000, 700)
        
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
        
        # Область для отображения информации о визуализации
        self.create_visualization_area()
        
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
    
    def create_visualization_area(self):
        """Создает область для отображения информации о визуализации"""
        viz_group = QtWidgets.QGroupBox("🎮 3D Визуализация")
        viz_layout = QtWidgets.QVBoxLayout(viz_group)
        
        # Текстовая область с информацией
        self.info_text = QtWidgets.QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMinimumHeight(300)
        self.info_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)
        
        # Начальное сообщение
        initial_message = """
🖥️ ROBOTY 3D Viewer

Это десктопное окно для просмотра 3D визуализации роботов.

Функции:
• 📊 Отображение информации о сцене
• 🎮 Управление визуализацией
• 🌐 Открытие в браузере
• 💾 Сохранение HTML файлов

Для запуска визуализации нажмите "Обновить" или используйте кнопки управления.
        """
        self.info_text.setPlainText(initial_message)
        
        viz_layout.addWidget(self.info_text)
        self.main_layout.addWidget(viz_group)
    
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
            self.update_info_text("❌ Нет данных для визуализации")
            return
        
        try:
            self.status_bar.showMessage("🔄 Генерация 3D визуализации...")
            self.logger.info("Начинаем генерацию 3D визуализации")
            
            # Применяем оптимизации для десктопного режима
            plan = dict(self.plan_data)
            robots = plan.get("robots", [])
            n_robots = len(robots)
            
            # Агрессивные оптимизации для десктопного режима
            if n_robots >= 4:
                plan["max_anim_frames"] = 60
                plan["anim_time_stride"] = 0.2
                plan["arm_segments"] = 2
                plan["robot_mesh"] = None  # Отключаем 3D модели
                plan["arm_mesh"] = True    # Используем простые сегменты
                self.logger.info("Применены агрессивные оптимизации для большой сцены")
            
            if n_robots >= 8:
                plan["max_anim_frames"] = 40
                plan["anim_time_stride"] = 0.3
                plan["arm_segments"] = 1
                self.logger.info("Применены максимальные оптимизации для очень большой сцены")
            
            # Настройки для десктопного режима
            plan["desktop_mode"] = True
            plan["high_performance"] = True
            plan["light_mesh_anim"] = True
            
            # Обновляем информацию
            self.update_info_panel()
            
            # Генерируем визуализацию
            def progress_callback(progress):
                self.status_bar.showMessage(f"🔄 Генерация визуализации: {int(progress)}%")
                QtWidgets.QApplication.processEvents()
            
            # Запускаем визуализацию
            show_visualization(plan, "3d_anim", progress_callback=progress_callback)
            
            # Ищем созданный HTML файл
            self.find_html_file()
            
            self.status_bar.showMessage("✅ 3D визуализация готова")
            self.logger.info("3D визуализация успешно сгенерирована")
            
            # Обновляем информацию в текстовой области
            self.update_info_text("✅ 3D визуализация успешно сгенерирована!")
            
        except Exception as e:
            error_msg = f"❌ Ошибка генерации визуализации: {e}"
            self.status_bar.showMessage(error_msg)
            self.logger.error(error_msg, exc_info=True)
            self.update_info_text(error_msg)
    
    def find_html_file(self):
        """Ищет созданный HTML файл"""
        try:
            html_files = []
            for root, dirs, files in os.walk("."):
                for file in files:
                    if file.endswith("_viz_3d_anim.html"):
                        html_files.append(os.path.join(root, file))
            
            if html_files:
                # Берем самый новый файл
                latest_file = max(html_files, key=os.path.getmtime)
                self.html_file_path = os.path.abspath(latest_file)
                self.logger.info(f"HTML файл найден: {latest_file}")
                
                # Обновляем информацию
                info_text = f"""
✅ 3D визуализация успешно сгенерирована!

📁 HTML файл: {os.path.basename(self.html_file_path)}
📍 Путь: {self.html_file_path}

🎮 Доступные действия:
• Нажмите "🌐 Открыть в браузере" для просмотра
• Нажмите "💾 Сохранить HTML" для сохранения копии
• Нажмите "🔄 Обновить" для перегенерации

📊 Информация о сцене:
• Роботов: {len(self.plan_data.get('robots', []))}
• Makespan: {self.plan_data.get('makespan', 0.0):.2f} сек
• Оптимизации: Применены для десктопного режима
                """
                self.update_info_text(info_text)
            else:
                self.update_info_text("⚠️ HTML файл не найден. Попробуйте обновить визуализацию.")
                
        except Exception as e:
            self.logger.error(f"Ошибка поиска HTML файла: {e}")
            self.update_info_text(f"❌ Ошибка поиска HTML файла: {e}")
    
    def update_info_text(self, text):
        """Обновляет текст в информационной области"""
        self.info_text.setPlainText(text)
    
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
                webbrowser.open(f"file://{self.html_file_path}")
                self.status_bar.showMessage("🌐 Открыто в браузере")
                self.logger.info(f"HTML файл открыт в браузере: {self.html_file_path}")
                
                # Обновляем информацию
                info_text = f"""
🌐 Визуализация открыта в браузере!

📁 Файл: {os.path.basename(self.html_file_path)}
📍 Путь: {self.html_file_path}

✅ 3D анимация должна загрузиться в вашем браузере.
Если браузер не открылся автоматически, скопируйте путь выше
и вставьте его в адресную строку браузера.
                """
                self.update_info_text(info_text)
            else:
                QtWidgets.QMessageBox.warning(self, "Предупреждение", "HTML файл не найден")
                self.update_info_text("⚠️ HTML файл не найден. Сначала сгенерируйте визуализацию.")
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
                    
                    # Обновляем информацию
                    info_text = f"""
💾 HTML файл сохранен!

📁 Сохранен как: {os.path.basename(file_path)}
📍 Путь: {file_path}

✅ Файл можно открыть в любом браузере для просмотра 3D визуализации.
                    """
                    self.update_info_text(info_text)
            else:
                QtWidgets.QMessageBox.warning(self, "Предупреждение", "HTML файл не найден")
                self.update_info_text("⚠️ HTML файл не найден. Сначала сгенерируйте визуализацию.")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения HTML: {e}")
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        try:
            self.logger.info("Закрытие Simple 3D Viewer")
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии: {e}")
        
        event.accept()


def main():
    """Главная функция для запуска Simple 3D Viewer"""
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("ROBOTY Simple 3D Viewer")
        app.setApplicationVersion("1.0")
        
        # Создаем окно без данных (для тестирования)
        window = Simple3DViewer()
        window.show()
        
        logger = logging.getLogger("ROBOTY_SIMPLE_3D_VIEWER.main")
        logger.info("Simple 3D Viewer успешно запущен")
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Критическая ошибка при запуске Simple 3D Viewer: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
