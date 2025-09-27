# -*- coding: utf-8 -*-
"""
Нативный 3D Viewer для ROBOTY с использованием OpenGL
"""

from PySide6 import QtWidgets, QtCore, QtGui, QtOpenGLWidgets
import sys
import logging
import os
import math
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    from OpenGL.arrays import vbo
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False

try:
    import moderngl
    import moderngl_window
    MODERNGL_AVAILABLE = True
except ImportError:
    MODERNGL_AVAILABLE = False


class Native3DViewer(QtWidgets.QMainWindow):
    """Нативный 3D Viewer с использованием OpenGL"""
    
    def __init__(self, plan_data=None):
        super().__init__()
        
        # Настройка логирования
        self.logger = logging.getLogger("ROBOTY.native_3d")
        self.log_file = self.setup_logging()
        
        # Данные для визуализации
        self.plan_data = plan_data
        self.robots_data = []
        self.trajectories_data = []
        self.animation_time = 0.0
        self.animation_speed = 1.0
        self.is_playing = False
        
        # 3D настройки
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.camera_z = 10.0
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.zoom = 1.0
        
        # Настройка окна
        self.setup_window()
        self.setup_ui()
        
        # Инициализация 3D данных
        if self.plan_data:
            self.parse_plan_data()
        
        self.logger.info("Native 3D Viewer инициализирован")
    
    def setup_logging(self):
        """Настройка логирования"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"native_3d_viewer_{timestamp}.log")
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        logger = logging.getLogger("ROBOTY_NATIVE_3D_VIEWER")
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
        self.setWindowTitle("🖥️ ROBOTY Native 3D Viewer - Нативная 3D визуализация")
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
        
        # 3D область визуализации
        self.create_3d_area()
        
        # Панель управления анимацией
        self.create_animation_panel()
        
        # Нижняя панель с кнопками
        self.create_control_panel()
        
        # Статус бар
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к 3D визуализации")
    
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
        
        # Информация о 3D движке
        engine_info = "OpenGL" if OPENGL_AVAILABLE else "Fallback"
        self.engine_label = QtWidgets.QLabel(f"3D Движок: {engine_info}")
        self.engine_label.setStyleSheet("font-weight: bold; color: #8B4513;")
        info_layout.addWidget(self.engine_label)
        
        self.main_layout.addWidget(info_group)
    
    def create_3d_area(self):
        """Создает область для 3D визуализации"""
        if OPENGL_AVAILABLE:
            # Создаем OpenGL виджет
            self.gl_widget = OpenGL3DWidget(self)
            self.gl_widget.setMinimumHeight(400)
            self.main_layout.addWidget(self.gl_widget)
        else:
            # Fallback: создаем простой виджет с сообщением
            fallback_widget = QtWidgets.QLabel("""
            ❌ OpenGL недоступен
            
            Для нативной 3D визуализации необходимо установить:
            • PyOpenGL
            • PyOpenGL-accelerate
            
            Установите зависимости:
            pip install PyOpenGL PyOpenGL-accelerate
            """)
            fallback_widget.setAlignment(QtCore.Qt.AlignCenter)
            fallback_widget.setStyleSheet("""
                color: red; 
                font-size: 14px; 
                background-color: #f0f0f0; 
                border: 2px solid #ccc;
                padding: 20px;
            """)
            self.main_layout.addWidget(fallback_widget)
    
    def create_animation_panel(self):
        """Создает панель управления анимацией"""
        anim_group = QtWidgets.QGroupBox("🎬 Управление анимацией")
        anim_group.setMaximumHeight(80)
        anim_layout = QtWidgets.QHBoxLayout(anim_group)
        
        # Кнопка воспроизведения/паузы
        self.play_button = QtWidgets.QPushButton("▶️ Воспроизвести")
        self.play_button.setToolTip("Воспроизвести/приостановить анимацию")
        self.play_button.clicked.connect(self.toggle_animation)
        anim_layout.addWidget(self.play_button)
        
        # Слайдер времени
        self.time_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.time_slider.setRange(0, 1000)
        self.time_slider.setValue(0)
        self.time_slider.valueChanged.connect(self.set_animation_time)
        anim_layout.addWidget(self.time_slider)
        
        # Отображение времени
        self.current_time_label = QtWidgets.QLabel("0.00 сек")
        self.current_time_label.setMinimumWidth(80)
        anim_layout.addWidget(self.current_time_label)
        
        # Скорость анимации
        self.speed_label = QtWidgets.QLabel("Скорость:")
        anim_layout.addWidget(self.speed_label)
        
        self.speed_spinbox = QtWidgets.QDoubleSpinBox()
        self.speed_spinbox.setRange(0.1, 5.0)
        self.speed_spinbox.setValue(1.0)
        self.speed_spinbox.setSingleStep(0.1)
        self.speed_spinbox.valueChanged.connect(self.set_animation_speed)
        anim_layout.addWidget(self.speed_spinbox)
        
        self.main_layout.addWidget(anim_group)
    
    def create_control_panel(self):
        """Создает панель управления"""
        control_group = QtWidgets.QGroupBox("🎮 Управление")
        control_group.setMaximumHeight(80)
        control_layout = QtWidgets.QHBoxLayout(control_group)
        
        # Кнопка сброса камеры
        self.reset_camera_button = QtWidgets.QPushButton("📷 Сброс камеры")
        self.reset_camera_button.setToolTip("Сбросить позицию камеры")
        self.reset_camera_button.clicked.connect(self.reset_camera)
        control_layout.addWidget(self.reset_camera_button)
        
        # Кнопка экспорта
        self.export_button = QtWidgets.QPushButton("💾 Экспорт")
        self.export_button.setToolTip("Экспортировать данные визуализации")
        self.export_button.clicked.connect(self.export_data)
        control_layout.addWidget(self.export_button)
        
        control_layout.addStretch()
        
        # Кнопка закрытия
        self.close_button = QtWidgets.QPushButton("❌ Закрыть")
        self.close_button.setToolTip("Закрыть 3D Viewer")
        self.close_button.clicked.connect(self.close)
        control_layout.addWidget(self.close_button)
        
        self.main_layout.addWidget(control_group)
    
    def parse_plan_data(self):
        """Парсит данные плана для 3D визуализации"""
        if not self.plan_data:
            return
        
        try:
            self.robots_data = []
            self.trajectories_data = []
            
            robots = self.plan_data.get("robots", [])
            for robot in robots:
                robot_id = robot.get("id", 0)
                base_xyz = robot.get("base_xyz", [0, 0, 0])
                trajectory = robot.get("trajectory", [])
                
                # Сохраняем данные робота
                robot_data = {
                    "id": robot_id,
                    "base_xyz": base_xyz,
                    "color": self.get_robot_color(robot_id)
                }
                self.robots_data.append(robot_data)
                
                # Сохраняем траекторию
                trajectory_data = []
                for point in trajectory:
                    t = point.get("t", 0.0)
                    x = point.get("x", 0.0)
                    y = point.get("y", 0.0)
                    z = point.get("z", 0.0)
                    trajectory_data.append((t, x, y, z))
                
                self.trajectories_data.append(trajectory_data)
            
            # Обновляем информацию
            self.update_info_panel()
            
            # Обновляем слайдер времени
            if self.trajectories_data:
                max_time = max(max(point[0] for point in traj) for traj in self.trajectories_data)
                self.time_slider.setRange(0, int(max_time * 100))
            
            self.logger.info(f"Парсинг завершен: {len(self.robots_data)} роботов")
            
        except Exception as e:
            self.logger.error(f"Ошибка парсинга данных: {e}")
    
    def get_robot_color(self, robot_id):
        """Возвращает цвет для робота"""
        colors = [
            (1.0, 0.0, 0.0),  # Красный
            (0.0, 1.0, 0.0),  # Зеленый
            (0.0, 0.0, 1.0),  # Синий
            (1.0, 1.0, 0.0),  # Желтый
            (1.0, 0.0, 1.0),  # Пурпурный
            (0.0, 1.0, 1.0),  # Голубой
            (1.0, 0.5, 0.0),  # Оранжевый
            (0.5, 0.0, 1.0),  # Фиолетовый
        ]
        return colors[robot_id % len(colors)]
    
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
    
    def toggle_animation(self):
        """Переключает воспроизведение анимации"""
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_button.setText("⏸️ Пауза")
            self.start_animation_timer()
        else:
            self.play_button.setText("▶️ Воспроизвести")
            self.stop_animation_timer()
    
    def start_animation_timer(self):
        """Запускает таймер анимации"""
        self.animation_timer = QtCore.QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50)  # 20 FPS
    
    def stop_animation_timer(self):
        """Останавливает таймер анимации"""
        if hasattr(self, 'animation_timer'):
            self.animation_timer.stop()
    
    def update_animation(self):
        """Обновляет анимацию"""
        if not self.trajectories_data:
            return
        
        # Увеличиваем время анимации
        self.animation_time += 0.05 * self.animation_speed
        
        # Находим максимальное время
        max_time = max(max(point[0] for point in traj) for traj in self.trajectories_data)
        
        # Зацикливаем анимацию
        if self.animation_time > max_time:
            self.animation_time = 0.0
        
        # Обновляем слайдер
        self.time_slider.setValue(int(self.animation_time * 100))
        
        # Обновляем отображение времени
        self.current_time_label.setText(f"{self.animation_time:.2f} сек")
        
        # Обновляем 3D виджет
        if hasattr(self, 'gl_widget'):
            self.gl_widget.update()
    
    def set_animation_time(self, value):
        """Устанавливает время анимации"""
        self.animation_time = value / 100.0
        self.current_time_label.setText(f"{self.animation_time:.2f} сек")
        
        if hasattr(self, 'gl_widget'):
            self.gl_widget.update()
    
    def set_animation_speed(self, speed):
        """Устанавливает скорость анимации"""
        self.animation_speed = speed
    
    def reset_camera(self):
        """Сбрасывает позицию камеры"""
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.camera_z = 10.0
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.zoom = 1.0
        
        if hasattr(self, 'gl_widget'):
            self.gl_widget.update()
    
    def export_data(self):
        """Экспортирует данные визуализации"""
        try:
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Экспортировать данные", "roboty_3d_data.json",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                import json
                export_data = {
                    "robots": self.robots_data,
                    "trajectories": self.trajectories_data,
                    "plan": self.plan_data
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                self.status_bar.showMessage(f"💾 Данные экспортированы: {file_path}")
                self.logger.info(f"Данные экспортированы: {file_path}")
                
        except Exception as e:
            self.logger.error(f"Ошибка экспорта: {e}")
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать данные: {e}")
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        try:
            self.stop_animation_timer()
            self.logger.info("Закрытие Native 3D Viewer")
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии: {e}")
        
        event.accept()


class OpenGL3DWidget(QtOpenGLWidgets.QOpenGLWidget):
    """OpenGL виджет для 3D визуализации"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_viewer = parent
        self.last_pos = QtCore.QPoint()
    
    def initializeGL(self):
        """Инициализация OpenGL"""
        if not OPENGL_AVAILABLE:
            return
        
        try:
            # Настройка OpenGL
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glEnable(GL_COLOR_MATERIAL)
            glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
            
            # Настройка света
            glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 10, 1])
            glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])
            
            # Настройка материала
            glMaterialfv(GL_FRONT, GL_SPECULAR, [1, 1, 1, 1])
            glMaterialf(GL_FRONT, GL_SHININESS, 50)
            
            glClearColor(0.1, 0.1, 0.1, 1.0)
            
        except Exception as e:
            print(f"Ошибка инициализации OpenGL: {e}")
    
    def paintGL(self):
        """Отрисовка OpenGL"""
        if not OPENGL_AVAILABLE or not self.parent_viewer:
            return
        
        try:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            
            # Настройка камеры
            viewer = self.parent_viewer
            glTranslatef(viewer.camera_x, viewer.camera_y, -viewer.camera_z * viewer.zoom)
            glRotatef(viewer.rotation_x, 1, 0, 0)
            glRotatef(viewer.rotation_y, 0, 1, 0)
            
            # Отрисовка координатных осей
            self.draw_axes()
            
            # Отрисовка роботов и траекторий
            self.draw_robots_and_trajectories()
            
        except Exception as e:
            print(f"Ошибка отрисовки OpenGL: {e}")
    
    def draw_axes(self):
        """Отрисовка координатных осей"""
        if not OPENGL_AVAILABLE:
            return
        
        glDisable(GL_LIGHTING)
        glLineWidth(2)
        
        # X ось (красная)
        glColor3f(1, 0, 0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(5, 0, 0)
        glEnd()
        
        # Y ось (зеленая)
        glColor3f(0, 1, 0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 5, 0)
        glEnd()
        
        # Z ось (синяя)
        glColor3f(0, 0, 1)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 5)
        glEnd()
        
        glEnable(GL_LIGHTING)
    
    def draw_robots_and_trajectories(self):
        """Отрисовка роботов и траекторий"""
        if not OPENGL_AVAILABLE or not self.parent_viewer:
            return
        
        viewer = self.parent_viewer
        
        # Отрисовка траекторий
        for i, trajectory in enumerate(viewer.trajectories_data):
            if i < len(viewer.robots_data):
                color = viewer.robots_data[i]["color"]
                glColor3f(*color)
                
                glDisable(GL_LIGHTING)
                glLineWidth(3)
                glBegin(GL_LINE_STRIP)
                
                for point in trajectory:
                    t, x, y, z = point
                    glVertex3f(x, y, z)
                
                glEnd()
                glEnable(GL_LIGHTING)
        
        # Отрисовка роботов в текущей позиции
        for i, trajectory in enumerate(viewer.trajectories_data):
            if i < len(viewer.robots_data):
                robot_data = viewer.robots_data[i]
                color = robot_data["color"]
                
                # Находим текущую позицию робота
                current_pos = self.get_robot_position_at_time(trajectory, viewer.animation_time)
                
                if current_pos:
                    x, y, z = current_pos
                    
                    # Отрисовка робота (простой куб)
                    glColor3f(*color)
                    glPushMatrix()
                    glTranslatef(x, y, z)
                    self.draw_cube(0.3)
                    glPopMatrix()
    
    def get_robot_position_at_time(self, trajectory, time):
        """Получает позицию робота в заданное время"""
        if not trajectory:
            return None
        
        # Находим ближайшие точки
        for i in range(len(trajectory) - 1):
            t1, x1, y1, z1 = trajectory[i]
            t2, x2, y2, z2 = trajectory[i + 1]
            
            if t1 <= time <= t2:
                # Линейная интерполяция
                alpha = (time - t1) / (t2 - t1) if t2 != t1 else 0
                x = x1 + alpha * (x2 - x1)
                y = y1 + alpha * (y2 - y1)
                z = z1 + alpha * (z2 - z1)
                return (x, y, z)
        
        # Если время выходит за границы, возвращаем последнюю позицию
        if trajectory:
            _, x, y, z = trajectory[-1]
            return (x, y, z)
        
        return None
    
    def draw_cube(self, size):
        """Отрисовка куба"""
        if not OPENGL_AVAILABLE:
            return
        
        s = size / 2
        vertices = [
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],  # задняя грань
            [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s]       # передняя грань
        ]
        
        faces = [
            [0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1],
            [2, 6, 7, 3], [0, 3, 7, 4], [1, 5, 6, 2]
        ]
        
        glBegin(GL_QUADS)
        for face in faces:
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()
    
    def mousePressEvent(self, event):
        """Обработка нажатия мыши"""
        self.last_pos = event.position().toPoint()
    
    def mouseMoveEvent(self, event):
        """Обработка движения мыши"""
        if not self.parent_viewer:
            return
        
        dx = event.position().x() - self.last_pos.x()
        dy = event.position().y() - self.last_pos.y()
        
        if event.buttons() & QtCore.Qt.LeftButton:
            # Поворот камеры
            self.parent_viewer.rotation_y += dx * 0.5
            self.parent_viewer.rotation_x += dy * 0.5
            self.update()
        elif event.buttons() & QtCore.Qt.RightButton:
            # Панорамирование
            self.parent_viewer.camera_x += dx * 0.01
            self.parent_viewer.camera_y -= dy * 0.01
            self.update()
        
        self.last_pos = event.position().toPoint()
    
    def wheelEvent(self, event):
        """Обработка колесика мыши"""
        if not self.parent_viewer:
            return
        
        # Зум
        delta = event.angleDelta().y()
        if delta > 0:
            self.parent_viewer.zoom *= 1.1
        else:
            self.parent_viewer.zoom /= 1.1
        
        self.parent_viewer.zoom = max(0.1, min(10.0, self.parent_viewer.zoom))
        self.update()
    
    def resizeGL(self, width, height):
        """Обработка изменения размера"""
        if not OPENGL_AVAILABLE:
            return
        
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)


def main():
    """Главная функция для запуска Native 3D Viewer"""
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("ROBOTY Native 3D Viewer")
        app.setApplicationVersion("1.0")
        
        # Создаем окно без данных (для тестирования)
        window = Native3DViewer()
        window.show()
        
        logger = logging.getLogger("ROBOTY_NATIVE_3D_VIEWER.main")
        logger.info("Native 3D Viewer успешно запущен")
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Критическая ошибка при запуске Native 3D Viewer: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
