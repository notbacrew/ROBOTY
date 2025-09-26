from PySide6 import QtWidgets, QtCore


class PastePositionsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, expected_count: int = 1):
        super().__init__(parent)
        self.setWindowTitle("Вставьте позиции роботов (JSON)")
        self.setModal(True)
        self._expected = max(1, int(expected_count))
        self.text = QtWidgets.QPlainTextEdit(self)
        self.text.setPlaceholderText("Вставьте сюда JSON из кнопки 'Скопировать позиции'\nпример: [{\"robotIndex\":0,\"x\":0,\"y\":0,\"z\":0.0}]")
        self.text.setMinimumSize(480, 260)
        self.label = QtWidgets.QLabel(f"Ожидается записей: {self._expected}")
        self.btn_ok = QtWidgets.QPushButton("Применить")
        self.btn_cancel = QtWidgets.QPushButton("Отмена")
        self.btn_ok.clicked.connect(self._on_ok)
        self.btn_cancel.clicked.connect(self.reject)
        bottom = QtWidgets.QHBoxLayout()
        bottom.addStretch()
        bottom.addWidget(self.btn_cancel)
        bottom.addWidget(self.btn_ok)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.text)
        layout.addLayout(bottom)
        self._parsed = None

    def _on_ok(self):
        try:
            import json
            data = json.loads(self.text.toPlainText())
            if isinstance(data, list):
                # не строго требуем точное совпадение количества
                self._parsed = data
                self.accept()
            else:
                QtWidgets.QMessageBox.warning(self, "Формат", "Ожидается массив JSON.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Ошибка", f"Некорректный JSON: {e}")

    def get_data(self):
        return self._parsed
