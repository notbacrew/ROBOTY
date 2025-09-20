# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window_improved.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGroupBox,
    QGridLayout, QHBoxLayout, QLabel, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QSpacerItem,
    QSpinBox, QStatusBar, QTextEdit, QVBoxLayout,
    QWidget)
from PySide6.QtGui import QAction

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_main = QVBoxLayout(self.centralwidget)
        self.verticalLayout_main.setObjectName(u"verticalLayout_main")
        
        # Группа для работы с файлами
        self.groupBox_file = QGroupBox(self.centralwidget)
        self.groupBox_file.setObjectName(u"groupBox_file")
        self.groupBox_file.setTitle("📁 Работа с файлами")
        self.horizontalLayout_file = QHBoxLayout(self.groupBox_file)
        self.horizontalLayout_file.setObjectName(u"horizontalLayout_file")
        
        self.pushButton_load = QPushButton(self.groupBox_file)
        self.pushButton_load.setObjectName(u"pushButton_load")
        self.pushButton_load.setText("📂 Загрузить файл")
        self.horizontalLayout_file.addWidget(self.pushButton_load)
        
        self.pushButton_save = QPushButton(self.groupBox_file)
        self.pushButton_save.setObjectName(u"pushButton_save")
        self.pushButton_save.setText("💾 Сохранить результат")
        self.horizontalLayout_file.addWidget(self.pushButton_save)
        
        self.horizontalSpacer_file = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_file.addItem(self.horizontalSpacer_file)
        
        self.verticalLayout_main.addWidget(self.groupBox_file)
        
        # Группа для выбора алгоритмов
        self.groupBox_algorithm = QGroupBox(self.centralwidget)
        self.groupBox_algorithm.setObjectName(u"groupBox_algorithm")
        self.groupBox_algorithm.setTitle("🧠 Алгоритмы и настройки")
        self.gridLayout_algorithm = QGridLayout(self.groupBox_algorithm)
        self.gridLayout_algorithm.setObjectName(u"gridLayout_algorithm")
        
        # Метод назначения операций
        self.label_assignment_method = QLabel(self.groupBox_algorithm)
        self.label_assignment_method.setObjectName(u"label_assignment_method")
        self.label_assignment_method.setText("Метод назначения операций:")
        self.gridLayout_algorithm.addWidget(self.label_assignment_method, 0, 0, 1, 1)
        
        self.comboBox_assignment_method = QComboBox(self.groupBox_algorithm)
        self.comboBox_assignment_method.setObjectName(u"comboBox_assignment_method")
        self.comboBox_assignment_method.addItems([
            "Round Robin (по очереди)",
            "Balanced (балансировка нагрузки)", 
            "Distance Based (по расстоянию)",
            "Genetic Algorithm (генетический)"
        ])
        self.comboBox_assignment_method.setCurrentIndex(1)  # По умолчанию Balanced
        self.gridLayout_algorithm.addWidget(self.comboBox_assignment_method, 0, 1, 1, 1)
        
        # Настройки генетического алгоритма
        self.label_genetic_population = QLabel(self.groupBox_algorithm)
        self.label_genetic_population.setObjectName(u"label_genetic_population")
        self.label_genetic_population.setText("Размер популяции (генетический):")
        self.gridLayout_algorithm.addWidget(self.label_genetic_population, 1, 0, 1, 1)
        
        self.spinBox_population_size = QSpinBox(self.groupBox_algorithm)
        self.spinBox_population_size.setObjectName(u"spinBox_population_size")
        self.spinBox_population_size.setMinimum(10)
        self.spinBox_population_size.setMaximum(200)
        self.spinBox_population_size.setValue(50)
        self.gridLayout_algorithm.addWidget(self.spinBox_population_size, 1, 1, 1, 1)
        
        self.label_genetic_generations = QLabel(self.groupBox_algorithm)
        self.label_genetic_generations.setObjectName(u"label_genetic_generations")
        self.label_genetic_generations.setText("Количество поколений (генетический):")
        self.gridLayout_algorithm.addWidget(self.label_genetic_generations, 2, 0, 1, 1)
        
        self.spinBox_generations = QSpinBox(self.groupBox_algorithm)
        self.spinBox_generations.setObjectName(u"spinBox_generations")
        self.spinBox_generations.setMinimum(10)
        self.spinBox_generations.setMaximum(500)
        self.spinBox_generations.setValue(100)
        self.gridLayout_algorithm.addWidget(self.spinBox_generations, 2, 1, 1, 1)
        
        # Дополнительные опции
        self.checkBox_optimize_trajectories = QCheckBox(self.groupBox_algorithm)
        self.checkBox_optimize_trajectories.setObjectName(u"checkBox_optimize_trajectories")
        self.checkBox_optimize_trajectories.setText("Оптимизация траекторий")
        self.checkBox_optimize_trajectories.setChecked(True)
        self.gridLayout_algorithm.addWidget(self.checkBox_optimize_trajectories, 3, 0, 1, 1)
        
        self.checkBox_path_planning = QCheckBox(self.groupBox_algorithm)
        self.checkBox_path_planning.setObjectName(u"checkBox_path_planning")
        self.checkBox_path_planning.setText("Планирование пути")
        self.gridLayout_algorithm.addWidget(self.checkBox_path_planning, 3, 1, 1, 1)
        
        self.verticalLayout_main.addWidget(self.groupBox_algorithm)
        
        # Группа управления
        self.groupBox_control = QGroupBox(self.centralwidget)
        self.groupBox_control.setObjectName(u"groupBox_control")
        self.groupBox_control.setTitle("🎮 Выполнение")
        self.horizontalLayout_control = QHBoxLayout(self.groupBox_control)
        self.horizontalLayout_control.setObjectName(u"horizontalLayout_control")
        
        self.pushButton_run = QPushButton(self.groupBox_control)
        self.pushButton_run.setObjectName(u"pushButton_run")
        self.pushButton_run.setText("🚀 Запустить планирование")
        self.horizontalLayout_control.addWidget(self.pushButton_run)
        
        self.pushButton_viz = QPushButton(self.groupBox_control)
        self.pushButton_viz.setObjectName(u"pushButton_viz")
        self.pushButton_viz.setText("📊 Открыть визуализацию")
        self.horizontalLayout_control.addWidget(self.pushButton_viz)
        
        self.pushButton_clear_logs = QPushButton(self.groupBox_control)
        self.pushButton_clear_logs.setObjectName(u"pushButton_clear_logs")
        self.pushButton_clear_logs.setText("🗑️ Очистить")
        self.horizontalLayout_control.addWidget(self.pushButton_clear_logs)
        
        self.horizontalSpacer_control = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_control.addItem(self.horizontalSpacer_control)
        
        self.verticalLayout_main.addWidget(self.groupBox_control)
        
        # Группа логов
        self.groupBox_logs = QGroupBox(self.centralwidget)
        self.groupBox_logs.setObjectName(u"groupBox_logs")
        self.groupBox_logs.setTitle("📋 Логи и результаты")
        self.verticalLayout_logs = QVBoxLayout(self.groupBox_logs)
        self.verticalLayout_logs.setObjectName(u"verticalLayout_logs")
        
        self.textLog = QTextEdit(self.groupBox_logs)
        self.textLog.setObjectName(u"textLog")
        self.textLog.setReadOnly(True)
        self.textLog.setPlaceholderText("Логи работы программы будут отображаться здесь...")
        self.verticalLayout_logs.addWidget(self.textLog)
        
        self.verticalLayout_main.addWidget(self.groupBox_logs)
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        # Меню
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuFile.setTitle("Файл")
        
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuHelp.setTitle("Справка")
        
        MainWindow.setMenuBar(self.menubar)
        
        # Статус бар
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        # Действия меню
        self.actionLoad = QAction(MainWindow)
        self.actionLoad.setObjectName(u"actionLoad")
        self.actionLoad.setText("Загрузить файл")
        self.actionLoad.setShortcut(QKeySequence("Ctrl+O"))
        
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.actionSave.setText("Сохранить")
        self.actionSave.setShortcut(QKeySequence("Ctrl+S"))
        
        self.actionSaveAs = QAction(MainWindow)
        self.actionSaveAs.setObjectName(u"actionSaveAs")
        self.actionSaveAs.setText("Сохранить как...")
        self.actionSaveAs.setShortcut(QKeySequence("Ctrl+Shift+S"))
        
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionExit.setText("Выход")
        self.actionExit.setShortcut(QKeySequence("Ctrl+Q"))
        
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionAbout.setText("О программе")
        
        # Добавляем действия в меню
        self.menuFile.addAction(self.actionLoad)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        
        self.menuHelp.addAction(self.actionAbout)
        
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        
        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"ROBOTY - Система планирования траекторий роботов", None))
        
        # Настройка видимости элементов генетического алгоритма
        self.updateGeneticControlsVisibility()

    def updateGeneticControlsVisibility(self):
        """Обновляет видимость элементов управления генетическим алгоритмом"""
        is_genetic = self.comboBox_assignment_method.currentText().startswith("Genetic")
        self.label_genetic_population.setVisible(is_genetic)
        self.spinBox_population_size.setVisible(is_genetic)
        self.label_genetic_generations.setVisible(is_genetic)
        self.spinBox_generations.setVisible(is_genetic)

    def get_assignment_method(self):
        """Возвращает выбранный метод назначения операций"""
        method_map = {
            "Round Robin (по очереди)": "round_robin",
            "Balanced (балансировка нагрузки)": "balanced",
            "Distance Based (по расстоянию)": "distance_based",
            "Genetic Algorithm (генетический)": "genetic"
        }
        return method_map.get(self.comboBox_assignment_method.currentText(), "balanced")

    def get_genetic_parameters(self):
        """Возвращает параметры генетического алгоритма"""
        return {
            "population_size": self.spinBox_population_size.value(),
            "generations": self.spinBox_generations.value()
        }

    def get_optimization_settings(self):
        """Возвращает настройки оптимизации"""
        return {
            "optimize_trajectories": self.checkBox_optimize_trajectories.isChecked(),
            "path_planning": self.checkBox_path_planning.isChecked()
        }
