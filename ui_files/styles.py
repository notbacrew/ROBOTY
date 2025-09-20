# -*- coding: utf-8 -*-
"""
Стили для приложения ROBOTY
"""

# Цветовая палитра
COLORS = {
    'light': {
        'primary': '#6A0DAD',      # темно-фиолетовый
        'secondary': '#9B30FF',    # ярко-фиолетовый
        'light_accent': '#E6E6FA', # лавандовый
        'background': '#FFFFFF',   # белый
        'surface': '#FAFAFA',      # очень светло-серый
        'text_primary': '#333333', # темно-серый
        'text_secondary': '#666666', # серый
        'text_disabled': '#999999', # светло-серый
        'border': '#E0E0E0',       # светло-серый
        'hover': '#C0C0C0',        # серый
        'success': '#4CAF50',      # зеленый
        'warning': '#FF9800',      # оранжевый
        'error': '#F44336',        # красный
    },
    'dark': {
        'primary': '#9B30FF',      # ярко-фиолетовый (в темной теме более яркий)
        'secondary': '#6A0DAD',    # темно-фиолетовый
        'light_accent': '#2A2A2A', # темно-серый
        'background': '#1E1E1E',   # очень темный
        'surface': '#2D2D2D',      # темный
        'text_primary': '#FFFFFF', # белый
        'text_secondary': '#CCCCCC', # светло-серый
        'text_disabled': '#888888', # серый
        'border': '#404040',       # темно-серый
        'hover': '#505050',        # серый
        'success': '#66BB6A',      # светло-зеленый
        'warning': '#FFB74D',      # светло-оранжевый
        'error': '#EF5350',        # светло-красный
    }
}

# Общие стили
COMMON_STYLES = """
    QWidget {{
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: 14px;
    }}
    
    QMainWindow {
        background-color: {background};
        color: {text_primary};
    }
    
    /* Анимации */
    QPushButton, QComboBox, QSpinBox, QCheckBox, QGroupBox {
        transition: all 0.3s ease-in-out;
    }
    
    /* Скроллбары */
    QScrollBar:vertical {
        background: {surface};
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background: {border};
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: {hover};
    }
    
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0px;
    }
"""

