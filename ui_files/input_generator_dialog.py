# -*- coding: utf-8 -*-
from PySide6 import QtWidgets, QtCore, QtGui
import json
import os
import math
import random
from datetime import datetime


class ChessFieldWidget(QtWidgets.QWidget):
    """Виджет шахматного поля для точного размещения роботов"""
    
    positions_changed = QtCore.Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.robot_positions = set()  # Множество выбранных позиций (row, col)
        self.grid_size = 8  # Размер сетки 8x8
        self.cell_size = 40  # Размер ячейки в пикселях
        self.max_robots = 64  # Максимальное количество роботов (8x8)
        self.setMinimumSize(self.grid_size * self.cell_size, self.grid_size * self.cell_size)
        self.setMaximumSize(self.grid_size * self.cell_size, self.grid_size * self.cell_size)
        
    def paintEvent(self, event):
        """Отрисовка шахматного поля"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Очищаем фон
        painter.fillRect(self.rect(), QtGui.QColor(240, 240, 240))
        
        # Рисуем сетку
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = col * self.cell_size
                y = row * self.cell_size
                
                # Чередующиеся цвета для шахматного поля
                if (row + col) % 2 == 0:
                    color = QtGui.QColor(255, 255, 255)  # Белый
                else:
                    color = QtGui.QColor(200, 200, 200)  # Серый
                
                # Если в ячейке есть робот, делаем ячейку белой
                if (row, col) in self.robot_positions:
                    color = QtGui.QColor(255, 255, 255)  # Белый для ячеек с роботами
                
                painter.fillRect(x, y, self.cell_size, self.cell_size, color)
                
                # Рисуем границы ячеек
                painter.setPen(QtGui.QPen(QtGui.QColor(100, 100, 100), 1))
                painter.drawRect(x, y, self.cell_size, self.cell_size)
                
                # Рисуем координаты
                painter.setPen(QtGui.QPen(QtGui.QColor(50, 50, 50), 1))
                font = painter.font()
                font.setPointSize(8)
                painter.setFont(font)
                painter.drawText(x + 2, y + 12, f"{row},{col}")
                
                # Рисуем робота, если позиция выбрана
                if (row, col) in self.robot_positions:
                    center_x = x + self.cell_size // 2
                    center_y = y + self.cell_size // 2
                    radius = self.cell_size // 3
                    
                    # Рисуем круг робота
                    painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 100, 100)))
                    painter.setPen(QtGui.QPen(QtGui.QColor(200, 0, 0), 2))
                    painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
                    
                    # Рисуем номер робота
                    painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 2))
                    font = painter.font()
                    font.setPointSize(10)
                    font.setBold(True)
                    painter.setFont(font)
                    robot_num = len([p for p in self.robot_positions if p <= (row, col)])
                    painter.drawText(center_x - 5, center_y + 3, str(robot_num))
    
    def mousePressEvent(self, event):
        """Обработка клика мыши"""
        if event.button() == QtCore.Qt.LeftButton:
            col = event.x() // self.cell_size
            row = event.y() // self.cell_size
            
            if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
                if (row, col) in self.robot_positions:
                    # Убираем робота
                    self.robot_positions.remove((row, col))
                else:
                    # Проверяем лимит роботов
                    if len(self.robot_positions) >= self.max_robots:
                        # Показываем сообщение о превышении лимита
                        from PySide6.QtWidgets import QMessageBox
                        QMessageBox.warning(self, "Превышен лимит", 
                                          f"Максимальное количество роботов: {self.max_robots}\n"
                                          f"Выберите большее количество роботов в настройках.")
                        return
                    # Добавляем робота
                    self.robot_positions.add((row, col))
                
                self.update()
                self.positions_changed.emit()
    
    def clear_all(self):
        """Очистить все позиции"""
        self.robot_positions.clear()
        self.update()
        self.positions_changed.emit()
    
    def get_positions(self):
        """Получить список позиций роботов"""
        return sorted(list(self.robot_positions))
    
    def set_positions(self, positions):
        """Установить позиции роботов"""
        self.robot_positions = set(positions)
        self.update()
        self.positions_changed.emit()
    
    def get_robot_count(self):
        """Получить количество выбранных роботов"""
        return len(self.robot_positions)
    
    def set_max_robots(self, max_robots):
        """Установить максимальное количество роботов"""
        # Если max_robots = 0, то лимит не установлен (можно добавлять сколько угодно)
        # Если max_robots > 0, то ограничиваем размером поля
        if max_robots > 0:
            self.max_robots = min(max_robots, 64)  # Не больше размера поля
        else:
            self.max_robots = 64  # По умолчанию - размер поля


class InputGeneratorDialog(QtWidgets.QDialog):
    """Диалог для генерации входных данных (JSON или TXT) с настройками пространства"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Генератор входных данных ROBOTY")
        self.setModal(True)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.resize(720, 600)

        # Создаем скроллируемую область
        scroll_area = QtWidgets.QScrollArea()
        scroll_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(scroll_area)

        # Основные параметры
        basic_group = QtWidgets.QGroupBox("🤖 Основные параметры")
        basic_layout = QtWidgets.QFormLayout(basic_group)
        
        self.spin_robots = QtWidgets.QSpinBox()
        self.spin_robots.setRange(1, 200)
        self.spin_robots.setValue(10)
        basic_layout.addRow("Количество роботов:", self.spin_robots)

        self.spin_ops = QtWidgets.QSpinBox()
        self.spin_ops.setRange(0, 5000)
        self.spin_ops.setValue(30)
        basic_layout.addRow("Количество операций:", self.spin_ops)

        self.spin_safe = QtWidgets.QDoubleSpinBox()
        self.spin_safe.setRange(0.0, 10.0)
        self.spin_safe.setDecimals(3)
        self.spin_safe.setSingleStep(0.05)
        self.spin_safe.setValue(0.3)
        basic_layout.addRow("Safe distance (м):", self.spin_safe)

        self.spin_tool = QtWidgets.QDoubleSpinBox()
        self.spin_tool.setRange(0.0, 5.0)
        self.spin_tool.setDecimals(3)
        self.spin_tool.setSingleStep(0.05)
        self.spin_tool.setValue(0.1)
        basic_layout.addRow("Tool clearance (м):", self.spin_tool)
        
        layout.addWidget(basic_group)

        # Настройки пространства
        space_group = QtWidgets.QGroupBox("🌍 Настройки пространства")
        space_layout = QtWidgets.QFormLayout(space_group)
        
        # Размеры пространства
        self.spin_space_width = QtWidgets.QDoubleSpinBox()
        self.spin_space_width.setRange(1.0, 1000.0)
        self.spin_space_width.setDecimals(2)
        self.spin_space_width.setSingleStep(0.5)
        self.spin_space_width.setValue(10.0)
        space_layout.addRow("Ширина пространства (м):", self.spin_space_width)

        self.spin_space_height = QtWidgets.QDoubleSpinBox()
        self.spin_space_height.setRange(1.0, 1000.0)
        self.spin_space_height.setDecimals(2)
        self.spin_space_height.setSingleStep(0.5)
        self.spin_space_height.setValue(10.0)
        space_layout.addRow("Длина пространства (м):", self.spin_space_height)

        self.spin_space_depth = QtWidgets.QDoubleSpinBox()
        self.spin_space_depth.setRange(1.0, 1000.0)
        self.spin_space_depth.setDecimals(2)
        self.spin_space_depth.setSingleStep(0.5)
        self.spin_space_depth.setValue(5.0)
        space_layout.addRow("Высота пространства (м, для операций):", self.spin_space_depth)

        # Рекомендации по размерам
        self.label_recommendations = QtWidgets.QLabel()
        self.label_recommendations.setWordWrap(True)
        self.label_recommendations.setStyleSheet("color: #666; font-style: italic;")
        self.update_recommendations()
        space_layout.addRow("Рекомендации:", self.label_recommendations)
        
        # Подключаем сигналы для обновления рекомендаций
        self.spin_robots.valueChanged.connect(self.update_recommendations)
        self.spin_space_width.valueChanged.connect(self.update_recommendations)
        self.spin_space_height.valueChanged.connect(self.update_recommendations)
        self.spin_space_depth.valueChanged.connect(self.update_recommendations)
        
        layout.addWidget(space_group)

        # Расположение роботов
        robot_group = QtWidgets.QGroupBox("📍 Расположение роботов")
        self.robot_layout = QtWidgets.QFormLayout(robot_group)
        
        self.combo_robot_layout = QtWidgets.QComboBox()
        self.combo_robot_layout.addItems([
            "Шахматное поле (точное размещение)",
            "Сетка (автоматически)",
            "Линия (вдоль X)",
            "Круг (по окружности)",
            "Случайно (равномерно)",
            "Случайно (кластеры)"
        ])
        self.robot_layout.addRow("Способ размещения:", self.combo_robot_layout)

        # Шахматное поле для точного размещения
        self.chess_widget = QtWidgets.QWidget()
        chess_layout = QtWidgets.QVBoxLayout(self.chess_widget)
        
        chess_info = QtWidgets.QLabel("🎯 Выберите позиции роботов на шахматном поле:")
        chess_info.setStyleSheet("font-weight: bold; color: #2E8B57;")
        chess_layout.addWidget(chess_info)
        
        # Создаем шахматное поле
        self.chess_field = ChessFieldWidget()
        self.chess_field.setMinimumSize(400, 300)
        chess_layout.addWidget(self.chess_field)
        
        # Кнопки управления шахматным полем
        chess_buttons = QtWidgets.QHBoxLayout()
        
        self.btn_clear_robots = QtWidgets.QPushButton("🗑️ Очистить все")
        self.btn_clear_robots.clicked.connect(self.chess_field.clear_all)
        chess_buttons.addWidget(self.btn_clear_robots)
        
        self.btn_fill_grid = QtWidgets.QPushButton("📋 Заполнить сеткой")
        self.btn_fill_grid.clicked.connect(self.fill_chess_grid)
        chess_buttons.addWidget(self.btn_fill_grid)
        
        self.btn_random_place = QtWidgets.QPushButton("🎲 Случайно")
        self.btn_random_place.clicked.connect(self.random_place_robots)
        chess_buttons.addWidget(self.btn_random_place)
        
        chess_layout.addLayout(chess_buttons)
        
        # Информация о выбранных позициях
        self.robot_positions_info = QtWidgets.QLabel("Выбрано роботов: 0")
        self.robot_positions_info.setStyleSheet("color: #4682B4; font-weight: bold;")
        chess_layout.addWidget(self.robot_positions_info)
        
        # Подключаем сигнал обновления позиций
        self.chess_field.positions_changed.connect(self.update_robot_positions_info)
        
        self.robot_layout.addRow(self.chess_widget)

        self.spin_robot_spacing = QtWidgets.QDoubleSpinBox()
        self.spin_robot_spacing.setRange(0.5, 50.0)
        self.spin_robot_spacing.setDecimals(2)
        self.spin_robot_spacing.setSingleStep(0.1)
        self.spin_robot_spacing.setValue(2.0)
        self.robot_layout.addRow("Расстояние между роботами (м):", self.spin_robot_spacing)

        self.spin_robot_margin = QtWidgets.QDoubleSpinBox()
        self.spin_robot_margin.setRange(0.0, 10.0)
        self.spin_robot_margin.setDecimals(2)
        self.spin_robot_margin.setSingleStep(0.1)
        self.spin_robot_margin.setValue(1.0)
        self.robot_layout.addRow("Отступ от краев (м):", self.spin_robot_margin)
        
        # Подключаем изменение способа размещения
        self.combo_robot_layout.currentTextChanged.connect(self.on_layout_type_changed)
        
        layout.addWidget(robot_group)

        # Дополнительные настройки
        advanced_group = QtWidgets.QGroupBox("⚙️ Дополнительные настройки")
        advanced_layout = QtWidgets.QFormLayout(advanced_group)

        self.chk_random = QtWidgets.QCheckBox("Добавить случайность к позициям и параметрам")
        self.chk_random.setChecked(True)
        advanced_layout.addRow(self.chk_random)

        seed_layout = QtWidgets.QHBoxLayout()
        self.spin_seed = QtWidgets.QSpinBox()
        self.spin_seed.setRange(0, 10_000_000)
        self.spin_seed.setValue(0)
        seed_layout.addWidget(QtWidgets.QLabel("Seed (0 — авто):"))
        seed_layout.addWidget(self.spin_seed)
        advanced_layout.addRow(seed_layout)

        fmt_layout = QtWidgets.QHBoxLayout()
        fmt_layout.addWidget(QtWidgets.QLabel("Формат:"))
        self.combo_fmt = QtWidgets.QComboBox()
        self.combo_fmt.addItems(["JSON", "TXT"])
        fmt_layout.addWidget(self.combo_fmt)
        advanced_layout.addRow(fmt_layout)
        
        layout.addWidget(advanced_group)

        # Путь сохранения
        path_group = QtWidgets.QGroupBox("💾 Сохранение")
        path_layout = QtWidgets.QVBoxLayout(path_group)
        
        path_input_layout = QtWidgets.QHBoxLayout()
        self.edit_path = QtWidgets.QLineEdit()
        default_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        os.makedirs(default_dir, exist_ok=True)
        default_name = f"input_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.edit_path.setText(os.path.join(default_dir, default_name))
        self.combo_fmt.currentTextChanged.connect(self._update_default_ext)
        btn_browse = QtWidgets.QPushButton("Выбрать...")
        btn_browse.clicked.connect(self.on_browse)
        path_input_layout.addWidget(self.edit_path)
        path_input_layout.addWidget(btn_browse)
        path_layout.addLayout(path_input_layout)
        
        layout.addWidget(path_group)

        # Кнопки
        btns = QtWidgets.QDialogButtonBox()
        self.btn_generate_load = btns.addButton("Сгенерировать и загрузить", QtWidgets.QDialogButtonBox.AcceptRole)
        self.btn_generate_save = btns.addButton("Сгенерировать и сохранить", QtWidgets.QDialogButtonBox.ApplyRole)
        self.btn_cancel = btns.addButton(QtWidgets.QDialogButtonBox.Cancel)
        layout.addWidget(btns)

        self.btn_generate_load.clicked.connect(lambda: self.on_generate(load_into_app=True))
        self.btn_generate_save.clicked.connect(lambda: self.on_generate(load_into_app=False))
        
        # Инициализация шахматного поля
        self.chess_widget.setVisible(False)  # Скрываем по умолчанию
        
        # Показываем обычные элементы по умолчанию
        self.spin_robot_spacing.setVisible(True)
        self.spin_robot_margin.setVisible(True)
        
        # Устанавливаем начальное состояние
        self.on_layout_type_changed(self.combo_robot_layout.currentText())
        
        self.btn_cancel.clicked.connect(self.reject)

        # Результаты
        self.saved_path = None
        self.load_into_app = False

    def update_recommendations(self):
        """Обновляет рекомендации по размерам пространства"""
        n_robots = self.spin_robots.value()
        width = self.spin_space_width.value()
        height = self.spin_space_height.value()
        depth = self.spin_space_depth.value()
        
        # Рекомендуемые размеры для роботов (они стоят на полу)
        min_robot_spacing = 2.0  # минимальное расстояние между роботами
        recommended_width = math.ceil(math.sqrt(n_robots)) * min_robot_spacing
        recommended_height = math.ceil(math.sqrt(n_robots)) * min_robot_spacing
        
        # Рекомендуемая высота для операций (роботы стоят на z=0, операции на разной высоте)
        recommended_depth = max(2.0, n_robots * 0.3)  # минимум 2м, плюс 0.3м на робота
        
        # Проверяем, достаточно ли места для роботов
        current_area = width * height
        recommended_area = recommended_width * recommended_height
        
        if current_area < recommended_area:
            status = "⚠️ Мало места для роботов"
            color = "#d32f2f"
        elif current_area < recommended_area * 1.5:
            status = "✅ Достаточно места"
            color = "#388e3c"
        else:
            status = "✅ Много места"
            color = "#1976d2"
        
        # Проверяем высоту для операций
        if depth < recommended_depth:
            height_status = "⚠️ Мало высоты для операций"
            height_color = "#d32f2f"
        else:
            height_status = "✅ Достаточно высоты"
            height_color = "#388e3c"
        
        recommendations = f"""
        <div style="color: {color};">
        <b>{status}</b><br>
        Рекомендуемые размеры: {recommended_width:.1f}×{recommended_height:.1f} м<br>
        Текущая площадь: {current_area:.1f} м²<br>
        Рекомендуемая площадь: {recommended_area:.1f} м²<br>
        <div style="color: {height_color}; margin-top: 5px;">
        <b>{height_status}</b><br>
        Рекомендуемая высота: {recommended_depth:.1f} м<br>
        Текущая высота: {depth:.1f} м<br>
        <small>Роботы стоят на полу (z=0), операции на разной высоте</small>
        </div>
        </div>
        """
        
        self.label_recommendations.setText(recommendations)

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        # При показе диалога используем только глобальный стиль приложения
        try:
            # Сбросим локальный стиль, чтобы наследовать app.setStyleSheet
            self.setStyleSheet("")
            # Убедимся, что все дочерние виджеты наследуют стиль
            for widget in self.findChildren(QtWidgets.QWidget):
                if hasattr(widget, 'setStyleSheet'):
                    widget.setStyleSheet("")
        except Exception:
            pass
        return super().showEvent(event)

    def _update_default_ext(self):
        path = self.edit_path.text()
        if not path:
            return
        base, ext = os.path.splitext(path)
        if self.combo_fmt.currentText() == "JSON":
            self.edit_path.setText(base + ".json")
        else:
            self.edit_path.setText(base + ".txt")

    def on_browse(self):
        fmt = self.combo_fmt.currentText()
        filt = "JSON Files (*.json)" if fmt == "JSON" else "Text Files (*.txt)"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Сохранить входной файл", self.edit_path.text(), filt)
        if path:
            self.edit_path.setText(path)

    def on_generate(self, load_into_app: bool):
        try:
            n_robots = self.spin_robots.value()
            n_ops = self.spin_ops.value()
            safe_dist = self.spin_safe.value()
            tool_clear = self.spin_tool.value()
            space_width = self.spin_space_width.value()
            space_height = self.spin_space_height.value()
            space_depth = self.spin_space_depth.value()
            robot_spacing = self.spin_robot_spacing.value()
            robot_margin = self.spin_robot_margin.value()
            robot_layout = self.combo_robot_layout.currentText()
            randomize = self.chk_random.isChecked()
            seed = self.spin_seed.value()
            if seed == 0:
                seed = int(datetime.now().timestamp())

            fmt = self.combo_fmt.currentText()
            path = self.edit_path.text()
            os.makedirs(os.path.dirname(path), exist_ok=True)

            if fmt == "JSON":
                data = self._build_json(n_robots, n_ops, safe_dist, tool_clear, 
                                      space_width, space_height, space_depth,
                                      robot_spacing, robot_margin, robot_layout,
                                      randomize, seed)
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                content = self._build_txt(n_robots, n_ops, safe_dist, tool_clear,
                                        space_width, space_height, space_depth,
                                        robot_spacing, robot_margin, robot_layout,
                                        randomize, seed)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)

            self.saved_path = path
            self.load_into_app = load_into_app
            self.accept()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка генерации", f"Не удалось сгенерировать входной файл: {e}")

    @staticmethod
    def _rng(randomize: bool, seed: int) -> random.Random:
        rng = random.Random()
        rng.seed(seed)
        return rng

    def _generate_robot_positions(self, n_robots: int, space_width: float, space_height: float, 
                                 space_depth: float, robot_spacing: float, robot_margin: float,
                                 layout_type: str, rng: random.Random) -> list:
        """Генерирует позиции роботов в зависимости от выбранного типа размещения"""
        positions = []
        
        # Учитываем отступы
        effective_width = space_width - 2 * robot_margin
        effective_height = space_height - 2 * robot_margin
        effective_depth = space_depth - 2 * robot_margin
        
        if layout_type == "Шахматное поле (точное размещение)":
            # Используем позиции с шахматного поля
            return self._generate_chess_positions(space_width, space_height, space_depth, 
                                                robot_spacing, robot_margin)
        
        elif layout_type == "Сетка (автоматически)":
            # Автоматическая сетка
            cols = max(1, int(math.ceil(math.sqrt(n_robots))))
            rows = int(math.ceil(n_robots / cols))
            
            step_x = effective_width / max(1, cols - 1) if cols > 1 else 0
            step_y = effective_height / max(1, rows - 1) if rows > 1 else 0
            
            for i in range(n_robots):
                row = i // cols
                col = i % cols
                x = robot_margin + col * step_x
                y = robot_margin + row * step_y
                z = 0.0  # Роботы всегда стоят на земле
                positions.append((round(x, 3), round(y, 3), round(z, 3)))
                
        elif layout_type == "Линия (вдоль X)":
            # Линия вдоль X
            step_x = effective_width / max(1, n_robots - 1) if n_robots > 1 else 0
            for i in range(n_robots):
                x = robot_margin + i * step_x
                y = robot_margin + effective_height / 2
                z = 0.0  # Роботы всегда стоят на земле
                positions.append((round(x, 3), round(y, 3), round(z, 3)))
                
        elif layout_type == "Круг (по окружности)":
            # Круг
            radius = min(effective_width, effective_height) / 2 - robot_spacing
            center_x = robot_margin + effective_width / 2
            center_y = robot_margin + effective_height / 2
            
            for i in range(n_robots):
                angle = 2 * math.pi * i / n_robots
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                z = 0.0  # Роботы всегда стоят на земле
                positions.append((round(x, 3), round(y, 3), round(z, 3)))
                
        elif layout_type == "Случайно (равномерно)":
            # Случайное равномерное распределение
            for i in range(n_robots):
                x = robot_margin + rng.uniform(0, effective_width)
                y = robot_margin + rng.uniform(0, effective_height)
                z = 0.0  # Роботы всегда стоят на земле
                positions.append((round(x, 3), round(y, 3), round(z, 3)))
                
        elif layout_type == "Случайно (кластеры)":
            # Случайные кластеры
            n_clusters = max(1, n_robots // 3)
            cluster_size = n_robots // n_clusters
            
            for cluster in range(n_clusters):
                cluster_x = robot_margin + rng.uniform(0, effective_width)
                cluster_y = robot_margin + rng.uniform(0, effective_height)
                cluster_z = 0.0  # Роботы всегда стоят на земле
                
                cluster_robots = cluster_size if cluster < n_clusters - 1 else n_robots - cluster * cluster_size
                for i in range(cluster_robots):
                    x = cluster_x + rng.gauss(0, robot_spacing / 2)
                    y = cluster_y + rng.gauss(0, robot_spacing / 2)
                    
                    # Ограничиваем в пределах пространства
                    x = max(robot_margin, min(robot_margin + effective_width, x))
                    y = max(robot_margin, min(robot_margin + effective_height, y))
                    z = 0.0  # Роботы всегда стоят на полу (z = 0)
                    
                    positions.append((round(x, 3), round(y, 3), round(z, 3)))
        
        return positions

    def _build_json(self, n_robots: int, n_ops: int, safe_dist: float, tool_clear: float,
                   space_width: float, space_height: float, space_depth: float,
                   robot_spacing: float, robot_margin: float, layout_type: str,
                   randomize: bool, seed: int) -> dict:
        rng = self._rng(randomize, seed)
        
        # Генерируем позиции роботов
        robot_positions = self._generate_robot_positions(
            n_robots, space_width, space_height, space_depth,
            robot_spacing, robot_margin, layout_type, rng
        )
        
        # Создаем роботов
        robots = []
        for i, pos in enumerate(robot_positions, 1):
            vbase = 1.0 + (rng.uniform(-0.3, 0.5) if randomize else 0.0)
            abase = 2.0 + (rng.uniform(-0.5, 0.8) if randomize else 0.0)
            robots.append({
                "id": i,
                "base_xyz": list(pos),
                "joint_limits": [[-180, 180], [-90, 90], [-90, 90], [-180, 180], [-90, 90], [-90, 90]],
                "vmax": [round(vbase, 2)] * 6,
                "amax": [round(abase, 2)] * 6,
                "tool_clearance": round(tool_clear, 3)
            })
        
        # Генерируем операции в пределах пространства
        operations = []
        for i in range(n_ops):
            # Случайные точки в пределах пространства
            pick_x = rng.uniform(robot_margin, robot_margin + space_width - robot_margin)
            pick_y = rng.uniform(robot_margin, robot_margin + space_height - robot_margin)
            # Pick операции на разной высоте (от 0.1 до 0.8 от высоты пространства)
            pick_z = rng.uniform(0.1, max(0.1, space_depth * 0.8))
            
            place_x = rng.uniform(robot_margin, robot_margin + space_width - robot_margin)
            place_y = rng.uniform(robot_margin, robot_margin + space_height - robot_margin)
            # Place операции на разной высоте (от 0.1 до 0.8 от высоты пространства)
            place_z = rng.uniform(0.1, max(0.1, space_depth * 0.8))
            
            pick = [round(pick_x, 3), round(pick_y, 3), round(pick_z, 3)]
            place = [round(place_x, 3), round(place_y, 3), round(place_z, 3)]
            t_hold = round(0.4 + (rng.random() * 0.8 if randomize else 0.6), 2)
            
            operations.append({
                "id": i + 1,
                "pick_xyz": pick,
                "place_xyz": place,
                "t_hold": t_hold
            })
        
        return {
            "robots": robots,
            "safe_dist": round(safe_dist, 3),
            "operations": operations,
            "space_settings": {
                "width": space_width,
                "height": space_height,
                "depth": space_depth,
                "robot_layout": layout_type
            }
        }

    def _build_txt(self, n_robots: int, n_ops: int, safe_dist: float, tool_clear: float,
                  space_width: float, space_height: float, space_depth: float,
                  robot_spacing: float, robot_margin: float, layout_type: str,
                  randomize: bool, seed: int) -> str:
        rng = self._rng(randomize, seed)
        
        # Генерируем позиции роботов
        robot_positions = self._generate_robot_positions(
            n_robots, space_width, space_height, space_depth,
            robot_spacing, robot_margin, layout_type, rng
        )
        
        lines = []
        # K N
        lines.append(f"{n_robots} {n_ops}")
        
        # Позиции роботов
        for (x, y, z) in robot_positions:
            lines.append(f"{x} {y} {z}")
        
        # 6 строк ограничений суставов
        for j in range(6):
            jmin, jmax = -180.0 if j in (0, 3) else -90.0, 180.0 if j in (0, 3) else 90.0
            vmax = 1.0 + (rng.uniform(-0.3, 0.5) if randomize else 0.0)
            amax = 2.0 + (rng.uniform(-0.5, 0.8) if randomize else 0.0)
            lines.append(f"{jmin} {jmax} {round(vmax,2)} {round(amax,2)}")
        
        # Tool_clearance Safe_dist
        lines.append(f"{round(tool_clear,3)} {round(safe_dist,3)}")
        
        # Операции в пределах пространства
        for i in range(n_ops):
            pick_x = rng.uniform(robot_margin, robot_margin + space_width - robot_margin)
            pick_y = rng.uniform(robot_margin, robot_margin + space_height - robot_margin)
            # Pick операции на разной высоте (от 0.1 до 0.8 от высоты пространства)
            pick_z = rng.uniform(0.1, max(0.1, space_depth * 0.8))
            
            place_x = rng.uniform(robot_margin, robot_margin + space_width - robot_margin)
            place_y = rng.uniform(robot_margin, robot_margin + space_height - robot_margin)
            # Place операции на разной высоте (от 0.1 до 0.8 от высоты пространства)
            place_z = rng.uniform(0.1, max(0.1, space_depth * 0.8))
            
            px, py, pz = round(pick_x, 3), round(pick_y, 3), round(pick_z, 3)
            qx, qy, qz = round(place_x, 3), round(place_y, 3), round(place_z, 3)
            t_i = round(0.4 + (rng.random() * 0.8 if randomize else 0.6), 2)
            lines.append(f"{px} {py} {pz} {qx} {qy} {qz} {t_i}")
        
        return "\n".join(lines) + "\n"
    
    def on_layout_type_changed(self, layout_type):
        """Обработка изменения типа размещения"""
        if layout_type == "Шахматное поле (точное размещение)":
            # Показываем шахматное поле
            self.chess_widget.setVisible(True)
            
            # Скрываем ненужные элементы
            self.spin_robot_spacing.setVisible(False)
            self.spin_robot_margin.setVisible(False)
            
            # Находим и скрываем лейблы для ненужных элементов
            for i in range(self.robot_layout.count()):
                item = self.robot_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if isinstance(widget, QtWidgets.QLabel):
                        if "Расстояние между роботами" in widget.text():
                            widget.setVisible(False)
                        elif "Отступ от краев" in widget.text():
                            widget.setVisible(False)
            
            # Обновляем количество роботов в соответствии с выбранными позициями
            robot_count = self.chess_field.get_robot_count()
            if robot_count > 0:
                self.spin_robots.setValue(robot_count)
        else:
            # Скрываем шахматное поле
            self.chess_widget.setVisible(False)
            
            # Показываем обычные элементы
            self.spin_robot_spacing.setVisible(True)
            self.spin_robot_margin.setVisible(True)
            
            # Показываем лейблы
            for i in range(self.robot_layout.count()):
                item = self.robot_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if isinstance(widget, QtWidgets.QLabel):
                        widget.setVisible(True)
    
    def update_robot_positions_info(self):
        """Обновление информации о выбранных позициях"""
        count = self.chess_field.get_robot_count()
        max_robots = self.spin_robots.value()
        
        # Устанавливаем лимит для шахматного поля
        # Если в спинбоксе установлено значение > 0, используем его как лимит
        # Если 0, то без ограничений
        if max_robots > 0:
            self.chess_field.set_max_robots(max_robots)
        else:
            self.chess_field.set_max_robots(0)  # Без ограничений
        
        if max_robots > 0:
            self.robot_positions_info.setText(f"Выбрано роботов: {count}/{max_robots}")
        else:
            self.robot_positions_info.setText(f"Выбрано роботов: {count}")
        
        # НЕ обновляем количество роботов в спинбоксе автоматически
        # Пользователь сам контролирует это значение
    
    def fill_chess_grid(self):
        """Заполнить шахматное поле сеткой роботов"""
        n_robots = self.spin_robots.value()
        positions = []
        
        # Заполняем по строкам
        for i in range(n_robots):
            row = i // 8
            col = i % 8
            if row < 8:  # Не выходим за границы поля
                positions.append((row, col))
        
        self.chess_field.set_positions(positions)
    
    def random_place_robots(self):
        """Случайно разместить роботов на шахматном поле"""
        n_robots = self.spin_robots.value()
        positions = []
        
        # Генерируем случайные позиции
        all_positions = [(r, c) for r in range(8) for c in range(8)]
        random.shuffle(all_positions)
        
        for i in range(min(n_robots, len(all_positions))):
            positions.append(all_positions[i])
        
        self.chess_field.set_positions(positions)
    
    def _generate_chess_positions(self, space_width: float, space_height: float, 
                                 space_depth: float, robot_spacing: float, 
                                 robot_margin: float) -> list:
        """Генерация позиций роботов на основе шахматного поля"""
        positions = []
        chess_positions = self.chess_field.get_positions()
        
        if not chess_positions:
            # Если позиции не выбраны, используем fallback - размещаем роботов в центре
            n_robots = self.spin_robots.value()
            if n_robots > 0:
                # Размещаем роботов в центре пространства
                center_x = space_width / 2
                center_y = space_height / 2
                
                # Размещаем роботов в линию по X на полу
                for i in range(n_robots):
                    x = center_x + (i - n_robots/2) * robot_spacing
                    y = center_y
                    z = 0.0  # Роботы всегда стоят на полу (z = 0)
                    positions.append((round(x, 3), round(y, 3), round(z, 3)))
            return positions
        
        # Вычисляем размер ячейки в реальных координатах
        effective_width = space_width - 2 * robot_margin
        effective_height = space_height - 2 * robot_margin
        
        cell_width = effective_width / 8
        cell_height = effective_height / 8
        
        for row, col in chess_positions:
            # Центр ячейки
            x = robot_margin + col * cell_width + cell_width / 2
            y = robot_margin + row * cell_height + cell_height / 2
            z = 0.0  # Роботы всегда стоят на полу (z = 0)
            
            positions.append((round(x, 3), round(y, 3), round(z, 3)))
        
        return positions
