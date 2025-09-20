# -*- coding: utf-8 -*-
from PySide6 import QtWidgets, QtCore, QtGui
import json
import os
import math
import random
from datetime import datetime


class InputGeneratorDialog(QtWidgets.QDialog):
    """Диалог для генерации входных данных (JSON или TXT)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Генератор входных данных ROBOTY")
        self.setModal(True)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.resize(620, 420)

        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        layout.addLayout(form)

        # Основные параметры
        self.spin_robots = QtWidgets.QSpinBox()
        self.spin_robots.setRange(1, 200)
        self.spin_robots.setValue(10)
        form.addRow("Количество роботов:", self.spin_robots)

        self.spin_ops = QtWidgets.QSpinBox()
        self.spin_ops.setRange(0, 5000)
        self.spin_ops.setValue(30)
        form.addRow("Количество операций:", self.spin_ops)

        self.spin_safe = QtWidgets.QDoubleSpinBox()
        self.spin_safe.setRange(0.0, 10.0)
        self.spin_safe.setDecimals(3)
        self.spin_safe.setSingleStep(0.05)
        self.spin_safe.setValue(0.3)
        form.addRow("Safe distance (м):", self.spin_safe)

        self.spin_tool = QtWidgets.QDoubleSpinBox()
        self.spin_tool.setRange(0.0, 5.0)
        self.spin_tool.setDecimals(3)
        self.spin_tool.setSingleStep(0.05)
        self.spin_tool.setValue(0.1)
        form.addRow("Tool clearance (м):", self.spin_tool)

        self.spin_spacing = QtWidgets.QDoubleSpinBox()
        self.spin_spacing.setRange(0.1, 200.0)
        self.spin_spacing.setDecimals(2)
        self.spin_spacing.setSingleStep(0.1)
        self.spin_spacing.setValue(1.5)
        form.addRow("Шаг сетки (м):", self.spin_spacing)

        self.chk_random = QtWidgets.QCheckBox("Добавить случайность к позициям и параметрам")
        self.chk_random.setChecked(True)
        layout.addWidget(self.chk_random)

        seed_layout = QtWidgets.QHBoxLayout()
        self.spin_seed = QtWidgets.QSpinBox()
        self.spin_seed.setRange(0, 10_000_000)
        self.spin_seed.setValue(0)
        seed_layout.addWidget(QtWidgets.QLabel("Seed (0 — авто):"))
        seed_layout.addWidget(self.spin_seed)
        layout.addLayout(seed_layout)

        fmt_layout = QtWidgets.QHBoxLayout()
        fmt_layout.addWidget(QtWidgets.QLabel("Формат:"))
        self.combo_fmt = QtWidgets.QComboBox()
        self.combo_fmt.addItems(["JSON", "TXT"])
        fmt_layout.addWidget(self.combo_fmt)
        layout.addLayout(fmt_layout)

        # Путь сохранения
        path_layout = QtWidgets.QHBoxLayout()
        self.edit_path = QtWidgets.QLineEdit()
        default_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        os.makedirs(default_dir, exist_ok=True)
        default_name = f"input_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.edit_path.setText(os.path.join(default_dir, default_name))
        self.combo_fmt.currentTextChanged.connect(self._update_default_ext)
        btn_browse = QtWidgets.QPushButton("Выбрать...")
        btn_browse.clicked.connect(self.on_browse)
        path_layout.addWidget(self.edit_path)
        path_layout.addWidget(btn_browse)
        layout.addLayout(path_layout)

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

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        # При показе диалога используем только глобальный стиль приложения
        try:
            # Сбросим локальный стиль, чтобы наследовать app.setStyleSheet
            self.setStyleSheet("")
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
            spacing = self.spin_spacing.value()
            randomize = self.chk_random.isChecked()
            seed = self.spin_seed.value()
            if seed == 0:
                seed = int(datetime.now().timestamp())

            fmt = self.combo_fmt.currentText()
            path = self.edit_path.text()
            os.makedirs(os.path.dirname(path), exist_ok=True)

            if fmt == "JSON":
                data = self._build_json(n_robots, n_ops, safe_dist, tool_clear, spacing, randomize, seed)
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                content = self._build_txt(n_robots, n_ops, safe_dist, tool_clear, spacing, randomize, seed)
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

    def _grid_bases(self, n: int, spacing: float, randomize: bool, rng: random.Random):
        cols = max(1, int(math.ceil(math.sqrt(n))))
        rows = int(math.ceil(n / cols))
        bases = []
        idx = 0
        for r in range(rows):
            for c in range(cols):
                if idx >= n:
                    break
                x = c * spacing
                y = r * spacing
                if randomize:
                    x += rng.uniform(-0.1 * spacing, 0.1 * spacing)
                    y += rng.uniform(-0.1 * spacing, 0.1 * spacing)
                bases.append((round(x, 3), round(y, 3), 0.0))
                idx += 1
        return bases

    def _build_json(self, n_robots: int, n_ops: int, safe_dist: float, tool_clear: float, spacing: float, randomize: bool, seed: int) -> dict:
        rng = self._rng(randomize, seed)
        # Роботы
        bases = self._grid_bases(n_robots, spacing if not (n_robots >= 20 and spacing < 3.0) else 3.0, randomize, rng)
        robots = []
        for i, base in enumerate(bases, 1):
            vbase = 1.0 + (rng.uniform(-0.3, 0.5) if randomize else 0.0)
            abase = 2.0 + (rng.uniform(-0.5, 0.8) if randomize else 0.0)
            robots.append({
                "id": i,
                "base_xyz": list(base),
                "joint_limits": [[-180, 180], [-90, 90], [-90, 90], [-180, 180], [-90, 90], [-90, 90]],
                "vmax": [round(vbase, 2)] * 6,
                "amax": [round(abase, 2)] * 6,
                "tool_clearance": round(tool_clear, 3)
            })
        # Операции
        ops = []
        for i in range(n_ops):
            ridx = i % n_robots if n_robots > 0 else 0
            rb = robots[ridx]["base_xyz"]
            dx1, dy1 = rng.uniform(-0.7, 0.7), rng.uniform(-0.7, 0.7)
            dx2, dy2 = rng.uniform(-0.7, 0.7), rng.uniform(-0.7, 0.7)
            pick = [round(rb[0] + dx1, 3), round(rb[1] + dy1, 3), 0.0]
            place = [round(rb[0] + dx2, 3), round(rb[1] + dy2, 3), round(abs(dy2) * 0.5, 3)]
            t_hold = round(0.4 + (rng.random() * 0.8 if randomize else 0.6), 2)
            ops.append({"id": i + 1, "pick_xyz": pick, "place_xyz": place, "t_hold": t_hold})
        return {"robots": robots, "safe_dist": round(safe_dist, 3), "operations": ops}

    def _build_txt(self, n_robots: int, n_ops: int, safe_dist: float, tool_clear: float, spacing: float, randomize: bool, seed: int) -> str:
        rng = self._rng(randomize, seed)
        bases = self._grid_bases(n_robots, spacing if not (n_robots >= 20 and spacing < 3.0) else 3.0, randomize, rng)
        lines = []
        # K N
        lines.append(f"{n_robots} {n_ops}")
        # base positions
        for (x, y, z) in bases:
            lines.append(f"{x} {y} {z}")
        # 6 lines of joint limits (global template) with vmax/amax per joint
        for j in range(6):
            jmin, jmax = -180.0 if j in (0, 3) else -90.0, 180.0 if j in (0, 3) else 90.0
            vmax = 1.0 + (rng.uniform(-0.3, 0.5) if randomize else 0.0)
            amax = 2.0 + (rng.uniform(-0.5, 0.8) if randomize else 0.0)
            lines.append(f"{jmin} {jmax} {round(vmax,2)} {round(amax,2)}")
        # Tool_clearance Safe_dist
        lines.append(f"{round(tool_clear,3)} {round(safe_dist,3)}")
        # Operations
        for i in range(n_ops):
            ridx = i % n_robots if n_robots > 0 else 0
            bx, by, bz = bases[ridx]
            dx1, dy1 = rng.uniform(-0.7, 0.7), rng.uniform(-0.7, 0.7)
            dx2, dy2 = rng.uniform(-0.7, 0.7), rng.uniform(-0.7, 0.7)
            px, py, pz = round(bx + dx1, 3), round(by + dy1, 3), 0.0
            qx, qy, qz = round(bx + dx2, 3), round(by + dy2, 3), round(abs(dy2) * 0.5, 3)
            t_i = round(0.4 + (rng.random() * 0.8 if randomize else 0.6), 2)
            lines.append(f"{px} {py} {pz} {qx} {qy} {qz} {t_i}")
        return "\n".join(lines) + "\n"