# Стили для светлой темы
LIGHT_STYLES = COMMON_STYLES.format(**COLORS['light']) + """
    /* Группы */
    QGroupBox {
        font-weight: 600;
        font-size: 16px;
        color: {text_primary};
        background-color: {surface};
        border: 2px solid {border};
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 8px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 8px 0 8px;
        background-color: {background};
        color: {primary};
    }
    
    /* Кнопки */
    QPushButton {
        background-color: {primary};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: 600;
        min-height: 20px;
    }
    
    QPushButton:hover {
        background-color: {secondary};
        transform: translateY(-1px);
    }
    
    QPushButton:pressed {
        background-color: {primary};
        transform: translateY(0px);
    }
    
    QPushButton:disabled {
        background-color: {border};
        color: {text_disabled};
    }
    
    /* Вторичные кнопки */
    QPushButton[class="secondary"] {
        background-color: {border};
        color: {text_primary};
    }
    
    QPushButton[class="secondary"]:hover {
        background-color: {hover};
    }
    
    /* Выпадающие списки */
    QComboBox {
        background-color: {background};
        color: {text_primary};
        border: 2px solid {border};
        border-radius: 8px;
        padding: 8px 12px;
        min-height: 20px;
        font-size: 14px;
    }
    
    QComboBox:hover {
        border-color: {primary};
    }
    
    QComboBox:focus {
        border-color: {primary};
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid {text_secondary};
        margin-right: 5px;
    }
    
    QComboBox QAbstractItemView {
        background-color: {background};
        color: {text_primary};
        border: 2px solid {border};
        border-radius: 8px;
        selection-background-color: {light_accent};
        outline: none;
    }
    
    /* Спинбоксы */
    QSpinBox {
        background-color: {background};
        color: {text_primary};
        border: 2px solid {border};
        border-radius: 8px;
        padding: 8px 12px;
        min-height: 20px;
        font-size: 14px;
    }
    
    QSpinBox:hover {
        border-color: {primary};
    }
    
    QSpinBox:focus {
        border-color: {primary};
    }
    
    QSpinBox::up-button, QSpinBox::down-button {
        background-color: {surface};
        border: none;
        border-radius: 4px;
        width: 20px;
    }
    
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {
        background-color: {hover};
    }
    
    QSpinBox::up-arrow, QSpinBox::down-arrow {
        width: 0;
        height: 0;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
    }
    
    QSpinBox::up-arrow {
        border-bottom: 4px solid {text_secondary};
    }
    
    QSpinBox::down-arrow {
        border-top: 4px solid {text_secondary};
    }
    
    /* Чекбоксы */
    QCheckBox {
        color: {text_primary};
        font-size: 14px;
        spacing: 8px;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 2px solid {border};
        border-radius: 4px;
        background-color: {background};
    }
    
    QCheckBox::indicator:hover {
        border-color: {primary};
    }
    
    QCheckBox::indicator:checked {
        background-color: {primary};
        border-color: {primary};
        image: none;
    }
    
    QCheckBox::indicator:checked::after {
        content: "✓";
        color: white;
        font-weight: bold;
    }
    
    /* Текстовые поля */
    QTextEdit {
        background-color: {background};
        color: {text_primary};
        border: 2px solid {border};
        border-radius: 8px;
        padding: 8px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 13px;
    }
    
    QTextEdit:focus {
        border-color: {primary};
    }
    
    QTextEdit::placeholder {
        color: {text_disabled};
    }
    
    /* Метки */
    QLabel {
        color: {text_primary};
        font-size: 14px;
    }
    
    /* Меню */
    QMenuBar {
        background-color: {surface};
        color: {text_primary};
        border-bottom: 1px solid {border};
        spacing: 3px;
    }
    
    QMenuBar::item {
        background: transparent;
        padding: 8px 12px;
        border-radius: 4px;
    }
    
    QMenuBar::item:selected {
        background-color: {light_accent};
    }
    
    QMenuBar::item:pressed {
        background-color: {primary};
        color: white;
    }
    
    QMenu {
        background-color: {background};
        color: {text_primary};
        border: 1px solid {border};
        border-radius: 8px;
    }
    
    QMenu::item {
        padding: 8px 16px;
        border-radius: 4px;
    }
    
    QMenu::item:selected {
        background-color: {light_accent};
    }
    
    QMenu::separator {
        height: 1px;
        background-color: {border};
        margin: 4px 8px;
    }
    
    /* Статус бар */
    QStatusBar {
        background-color: {surface};
        color: {text_secondary};
        border-top: 1px solid {border};
    }
    
    /* Разделители */
    QFrame[frameShape="4"] {
        color: {border};
    }
""".format(**COLORS['light'])

