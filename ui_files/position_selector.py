from PySide6 import QtWidgets, QtCore, QtGui


class PositionSelectorDialog(QtWidgets.QDialog):
    """
    Диалог выбора позиций роботов на сетке (как шахматная доска).
    Пользователь последовательно выбирает клетки для каждого робота.
    Результат: список позиций [(x, y, z), ...] в метрах.
    """

    def __init__(self, parent=None, num_robots=1, tiles=12, tile_size=0.5, origin=(-3.0, -3.0), z_plane=0.0):
        super().__init__(parent)
        self.setWindowTitle("Выбор позиций роботов")
        self.setModal(True)

        self._num_robots = max(1, int(num_robots))
        self._tiles = int(tiles)
        self._tile_size = float(tile_size)
        self._origin_x = float(origin[0])
        self._origin_y = float(origin[1])
        self._z_plane = float(z_plane)

        self._selected_cells = []  # [(i, j)]
        self._robot_colors = self._generate_robot_colors(self._num_robots)

        # Левая панель: список роботов
        self._robots_list = QtWidgets.QListWidget(self)
        for idx in range(self._num_robots):
            item = QtWidgets.QListWidgetItem(f"R{idx+1}")
            icon = self._make_color_icon(self._robot_colors[idx])
            item.setIcon(icon)
            self._robots_list.addItem(item)
        self._robots_list.setFixedWidth(140)
        self._robots_list.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        self._label = QtWidgets.QLabel(self)
        self._label.setText(self._build_status_text())

        self._hint = QtWidgets.QLabel(self)
        self._hint.setText("ЛКМ — поставить робота. ПКМ — удалить. Готово — после выбора всех.")
        self._hint.setStyleSheet("color: #666;")

        self._grid = QtWidgets.QGridLayout()
        self._grid.setSpacing(2)

        self._buttons = {}
        for i in range(self._tiles):
            for j in range(self._tiles):
                btn = QtWidgets.QPushButton("")
                btn.setFixedSize(28, 28)
                # Раскраска как шахматная доска
                if (i + j) % 2 == 0:
                    btn.setStyleSheet("background-color: #eaeaea; border: 1px solid #c9c9c9;")
                else:
                    btn.setStyleSheet("background-color: #cfcfcf; border: 1px solid #b5b5b5;")
                btn.installEventFilter(self)
                btn.clicked.connect(self._make_on_click(i, j))
                self._grid.addWidget(btn, self._tiles - 1 - j, i)  # визуально Y вверх
                self._buttons[(i, j)] = btn

        # Легенда
        legend = QtWidgets.QHBoxLayout()
        legend.addWidget(self._legend_swatch("Свободно", QtGui.QColor('#e0e0e0')))
        legend.addWidget(self._legend_swatch("Занято", QtGui.QColor('#9e9e9e')))
        legend.addWidget(self._legend_swatch("Наведение", QtGui.QColor('#a0c4ff')))
        legend.addStretch()

        self._btn_auto = QtWidgets.QPushButton("Авторазмещение")
        self._btn_auto.clicked.connect(self._on_auto_place)

        self._btn_clear = QtWidgets.QPushButton("Сбросить выбор")
        self._btn_clear.clicked.connect(self._on_clear)

        self._btn_ok = QtWidgets.QPushButton("Готово")
        self._btn_ok.clicked.connect(self._on_ok)
        self._btn_ok.setEnabled(False)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(self._btn_auto)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self._btn_clear)
        bottom_layout.addWidget(self._btn_ok)

        # Центральная зона: слева список роботов, справа сетка и подсказки
        center = QtWidgets.QHBoxLayout()
        center.addWidget(self._robots_list)
        grid_area = QtWidgets.QVBoxLayout()
        grid_area.addWidget(self._label)
        grid_area.addLayout(legend)
        grid_area.addLayout(self._grid)
        grid_area.addWidget(self._hint)
        center.addLayout(grid_area)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(center)
        layout.addLayout(bottom_layout)

        self._update_ok_state()

    def _build_status_text(self) -> str:
        return f"Выберите позицию для робота {len(self._selected_cells) + 1} из {self._num_robots}"

    def _make_on_click(self, i, j):
        def handler():
            if len(self._selected_cells) >= self._num_robots:
                return
            if (i, j) in self._selected_cells:
                return
            self._selected_cells.append((i, j))
            btn = self._buttons.get((i, j))
            if btn is not None:
                btn.setEnabled(False)
                # Пиктограмма куба с номером робота
                color = self._robot_colors[len(self._selected_cells) - 1]
                pix = self._make_cube_pixmap(28, 28, len(self._selected_cells), color)
                btn.setIcon(QtGui.QIcon(pix))
                btn.setIconSize(QtCore.QSize(24, 24))
            self._label.setText(self._build_status_text())
            self._update_robot_list()
            self._update_ok_state()
        return handler

    def _on_clear(self):
        # Сбросить всё
        for (i, j), btn in self._buttons.items():
            btn.setEnabled(True)
            btn.setText("")
            btn.setIcon(QtGui.QIcon())
        self._selected_cells.clear()
        self._label.setText(self._build_status_text())
        self._update_robot_list()
        self._update_ok_state()

    def _update_ok_state(self):
        # Разрешаем завершить, когда выбраны все
        self._btn_ok.setEnabled(len(self._selected_cells) == self._num_robots)
        # Блокируем невыбранные клетки, когда достигнут лимит
        limit_reached = len(self._selected_cells) >= self._num_robots
        for (i, j), btn in self._buttons.items():
            if (i, j) not in self._selected_cells:
                btn.setEnabled(not limit_reached)

    def _on_ok(self):
        if len(self._selected_cells) != self._num_robots:
            return
        self.accept()

    def get_positions(self):
        """
        Возвращает список [(x, y, z)] для каждого выбранного робота в порядке выбора.
        Центр клетки: origin + (i+0.5,j+0.5) * tile_size.
        """
        positions = []
        for (i, j) in self._selected_cells:
            cx = self._origin_x + (i + 0.5) * self._tile_size
            cy = self._origin_y + (j + 0.5) * self._tile_size
            positions.append((cx, cy, self._z_plane))
        return positions

    def _make_cube_pixmap(self, w: int, h: int, number: int, color: QtGui.QColor) -> QtGui.QPixmap:
        """Рисует простую иконку изометрического куба с номером и цветом робота."""
        pix = QtGui.QPixmap(w, h)
        pix.fill(QtCore.Qt.GlobalColor.transparent)
        p = QtGui.QPainter(pix)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

        # Координаты куба
        margin = 4
        cw = w - 2 * margin
        ch = h - 2 * margin
        cx = margin
        cy = margin

        # Грани куба (упрощённая изометрия)
        top = QtGui.QPolygon([
            QtCore.QPoint(cx + cw * 0.2, cy),
            QtCore.QPoint(cx + cw * 0.8, cy),
            QtCore.QPoint(cx + cw, cy + ch * 0.3),
            QtCore.QPoint(cx + cw * 0.5, cy + ch * 0.5),
            QtCore.QPoint(cx, cy + ch * 0.3)
        ])
        left = QtGui.QPolygon([
            QtCore.QPoint(cx, cy + ch * 0.3),
            QtCore.QPoint(cx + cw * 0.5, cy + ch * 0.5),
            QtCore.QPoint(cx + cw * 0.5, cy + ch),
            QtCore.QPoint(cx, cy + ch * 0.8)
        ])
        right = QtGui.QPolygon([
            QtCore.QPoint(cx + cw * 0.5, cy + ch * 0.5),
            QtCore.QPoint(cx + cw, cy + ch * 0.3),
            QtCore.QPoint(cx + cw, cy + ch * 0.8),
            QtCore.QPoint(cx + cw * 0.5, cy + ch)
        ])

        p.setPen(QtGui.QPen(QtGui.QColor('#666'), 1))
        p.setBrush(color.lighter(120))
        p.drawPolygon(top)
        p.setBrush(color)
        p.drawPolygon(left)
        p.setBrush(color.darker(120))
        p.drawPolygon(right)

        # Номер робота
        f = QtGui.QFont()
        f.setPointSize(8)
        f.setBold(True)
        p.setFont(f)
        p.setPen(QtGui.QPen(QtGui.QColor('#222')))
        rect = QtCore.QRect(0, 0, w, h)
        p.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, f"R{number}")

        p.end()
        return pix

    def _make_color_icon(self, color: QtGui.QColor) -> QtGui.QIcon:
        pm = QtGui.QPixmap(16, 16)
        pm.fill(QtCore.Qt.GlobalColor.transparent)
        qp = QtGui.QPainter(pm)
        qp.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        qp.setBrush(color)
        qp.setPen(QtGui.QPen(QtGui.QColor('#555'), 1))
        qp.drawRoundedRect(1, 1, 14, 14, 3, 3)
        qp.end()
        return QtGui.QIcon(pm)

    def _generate_robot_colors(self, n: int):
        base = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b',
            '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
        colors = []
        for i in range(n):
            col = QtGui.QColor(base[i % len(base)])
            colors.append(col)
        return colors

    def _update_robot_list(self):
        # Помечаем уже размещённых
        for idx in range(self._robots_list.count()):
            item = self._robots_list.item(idx)
            placed = idx < len(self._selected_cells)
            text = f"R{idx+1}" + (" ✓" if placed else "")
            item.setText(text)

    def _legend_swatch(self, text: str, color: QtGui.QColor) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        h = QtWidgets.QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        sw = QtWidgets.QLabel()
        pm = QtGui.QPixmap(14, 14)
        pm.fill(color)
        sw.setPixmap(pm)
        h.addWidget(sw)
        h.addWidget(QtWidgets.QLabel(text))
        return w

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:
        # Наведение курсора — подсветка
        if isinstance(obj, QtWidgets.QPushButton):
            pos = None
            for (i, j), btn in self._buttons.items():
                if btn is obj:
                    pos = (i, j)
                    break
            if pos is not None:
                if event.type() == QtCore.QEvent.Type.Enter and obj.isEnabled():
                    obj.setStyleSheet("background-color: #a0c4ff; border: 1px solid #6699ff;")
                elif event.type() == QtCore.QEvent.Type.Leave and obj.isEnabled():
                    i, j = pos
                    if (i + j) % 2 == 0:
                        obj.setStyleSheet("background-color: #eaeaea; border: 1px solid #c9c9c9;")
                    else:
                        obj.setStyleSheet("background-color: #cfcfcf; border: 1px solid #b5b5b5;")
                elif event.type() == QtCore.QEvent.Type.MouseButtonPress:
                    me = event  # type: ignore
                    if hasattr(me, 'button') and me.button() == QtCore.Qt.MouseButton.RightButton:
                        # Удалить, если это занятая клетка
                        if pos in self._selected_cells:
                            self._selected_cells.remove(pos)
                            self._renumber_icons()
                            self._update_robot_list()
                            self._update_ok_state()
                            return True
        return super().eventFilter(obj, event)

    def _renumber_icons(self):
        # Очистить все и восстановить согласно новому порядку
        for (i, j), btn in self._buttons.items():
            if (i, j) not in self._selected_cells:
                btn.setEnabled(True)
                btn.setText("")
                btn.setIcon(QtGui.QIcon())
        for idx, (i, j) in enumerate(self._selected_cells, start=1):
            btn = self._buttons.get((i, j))
            if btn is not None:
                btn.setEnabled(False)
                color = self._robot_colors[idx - 1]
                pix = self._make_cube_pixmap(28, 28, idx, color)
                btn.setIcon(QtGui.QIcon(pix))
                btn.setIconSize(QtCore.QSize(24, 24))

    def _on_auto_place(self):
        # Простая авто-раскладка по шахматному шаблону слева-направо, снизу-вверх
        self._on_clear()
        count = 0
        for j in range(self._tiles):
            for i in range(self._tiles):
                if (i + j) % 2 == 0:
                    self._selected_cells.append((i, j))
                    count += 1
                    if count >= self._num_robots:
                        self._renumber_icons()
                        self._label.setText(self._build_status_text())
                        self._update_robot_list()
                        self._update_ok_state()
                        return
        # Если не хватило чёрно-белых, добираем остальные
        for j in range(self._tiles):
            for i in range(self._tiles):
                if (i, j) not in self._selected_cells:
                    self._selected_cells.append((i, j))
                    count += 1
                    if count >= self._num_robots:
                        self._renumber_icons()
                        self._label.setText(self._build_status_text())
                        self._update_robot_list()
                        self._update_ok_state()
                        return


