# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QSizePolicy,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(640, 480)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pushButton_load = QPushButton(self.centralwidget)
        self.pushButton_load.setObjectName(u"pushButton_load")

        self.verticalLayout.addWidget(self.pushButton_load)

        self.pushButton_run = QPushButton(self.centralwidget)
        self.pushButton_run.setObjectName(u"pushButton_run")

        self.verticalLayout.addWidget(self.pushButton_run)

        self.pushButton_viz = QPushButton(self.centralwidget)
        self.pushButton_viz.setObjectName(u"pushButton_viz")

        self.verticalLayout.addWidget(self.pushButton_viz)

        self.textLog = QTextEdit(self.centralwidget)
        self.textLog.setObjectName(u"textLog")
        self.textLog.setReadOnly(True)

        self.verticalLayout.addWidget(self.textLog)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Robot Planner", None))
        self.pushButton_load.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044c \u0432\u0445\u043e\u0434\u043d\u043e\u0439 \u0444\u0430\u0439\u043b", None))
        self.pushButton_run.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u043f\u0443\u0441\u0442\u0438\u0442\u044c \u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435", None))
        self.pushButton_viz.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u0432\u0438\u0437\u0443\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u044e", None))
        self.textLog.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u041b\u043e\u0433\u0438 \u0440\u0430\u0431\u043e\u0442\u044b \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u044b \u0431\u0443\u0434\u0443\u0442 \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0442\u044c\u0441\u044f \u0437\u0434\u0435\u0441\u044c...", None))
    # retranslateUi

import sys
from PyQt5 import QtWidgets, uic
from core.parser import parse_input_file
from core.planner import assign_operations, generate_waypoints
from core.collision import check_collision
from viz.visualizer import plot_trajectories

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/main_window.ui", self)
        self.pushButton_run.clicked.connect(self.run_planning)
        self.pushButton_visualize.clicked.connect(self.visualize)

    def run_planning(self):
        input_path = "data/input.txt"
        output_path = "data/output.txt"
        try:
            data = parse_input_file(input_path)
            robot_ops = assign_operations(data['K'], data['operations'])
            waypoints = generate_waypoints(robot_ops, data['joints'])
            collision_free = check_collision(waypoints, data['tool_clearance'], data['safe_dist'])
            self.label_status.setText("Коллизий нет" if collision_free else "Обнаружена коллизия")
            self.write_output_file(output_path, waypoints)
        except Exception as e:
            self.label_status.setText(f"Ошибка: {e}")

    def write_output_file(self, filepath, waypoints):
        makespan = max(wp[-1]['time'] if wp else 0 for wp in waypoints)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Makespan: {makespan:.2f}\n")
            for idx, wp in enumerate(waypoints):
                f.write(f"Robot {idx+1}: {len(wp)} waypoints\n")
                for point in wp:
                    x, y, z = point['pos']
                    t = point['time']
                    f.write(f"{t:.2f} {x:.2f} {y:.2f} {z:.2f}\n")