# Стили для темной темы
DARK_STYLES = COMMON_STYLES.format(**COLORS['dark']) + """
    /* Группы */
    QGroupBox {
        font-weight: 600;
        font-size: 16px;
        color: {text_primary};
        background-color: {surface};
        border: 2px solid {border};
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 8px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 8px 0 8px;
        background-color: {background};
        color: {primary};
    }
    
    /* Кнопки */
    QPushButton {
        background-color: {primary};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: 600;
        min-height: 20px;
    }
    
    QPushButton:hover {
        background-color: {secondary};
        transform: translateY(-1px);
    }
    
    QPushButton:pressed {
        background-color: {primary};
        transform: translateY(0px);
    }
    
    QPushButton:disabled {
        background-color: {border};
        color: {text_disabled};
    }
    
    /* Вторичные кнопки */
    QPushButton[class="secondary"] {
        background-color: {border};
        color: {text_primary};
    }
    
    QPushButton[class="secondary"]:hover {
        background-color: {hover};
    }
    
    /* Выпадающие списки */
    QComboBox {
        background-color: {surface};
        color: {text_primary};
        border: 2px solid {border};
        border-radius: 8px;
        padding: 8px 12px;
        min-height: 20px;
        font-size: 14px;
    }
    
    QComboBox:hover {
        border-color: {primary};
    }
    
    QComboBox:focus {
        border-color: {primary};
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid {text_secondary};
        margin-right: 5px;
    }
    
    QComboBox QAbstractItemView {
        background-color: {surface};
        color: {text_primary};
        border: 2px solid {border};
        border-radius: 8px;
        selection-background-color: {light_accent};
        outline: none;
    }
    
    /* Спинбоксы */
    QSpinBox {
        background-color: {surface};
        color: {text_primary};
        border: 2px solid {border};
        border-radius: 8px;
        padding: 8px 12px;
        min-height: 20px;
        font-size: 14px;
    }
    
    QSpinBox:hover {
        border-color: {primary};
    }
    
    QSpinBox:focus {
        border-color: {primary};
    }
    
    QSpinBox::up-button, QSpinBox::down-button {
        background-color: {border};
        border: none;
        border-radius: 4px;
        width: 20px;
    }
    
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {
        background-color: {hover};
    }
    
    QSpinBox::up-arrow, QSpinBox::down-arrow {
        width: 0;
        height: 0;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
    }
    
    QSpinBox::up-arrow {
        border-bottom: 4px solid {text_secondary};
    }
    
    QSpinBox::down-arrow {
        border-top: 4px solid {text_secondary};
    }
    
    /* Чекбоксы */
    QCheckBox {
        color: {text_primary};
        font-size: 14px;
        spacing: 8px;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 2px solid {border};
        border-radius: 4px;
        background-color: {surface};
    }
    
    QCheckBox::indicator:hover {
        border-color: {primary};
    }
    
    QCheckBox::indicator:checked {
        background-color: {primary};
        border-color: {primary};
        image: none;
    }
    
    QCheckBox::indicator:checked::after {
        content: "✓";
        color: white;
        font-weight: bold;
    }
    
    /* Текстовые поля */
    QTextEdit {
        background-color: {surface};
        color: {text_primary};
        border: 2px solid {border};
        border-radius: 8px;
        padding: 8px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 13px;
    }
    
    QTextEdit:focus {
        border-color: {primary};
    }
    
    QTextEdit::placeholder {
        color: {text_disabled};
    }
    
    /* Метки */
    QLabel {
        color: {text_primary};
        font-size: 14px;
    }
    
    /* Меню */
    QMenuBar {
        background-color: {surface};
        color: {text_primary};
        border-bottom: 1px solid {border};
        spacing: 3px;
    }
    
    QMenuBar::item {
        background: transparent;
        padding: 8px 12px;
        border-radius: 4px;
    }
    
    QMenuBar::item:selected {
        background-color: {light_accent};
    }
    
    QMenuBar::item:pressed {
        background-color: {primary};
        color: white;
    }
    
    QMenu {
        background-color: {surface};
        color: {text_primary};
        border: 1px solid {border};
        border-radius: 8px;
    }
    
    QMenu::item {
        padding: 8px 16px;
        border-radius: 4px;
    }
    
    QMenu::item:selected {
        background-color: {light_accent};
    }
    
    QMenu::separator {
        height: 1px;
        background-color: {border};
        margin: 4px 8px;
    }
    
    /* Статус бар */
    QStatusBar {
        background-color: {surface};
        color: {text_secondary};
        border-top: 1px solid {border};
    }
    
    /* Разделители */
    QFrame[frameShape="4"] {
        color: {border};
    }
""".format(**COLORS['dark'])

def get_light_style():
    """Возвращает стили для светлой темы"""
    return LIGHT_STYLES

def get_dark_style():
    """Возвращает стили для темной темы"""
    return DARK_STYLES

def get_colors(theme='light'):
    """Возвращает цвета для указанной темы"""
    return COLORS.get(theme, COLORS['light'])
