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
        self.spin_tool.setRange(0.0, 2.0)
        self.spin_tool.setDecimals(3)
        self.spin_tool.setSingleStep(0.01)
        self.spin_tool.setValue(0.1)
        basic_layout.addRow("Tool length (м):", self.spin_tool)
        
        layout.addWidget(basic_group)

        # Пространственные параметры
        space_group = QtWidgets.QGroupBox("📐 Пространственные параметры")
        space_layout = QtWidgets.QFormLayout(space_group)

        self.spin_space_x = QtWidgets.QDoubleSpinBox()
        self.spin_space_x.setRange(0.1, 50.0)
        self.spin_space_x.setDecimals(1)
        self.spin_space_x.setSingleStep(0.5)
        self.spin_space_x.setValue(6.0)
        space_layout.addRow("Размер X (м):", self.spin_space_x)

        self.spin_space_y = QtWidgets.QDoubleSpinBox()
        self.spin_space_y.setRange(0.1, 50.0)
        self.spin_space_y.setDecimals(1)
        self.spin_space_y.setSingleStep(0.5)
        self.spin_space_y.setValue(6.0)
        space_layout.addRow("Размер Y (м):", self.spin_space_y)

        self.spin_space_z = QtWidgets.QDoubleSpinBox()
        self.spin_space_z.setRange(0.1, 20.0)
        self.spin_space_z.setDecimals(1)
        self.spin_space_z.setSingleStep(0.1)
        self.spin_space_z.setValue(3.0)
        space_layout.addRow("Размер Z (м):", self.spin_space_z)
        
        layout.addWidget(space_group)

        # Параметры роботов
        robot_group = QtWidgets.QGroupBox("🦾 Параметры роботов")
        robot_layout = QtWidgets.QFormLayout(robot_group)

        self.spin_robot_reach = QtWidgets.QDoubleSpinBox()
        self.spin_robot_reach.setRange(0.1, 10.0)
        self.spin_robot_reach.setDecimals(2)
        self.spin_robot_reach.setSingleStep(0.1)
        self.spin_robot_reach.setValue(1.8)
        robot_layout.addRow("Радиус действия (м):", self.spin_robot_reach)

        self.spin_robot_margin = QtWidgets.QDoubleSpinBox()
        self.spin_robot_margin.setRange(0.0, 2.0)
        self.spin_robot_margin.setDecimals(2)
        self.spin_robot_margin.setSingleStep(0.05)
        self.spin_robot_margin.setValue(0.2)
        robot_layout.addRow("Отступ от края (м):", self.spin_robot_margin)
        
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

        self.chk_load = QtWidgets.QCheckBox("Загрузить созданный файл в приложение")
        self.chk_load.setChecked(True)
        path_layout.addWidget(self.chk_load)
        
        layout.addWidget(path_group)

        # Кнопки
        buttons_layout = QtWidgets.QHBoxLayout()
        
        self.btn_generate = QtWidgets.QPushButton("🎲 Сгенерировать")
        self.btn_generate.clicked.connect(self.generate_data)
        self.btn_generate.setMinimumHeight(40)
        self.btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 20px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        self.btn_cancel = QtWidgets.QPushButton("❌ Отмена")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_cancel.setMinimumHeight(40)
        
        buttons_layout.addWidget(self.btn_generate)
        buttons_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(buttons_layout)

        # Статус
        self.status_label = QtWidgets.QLabel("Готов к генерации данных")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

        self.saved_path = None
        self.load_into_app = False

    def _update_default_ext(self, fmt):
        """Обновляет расширение файла при смене формата"""
        path = self.edit_path.text()
        base_path = os.path.splitext(path)[0]
        ext = ".json" if fmt == "JSON" else ".txt"
        self.edit_path.setText(base_path + ext)

    def on_browse(self):
        """Открывает диалог выбора файла для сохранения"""
        fmt = self.combo_fmt.currentText()
        ext = "*.json" if fmt == "JSON" else "*.txt"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, 
            f"Сохранить {fmt} файл", 
            self.edit_path.text(),
            f"{fmt} файлы ({ext});;Все файлы (*.*)"
        )
        if path:
            self.edit_path.setText(path)

    def generate_data(self):
        """Генерирует входные данные согласно настройкам"""
        try:
            self.status_label.setText("Генерация данных...")
            self.status_label.repaint()

            # Получаем параметры
            num_robots = self.spin_robots.value()
            num_ops = self.spin_ops.value()
            safe_dist = self.spin_safe.value()
            tool_length = self.spin_tool.value()
            
            space_x = self.spin_space_x.value()
            space_y = self.spin_space_y.value()
            space_z = self.spin_space_z.value()
            
            robot_reach = self.spin_robot_reach.value()
            robot_margin = self.spin_robot_margin.value()
            
            use_random = self.chk_random.isChecked()
            seed = self.spin_seed.value() if self.spin_seed.value() > 0 else None
            
            if seed:
                random.seed(seed)

            # Генерируем роботов
            robots = []
            for i in range(num_robots):
                if use_random:
                    x = random.uniform(-space_x/2 + robot_margin, space_x/2 - robot_margin)
                    y = random.uniform(-space_y/2 + robot_margin, space_y/2 - robot_margin)
                    z = random.uniform(0.1, space_z * 0.3)
                else:
                    # Равномерное распределение по сетке
                    grid_size = int(math.ceil(math.sqrt(num_robots)))
                    row = i // grid_size
                    col = i % grid_size
                    x = -space_x/2 + robot_margin + (col + 0.5) * (space_x - 2*robot_margin) / grid_size
                    y = -space_y/2 + robot_margin + (row + 0.5) * (space_y - 2*robot_margin) / grid_size
                    z = 0.1

                robot = {
                    "id": i + 1,
                    "base_xyz": [round(x, 3), round(y, 3), round(z, 3)],
                    "reach": round(robot_reach + (random.uniform(-0.1, 0.1) if use_random else 0), 2),
                    "tool_length": round(tool_length + (random.uniform(-0.02, 0.02) if use_random else 0), 3)
                }
                robots.append(robot)

            # Генерируем операции
            operations = []
            for i in range(num_ops):
                if use_random:
                    x = random.uniform(-space_x/2, space_x/2)
                    y = random.uniform(-space_y/2, space_y/2)
                    z = random.uniform(0.1, space_z * 0.8)
                else:
                    # Равномерное распределение
                    x = -space_x/2 + (i % int(space_x * 10)) * 0.1
                    y = -space_y/2 + (i // int(space_x * 10)) * 0.1
                    z = 0.1 + (i % 20) * 0.1

                operation = {
                    "id": i + 1,
                    "target_xyz": [round(x, 3), round(y, 3), round(z, 3)],
                    "duration": round(random.uniform(1.0, 10.0) if use_random else 5.0, 1),
                    "priority": random.randint(1, 5) if use_random else 3
                }
                operations.append(operation)

            # Создаем структуру данных
            data = {
                "robots": robots,
                "operations": operations,
                "safe_distance": safe_dist,
                "space_bounds": {
                    "x_min": -space_x/2,
                    "x_max": space_x/2,
                    "y_min": -space_y/2,
                    "y_max": space_y/2,
                    "z_min": 0.0,
                    "z_max": space_z
                },
                "generation_params": {
                    "num_robots": num_robots,
                    "num_operations": num_ops,
                    "use_random": use_random,
                    "seed": seed,
                    "generated_at": datetime.now().isoformat()
                }
            }

            # Сохраняем файл
            output_path = self.edit_path.text()
            fmt = self.combo_fmt.currentText()
            
            if fmt == "JSON":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:  # TXT
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"# ROBOTY Input File\n")
                    f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    f.write(f"ROBOTS {num_robots}\n")
                    f.write(f"OPERATIONS {num_ops}\n")
                    f.write(f"SAFE_DISTANCE {safe_dist}\n")
                    f.write(f"SPACE_X {space_x}\n")
                    f.write(f"SPACE_Y {space_y}\n")
                    f.write(f"SPACE_Z {space_z}\n\n")
                    
                    f.write("# Robots\n")
                    for robot in robots:
                        f.write(f"ROBOT {robot['id']} {robot['base_xyz'][0]} {robot['base_xyz'][1]} {robot['base_xyz'][2]} {robot['reach']} {robot['tool_length']}\n")
                    
                    f.write("\n# Operations\n")
                    for op in operations:
                        f.write(f"OPERATION {op['id']} {op['target_xyz'][0]} {op['target_xyz'][1]} {op['target_xyz'][2]} {op['duration']} {op['priority']}\n")

            self.saved_path = output_path
            self.load_into_app = self.chk_load.isChecked()
            
            self.status_label.setText(f"✅ Данные сохранены: {os.path.basename(output_path)}")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            
            # Показываем информацию о созданных данных
            info_text = f"""
Создано:
• Роботов: {num_robots}
• Операций: {num_ops}
• Размер пространства: {space_x}×{space_y}×{space_z} м
• Safe distance: {safe_dist} м
• Формат: {fmt}
• Файл: {os.path.basename(output_path)}
            """.strip()
            
            QtWidgets.QMessageBox.information(self, "Генерация завершена", info_text)
            self.accept()

        except Exception as e:
            error_msg = f"Ошибка генерации: {str(e)}"
            self.status_label.setText(error_msg)
            self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")
            QtWidgets.QMessageBox.critical(self, "Ошибка", error_msg)
