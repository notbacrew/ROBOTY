# -*- coding: utf-8 -*-
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGroupBox,
    QGridLayout, QHBoxLayout, QLabel, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QSpacerItem,
    QSpinBox, QStatusBar, QTextEdit, QVBoxLayout,
    QWidget, QSplitter, QProgressBar)
from PySide6.QtGui import QAction

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1200, 800)  # Увеличил размер для лучшего размещения
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        
        # Главный вертикальный layout
        self.verticalLayout_main = QVBoxLayout(self.centralwidget)
        self.verticalLayout_main.setObjectName(u"verticalLayout_main")
        self.verticalLayout_main.setContentsMargins(10, 10, 10, 10)  # Отступы от краев
        self.verticalLayout_main.setSpacing(15)  # Расстояние между группами
        
        # Группа для работы с файлами
        self.groupBox_file = QGroupBox(self.centralwidget)
        self.groupBox_file.setObjectName(u"groupBox_file")
        self.groupBox_file.setTitle("📁 Работа с файлами")
        self.groupBox_file.setMaximumHeight(80)  # Ограничиваем высоту
        self.horizontalLayout_file = QHBoxLayout(self.groupBox_file)
        self.horizontalLayout_file.setObjectName(u"horizontalLayout_file")
        self.horizontalLayout_file.setContentsMargins(15, 10, 15, 10)
        self.horizontalLayout_file.setSpacing(10)
        
        # Основные кнопки файлов
        self.pushButton_load = QPushButton(self.groupBox_file)
        self.pushButton_load.setObjectName(u"pushButton_load")
        self.pushButton_load.setText("📂 Загрузить файл")
        self.pushButton_load.setMinimumHeight(35)
        self.horizontalLayout_file.addWidget(self.pushButton_load)
        
        self.pushButton_save = QPushButton(self.groupBox_file)
        self.pushButton_save.setObjectName(u"pushButton_save")
        self.pushButton_save.setText("💾 Сохранить результат")
        self.pushButton_save.setMinimumHeight(35)
        self.horizontalLayout_file.addWidget(self.pushButton_save)
        
        # Отступ
        self.horizontalSpacer_file = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_file.addItem(self.horizontalSpacer_file)
        
        # Генератор входных данных
        self.pushButton_input_gen = QPushButton(self.groupBox_file)
        self.pushButton_input_gen.setObjectName(u"pushButton_input_gen")
        self.pushButton_input_gen.setText("📥 Генератор входных данных")
        self.pushButton_input_gen.setToolTip("Создать входной файл (JSON или TXT) и загрузить его")
        self.pushButton_input_gen.setMinimumHeight(35)
        self.pushButton_input_gen.setStyleSheet("""
            QPushButton {
                background-color: #9B30FF;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #6A0DAD;
            }
        """)
        self.horizontalLayout_file.addWidget(self.pushButton_input_gen)
        
        self.verticalLayout_main.addWidget(self.groupBox_file)
        
        # Группа для выбора алгоритмов
        self.groupBox_algorithm = QGroupBox(self.centralwidget)
        self.groupBox_algorithm.setObjectName(u"groupBox_algorithm")
        self.groupBox_algorithm.setTitle("🧠 Алгоритмы и настройки")
        self.groupBox_algorithm.setMaximumHeight(200)  # Ограничиваем высоту
        self.gridLayout_algorithm = QGridLayout(self.groupBox_algorithm)
        self.gridLayout_algorithm.setObjectName(u"gridLayout_algorithm")
        self.gridLayout_algorithm.setContentsMargins(15, 15, 15, 15)
        self.gridLayout_algorithm.setSpacing(10)
        
        # Первая строка: Метод назначения операций
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
        self.comboBox_assignment_method.setCurrentIndex(1)
        self.gridLayout_algorithm.addWidget(self.comboBox_assignment_method, 0, 1, 1, 1)
        
        # Вторая строка: Настройки генетического алгоритма
        self.label_genetic_population = QLabel(self.groupBox_algorithm)
        self.label_genetic_population.setObjectName(u"label_genetic_population")
        self.label_genetic_population.setText("Размер популяции:")
        self.gridLayout_algorithm.addWidget(self.label_genetic_population, 1, 0, 1, 1)
        
        self.spinBox_population_size = QSpinBox(self.groupBox_algorithm)
        self.spinBox_population_size.setObjectName(u"spinBox_population_size")
        self.spinBox_population_size.setMinimum(10)
        self.spinBox_population_size.setMaximum(200)
        self.spinBox_population_size.setValue(50)
        self.gridLayout_algorithm.addWidget(self.spinBox_population_size, 1, 1, 1, 1)
        
        # Третья строка: Количество поколений
        self.label_genetic_generations = QLabel(self.groupBox_algorithm)
        self.label_genetic_generations.setObjectName(u"label_genetic_generations")
        self.label_genetic_generations.setText("Количество поколений:")
        self.gridLayout_algorithm.addWidget(self.label_genetic_generations, 2, 0, 1, 1)
        
        self.spinBox_generations = QSpinBox(self.groupBox_algorithm)
        self.spinBox_generations.setObjectName(u"spinBox_generations")
        self.spinBox_generations.setMinimum(10)
        self.spinBox_generations.setMaximum(500)
        self.spinBox_generations.setValue(100)
        self.gridLayout_algorithm.addWidget(self.spinBox_generations, 2, 1, 1, 1)
        
        # Четвертая строка: Дополнительные опции
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
        self.groupBox_control.setMaximumHeight(80)  # Ограничиваем высоту
        self.horizontalLayout_control = QHBoxLayout(self.groupBox_control)
        self.horizontalLayout_control.setObjectName(u"horizontalLayout_control")
        self.horizontalLayout_control.setContentsMargins(15, 10, 15, 10)
        self.horizontalLayout_control.setSpacing(10)
        
        # Главная кнопка запуска
        self.pushButton_run = QPushButton(self.groupBox_control)
        self.pushButton_run.setObjectName(u"pushButton_run")
        self.pushButton_run.setText("🚀 Запустить планирование")
        self.pushButton_run.setMinimumHeight(40)
        self.pushButton_run.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.horizontalLayout_control.addWidget(self.pushButton_run)
        
        # Режим визуализации
        self.label_viz_mode = QLabel(self.groupBox_control)
        self.label_viz_mode.setObjectName(u"label_viz_mode")
        self.label_viz_mode.setText("Режим визуализации:")
        self.horizontalLayout_control.addWidget(self.label_viz_mode)

        self.comboBox_viz_mode = QComboBox(self.groupBox_control)
        self.comboBox_viz_mode.setObjectName(u"comboBox_viz_mode")
        self.comboBox_viz_mode.addItems([
            "Анимация (реальный режим)",
            "Статическая 3D"
        ])
        self.horizontalLayout_control.addWidget(self.comboBox_viz_mode)

        # Флаг 3D (рука/модель)
        self.checkBox_arm_mesh = QCheckBox(self.groupBox_control)
        self.checkBox_arm_mesh.setObjectName(u"checkBox_arm_mesh")
        self.checkBox_arm_mesh.setText("3D рука/модель")
        self.horizontalLayout_control.addWidget(self.checkBox_arm_mesh)

        # Упрощение: отдельный флаг для реальной модели скрыт, используем общий чекбокс
        self.checkBox_robot_model = QCheckBox(self.groupBox_control)
        self.checkBox_robot_model.setObjectName(u"checkBox_robot_model")
        self.checkBox_robot_model.setVisible(False)

        self.label_robot_model = QLabel(self.groupBox_control)
        self.label_robot_model.setObjectName(u"label_robot_model")
        self.label_robot_model.setText("Модель:")
        self.horizontalLayout_control.addWidget(self.label_robot_model)

        self.comboBox_robot_model = QComboBox(self.groupBox_control)
        self.comboBox_robot_model.setObjectName(u"comboBox_robot_model")
        self.comboBox_robot_model.addItems([
            "KUKA KR QUANTEC",
            "KUKA KR 360 FORTEC",
            "KUKA KR 300"
        ])
        self.horizontalLayout_control.addWidget(self.comboBox_robot_model)

        # Кнопка визуализации
        self.pushButton_viz = QPushButton(self.groupBox_control)
        self.pushButton_viz.setObjectName(u"pushButton_viz")
        self.pushButton_viz.setText("📊 Открыть визуализацию")
        self.pushButton_viz.setMinimumHeight(35)
        self.horizontalLayout_control.addWidget(self.pushButton_viz)
        
        # Кнопка проверки мощности системы
        self.pushButton_check_perf = QPushButton(self.groupBox_control)
        self.pushButton_check_perf.setObjectName(u"pushButton_check_perf")
        self.pushButton_check_perf.setText("⚙️ Проверка мощности")
        self.pushButton_check_perf.setMinimumHeight(35)
        self.pushButton_check_perf.setToolTip("Оценить производительность системы и рекомендовать модель руки")
        self.pushButton_check_perf.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border-radius: 6px;
                padding: 8px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #125A9C;
            }
        """)
        self.horizontalLayout_control.addWidget(self.pushButton_check_perf)

        # Кнопка запуска десктопного приложения
        self.pushButton_desktop_app = QPushButton(self.groupBox_control)
        self.pushButton_desktop_app.setObjectName(u"pushButton_desktop_app")
        self.pushButton_desktop_app.setText("🖥️ Native 3D")
        self.pushButton_desktop_app.setMinimumHeight(35)
        self.pushButton_desktop_app.setToolTip("Открыть нативную 3D визуализацию с OpenGL")
        self.pushButton_desktop_app.setStyleSheet("""
            QPushButton {
                background-color: #FF6B35;
                color: white;
                border-radius: 6px;
                padding: 8px 14px;
                font-weight: 600;
                border: 2px solid #E55A2B;
            }
            QPushButton:hover {
                background-color: #E55A2B;
                border-color: #D14A1B;
            }
            QPushButton:pressed {
                background-color: #D14A1B;
            }
        """)
        self.horizontalLayout_control.addWidget(self.pushButton_desktop_app)

        # Отступ
        self.horizontalSpacer_control = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_control.addItem(self.horizontalSpacer_control)
        
        # Кнопка очистки
        self.pushButton_clear_logs = QPushButton(self.groupBox_control)
        self.pushButton_clear_logs.setObjectName(u"pushButton_clear_logs")
        self.pushButton_clear_logs.setText("🗑️ Очистить")
        self.pushButton_clear_logs.setMinimumHeight(35)
        self.pushButton_clear_logs.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.horizontalLayout_control.addWidget(self.pushButton_clear_logs)
        
        self.verticalLayout_main.addWidget(self.groupBox_control)
        
        # Группа логов - растягивается на оставшееся место
        self.groupBox_logs = QGroupBox(self.centralwidget)
        self.groupBox_logs.setObjectName(u"groupBox_logs")
        self.groupBox_logs.setTitle("📋 Логи и результаты")
        self.groupBox_logs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.verticalLayout_logs = QVBoxLayout(self.groupBox_logs)
        self.verticalLayout_logs.setObjectName(u"verticalLayout_logs")
        self.verticalLayout_logs.setContentsMargins(15, 15, 15, 15)
        
        self.textLog = QTextEdit(self.groupBox_logs)
        self.textLog.setObjectName(u"textLog")
        self.textLog.setReadOnly(True)
        self.textLog.setPlaceholderText("Логи работы программы будут отображаться здесь...")
        self.textLog.setMinimumHeight(300)  # Минимальная высота
        self.verticalLayout_logs.addWidget(self.textLog)

        # Нижняя панель с прогресс-баром (фиолетовый)
        self.progressBar_bottom = QProgressBar(self.groupBox_logs)
        self.progressBar_bottom.setObjectName(u"progressBar_bottom")
        self.progressBar_bottom.setMinimumHeight(18)
        self.progressBar_bottom.setRange(0, 100)
        self.progressBar_bottom.setValue(0)
        self.progressBar_bottom.setTextVisible(False)
        self.progressBar_bottom.setStyleSheet("""
            QProgressBar {
                background-color: #EDE7F6; /* светло-фиолетовый фон */
                border: 1px solid #C7A4FF; /* нежный бордер */
                border-radius: 6px;
                padding: 1px;
            }
            QProgressBar::chunk {
                background-color: #6A0DAD; /* фиолетовое заполнение */
                width: 8px;
                margin: 0.5px;
                border-radius: 6px;
            }
        """)
        self.verticalLayout_logs.addWidget(self.progressBar_bottom)

        # Подпись под прогресс-баром с процентами
        self.labelProgress_bottom = QLabel(self.groupBox_logs)
        self.labelProgress_bottom.setObjectName(u"labelProgress_bottom")
        self.labelProgress_bottom.setText("Загрузка визуализации: 0%")
        self.labelProgress_bottom.setStyleSheet("color: #6A0DAD; font-weight: 600;")
        self.verticalLayout_logs.addWidget(self.labelProgress_bottom)
        
        self.verticalLayout_main.addWidget(self.groupBox_logs)
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        # Меню
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1200, 22))
        
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

        # Индикатор прогресса в статус-баре (нижняя полоса загрузки)
        self.progressBar_status = QProgressBar()
        self.progressBar_status.setObjectName(u"progressBar_status")
        # Фиксированная ширина как в первоначальном виде
        self.progressBar_status.setMaximumWidth(240)
        self.progressBar_status.setTextVisible(False)
        self.progressBar_status.setRange(0, 100)
        self.progressBar_status.setValue(0)
        self.statusbar.addPermanentWidget(self.progressBar_status)
        
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

    def get_visualization_mode(self):
        text = self.comboBox_viz_mode.currentText()
        if text.startswith("Анимация"):
            return "3d_anim"
        return "3d"

    def get_arm_mesh_enabled(self):
        return self.checkBox_arm_mesh.isChecked()

    def get_robot_model_enabled(self):
        # Единый переключатель: включает и меш-руку, и реальную модель
        return self.checkBox_arm_mesh.isChecked()

    def get_robot_model_selection(self):
        return self.comboBox_robot_model.currentText()