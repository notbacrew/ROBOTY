# -*- coding: utf-8 -*-
from PySide6 import QtWidgets, QtCore, QtGui
import json
import os
import math
import random
from datetime import datetime


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
        space_layout.addRow("Высота пространства (м):", self.spin_space_height)

        self.spin_space_depth = QtWidgets.QDoubleSpinBox()
        self.spin_space_depth.setRange(1.0, 1000.0)
        self.spin_space_depth.setDecimals(2)
        self.spin_space_depth.setSingleStep(0.5)
        self.spin_space_depth.setValue(5.0)
        space_layout.addRow("Глубина пространства (м):", self.spin_space_depth)

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
        robot_layout = QtWidgets.QFormLayout(robot_group)
        
        self.combo_robot_layout = QtWidgets.QComboBox()
        self.combo_robot_layout.addItems([
            "Сетка (автоматически)",
            "Линия (вдоль X)",
            "Круг (по окружности)",
            "Случайно (равномерно)",
            "Случайно (кластеры)"
        ])
        robot_layout.addRow("Способ размещения:", self.combo_robot_layout)

        self.spin_robot_spacing = QtWidgets.QDoubleSpinBox()
        self.spin_robot_spacing.setRange(0.5, 50.0)
        self.spin_robot_spacing.setDecimals(2)
        self.spin_robot_spacing.setSingleStep(0.1)
        self.spin_robot_spacing.setValue(2.0)
        robot_layout.addRow("Расстояние между роботами (м):", self.spin_robot_spacing)

        self.spin_robot_margin = QtWidgets.QDoubleSpinBox()
        self.spin_robot_margin.setRange(0.0, 10.0)
        self.spin_robot_margin.setDecimals(2)
        self.spin_robot_margin.setSingleStep(0.1)
        self.spin_robot_margin.setValue(1.0)
        robot_layout.addRow("Отступ от краев (м):", self.spin_robot_margin)
        
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
        
        # Рекомендуемые размеры
        min_robot_spacing = 2.0  # минимальное расстояние между роботами
        recommended_width = math.ceil(math.sqrt(n_robots)) * min_robot_spacing
        recommended_height = math.ceil(math.sqrt(n_robots)) * min_robot_spacing
        
        # Проверяем, достаточно ли места
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
        
        recommendations = f"""
        <div style="color: {color};">
        <b>{status}</b><br>
        Рекомендуемые размеры: {recommended_width:.1f}×{recommended_height:.1f} м<br>
        Текущая площадь: {current_area:.1f} м²<br>
        Рекомендуемая площадь: {recommended_area:.1f} м²
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
        
        if layout_type == "Сетка (автоматически)":
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
                z = robot_margin + rng.uniform(0, effective_depth) if effective_depth > 0 else robot_margin
                positions.append((round(x, 3), round(y, 3), round(z, 3)))
                
        elif layout_type == "Линия (вдоль X)":
            # Линия вдоль X
            step_x = effective_width / max(1, n_robots - 1) if n_robots > 1 else 0
            for i in range(n_robots):
                x = robot_margin + i * step_x
                y = robot_margin + effective_height / 2
                z = robot_margin + rng.uniform(0, effective_depth) if effective_depth > 0 else robot_margin
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
                z = robot_margin + rng.uniform(0, effective_depth) if effective_depth > 0 else robot_margin
                positions.append((round(x, 3), round(y, 3), round(z, 3)))
                
        elif layout_type == "Случайно (равномерно)":
            # Случайное равномерное распределение
            for i in range(n_robots):
                x = robot_margin + rng.uniform(0, effective_width)
                y = robot_margin + rng.uniform(0, effective_height)
                z = robot_margin + rng.uniform(0, effective_depth) if effective_depth > 0 else robot_margin
                positions.append((round(x, 3), round(y, 3), round(z, 3)))
                
        elif layout_type == "Случайно (кластеры)":
            # Случайные кластеры
            n_clusters = max(1, n_robots // 3)
            cluster_size = n_robots // n_clusters
            
            for cluster in range(n_clusters):
                cluster_x = robot_margin + rng.uniform(0, effective_width)
                cluster_y = robot_margin + rng.uniform(0, effective_height)
                cluster_z = robot_margin + rng.uniform(0, effective_depth) if effective_depth > 0 else robot_margin
                
                cluster_robots = cluster_size if cluster < n_clusters - 1 else n_robots - cluster * cluster_size
                for i in range(cluster_robots):
                    x = cluster_x + rng.gauss(0, robot_spacing / 2)
                    y = cluster_y + rng.gauss(0, robot_spacing / 2)
                    z = cluster_z + rng.gauss(0, robot_spacing / 2)
                    
                    # Ограничиваем в пределах пространства
                    x = max(robot_margin, min(robot_margin + effective_width, x))
                    y = max(robot_margin, min(robot_margin + effective_height, y))
                    z = max(robot_margin, min(robot_margin + effective_depth, z))
                    
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
            pick_z = rng.uniform(robot_margin, robot_margin + space_depth - robot_margin)
            
            place_x = rng.uniform(robot_margin, robot_margin + space_width - robot_margin)
            place_y = rng.uniform(robot_margin, robot_margin + space_height - robot_margin)
            place_z = rng.uniform(robot_margin, robot_margin + space_depth - robot_margin)
            
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
            pick_z = rng.uniform(robot_margin, robot_margin + space_depth - robot_margin)
            
            place_x = rng.uniform(robot_margin, robot_margin + space_width - robot_margin)
            place_y = rng.uniform(robot_margin, robot_margin + space_height - robot_margin)
            place_z = rng.uniform(robot_margin, robot_margin + space_depth - robot_margin)
            
            px, py, pz = round(pick_x, 3), round(pick_y, 3), round(pick_z, 3)
            qx, qy, qz = round(place_x, 3), round(place_y, 3), round(place_z, 3)
            t_i = round(0.4 + (rng.random() * 0.8 if randomize else 0.6), 2)
            lines.append(f"{px} {py} {pz} {qx} {qy} {qz} {t_i}")
        
        return "\n".join(lines) + "\n"
