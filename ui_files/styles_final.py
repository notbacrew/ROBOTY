# -*- coding: utf-8 -*-
"""
Финальные стили для приложения ROBOTY с плавными переходами
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

def get_light_style():
    """Возвращает стили для светлой темы"""
    return f"""
    QMainWindow {{
        background-color: {COLORS['light']['background']};
        color: {COLORS['light']['text_primary']};
    }}
    
    QGroupBox {{
        font-weight: 600;
        font-size: 16px;
        color: {COLORS['light']['text_primary']};
        background-color: {COLORS['light']['surface']};
        border: 2px solid {COLORS['light']['border']};
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 8px;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 8px 0 8px;
        background-color: {COLORS['light']['background']};
        color: {COLORS['light']['primary']};
    }}
    
    QPushButton {{
        background-color: {COLORS['light']['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: 600;
        min-height: 20px;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['light']['secondary']};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS['light']['primary']};
    }}
    
    QPushButton[class="secondary"] {{
        background-color: {COLORS['light']['border']};
        color: {COLORS['light']['text_primary']};
    }}
    
    QPushButton[class="secondary"]:hover {{
        background-color: {COLORS['light']['hover']};
    }}
    
    QPushButton[class="theme-toggle"] {{
        background-color: transparent;
        border: 2px solid {COLORS['light']['border']};
        border-radius: 20px;
        padding: 8px;
        min-width: 40px;
        max-width: 40px;
        min-height: 40px;
        max-height: 40px;
        font-size: 18px;
    }}
    
    QPushButton[class="theme-toggle"]:hover {{
        background-color: {COLORS['light']['light_accent']};
        border-color: {COLORS['light']['primary']};
    }}
    
    QComboBox {{
        background-color: {COLORS['light']['background']};
        color: {COLORS['light']['text_primary']};
        border: 2px solid {COLORS['light']['border']};
        border-radius: 8px;
        padding: 8px 12px;
        min-height: 20px;
        font-size: 14px;
    }}
    
    QComboBox:hover {{
        border-color: {COLORS['light']['primary']};
    }}
    
    QComboBox:focus {{
        border-color: {COLORS['light']['primary']};
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {COLORS['light']['background']};
        color: {COLORS['light']['text_primary']};
        border: 2px solid {COLORS['light']['border']};
        border-radius: 8px;
        selection-background-color: {COLORS['light']['light_accent']};
    }}
    
    /* Улучшенные стили для полей ввода чисел */
    QSpinBox, QDoubleSpinBox {{
        background-color: {COLORS['light']['background']};
        color: {COLORS['light']['text_primary']};
        border: 2px solid {COLORS['light']['border']};
        border-radius: 8px;
        padding: 8px 12px;
        min-height: 20px;
        font-size: 14px;
        font-weight: 500;
        font-family: 'Segoe UI', 'Arial', sans-serif;
    }}
    
    QSpinBox:hover, QDoubleSpinBox:hover {{
        border-color: {COLORS['light']['primary']};
    }}
    
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {COLORS['light']['primary']};
        background-color: {COLORS['light']['light_accent']};
    }}
    
    QSpinBox::up-button, QDoubleSpinBox::up-button {{
        background-color: {COLORS['light']['primary']};
        border: 2px solid {COLORS['light']['primary']};
        border-radius: 4px;
        width: 20px;
        height: 16px;
        margin: 1px;
    }}
    
    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
        background-color: {COLORS['light']['secondary']};
        border-color: {COLORS['light']['secondary']};
    }}
    
    QSpinBox::up-button:pressed, QDoubleSpinBox::up-button:pressed {{
        background-color: {COLORS['light']['primary']};
        border-color: {COLORS['light']['primary']};
    }}
    
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        background-color: {COLORS['light']['primary']};
        border: 2px solid {COLORS['light']['primary']};
        border-radius: 4px;
        width: 20px;
        height: 16px;
        margin: 1px;
    }}
    
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
        background-color: {COLORS['light']['secondary']};
        border-color: {COLORS['light']['secondary']};
    }}
    
    QSpinBox::down-button:pressed, QDoubleSpinBox::down-button:pressed {{
        background-color: {COLORS['light']['primary']};
        border-color: {COLORS['light']['primary']};
    }}
    
    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
        color: white;
        width: 8px;
        height: 8px;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 8px solid white;
        background: none;
        image: none;
    }}
    
    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
        color: white;
        width: 8px;
        height: 8px;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 8px solid white;
        background: none;
        image: none;
    }}
    
    QLineEdit {{
        background-color: {COLORS['light']['background']};
        color: {COLORS['light']['text_primary']};
        border: 2px solid {COLORS['light']['border']};
        border-radius: 8px;
        padding: 8px 12px;
        min-height: 20px;
        font-size: 14px;
        font-weight: 500;
        font-family: 'Segoe UI', 'Arial', sans-serif;
    }}
    
    QLineEdit:hover {{
        border-color: {COLORS['light']['primary']};
    }}
    
    QLineEdit:focus {{
        border-color: {COLORS['light']['primary']};
        background-color: {COLORS['light']['light_accent']};
    }}
    
    QCheckBox {{
        color: {COLORS['light']['text_primary']};
        font-size: 14px;
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {COLORS['light']['border']};
        border-radius: 4px;
        background-color: {COLORS['light']['background']};
    }}
    
    QCheckBox::indicator:hover {{
        border-color: {COLORS['light']['primary']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {COLORS['light']['primary']};
        border-color: {COLORS['light']['primary']};
    }}
    
    QTextEdit {{
        background-color: {COLORS['light']['background']};
        color: {COLORS['light']['text_primary']};
        border: 2px solid {COLORS['light']['border']};
        border-radius: 8px;
        padding: 8px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 13px;
    }}
    
    QTextEdit:focus {{
        border-color: {COLORS['light']['primary']};
    }}
    
    QLabel {{
        color: {COLORS['light']['text_primary']};
        font-size: 14px;
    }}
    
    QMenuBar {{
        background-color: {COLORS['light']['surface']};
        color: {COLORS['light']['text_primary']};
        border-bottom: 1px solid {COLORS['light']['border']};
    }}
    
    QMenuBar::item {{
        background: transparent;
        padding: 8px 12px;
        border-radius: 4px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {COLORS['light']['light_accent']};
    }}
    
    QStatusBar {{
        background-color: {COLORS['light']['surface']};
        color: {COLORS['light']['text_secondary']};
        border-top: 1px solid {COLORS['light']['border']};
    }}
    
    /* Стили для диалогов */
    QDialog {{
        background-color: {COLORS['light']['background']};
        color: {COLORS['light']['text_primary']};
    }}
    
    QScrollArea {{
        background-color: {COLORS['light']['background']};
        border: none;
    }}
    
    QScrollArea QWidget {{
        background-color: {COLORS['light']['background']};
    }}
    
    /* Стили для кнопок диалога */
    QDialog QPushButton {{
        background-color: {COLORS['light']['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: 600;
        min-height: 20px;
    }}
    
    QDialog QPushButton:hover {{
        background-color: {COLORS['light']['secondary']};
    }}
    
    QDialog QPushButton:pressed {{
        background-color: {COLORS['light']['primary']};
    }}
    
    QDialog QPushButton[class="secondary"] {{
        background-color: {COLORS['light']['border']};
        color: {COLORS['light']['text_primary']};
    }}
    
    QDialog QPushButton[class="secondary"]:hover {{
        background-color: {COLORS['light']['hover']};
    }}
    
    /* Дополнительные стили для улучшения видимости кнопок со стрелками */
    QSpinBox::up-button:disabled, QDoubleSpinBox::up-button:disabled {{
        background-color: {COLORS['light']['text_disabled']};
        border-color: {COLORS['light']['text_disabled']};
    }}
    
    QSpinBox::down-button:disabled, QDoubleSpinBox::down-button:disabled {{
        background-color: {COLORS['light']['text_disabled']};
        border-color: {COLORS['light']['text_disabled']};
    }}
    
    QSpinBox::up-arrow:disabled, QDoubleSpinBox::up-arrow:disabled {{
        border-bottom-color: {COLORS['light']['background']};
    }}
    
    QSpinBox::down-arrow:disabled, QDoubleSpinBox::down-arrow:disabled {{
        border-top-color: {COLORS['light']['background']};
    }}
    """

def get_dark_style():
    """Возвращает стили для темной темы"""
    return f"""
    QMainWindow {{
        background-color: {COLORS['dark']['background']};
        color: {COLORS['dark']['text_primary']};
    }}
    
    QGroupBox {{
        font-weight: 600;
        font-size: 16px;
        color: {COLORS['dark']['text_primary']};
        background-color: {COLORS['dark']['surface']};
        border: 2px solid {COLORS['dark']['border']};
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 8px;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 8px 0 8px;
        background-color: {COLORS['dark']['background']};
        color: {COLORS['dark']['primary']};
    }}
    
    QPushButton {{
        background-color: {COLORS['dark']['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: 600;
        min-height: 20px;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['dark']['secondary']};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS['dark']['primary']};
    }}
    
    QPushButton[class="secondary"] {{
        background-color: {COLORS['dark']['border']};
        color: {COLORS['dark']['text_primary']};
    }}
    
    QPushButton[class="secondary"]:hover {{
        background-color: {COLORS['dark']['hover']};
    }}
    
    QPushButton[class="theme-toggle"] {{
        background-color: transparent;
        border: 2px solid {COLORS['dark']['border']};
        border-radius: 20px;
        padding: 8px;
        min-width: 40px;
        max-width: 40px;
        min-height: 40px;
        max-height: 40px;
        font-size: 18px;
    }}
    
    QPushButton[class="theme-toggle"]:hover {{
        background-color: {COLORS['dark']['light_accent']};
        border-color: {COLORS['dark']['primary']};
    }}
    
    QComboBox {{
        background-color: {COLORS['dark']['surface']};
        color: {COLORS['dark']['text_primary']};
        border: 2px solid {COLORS['dark']['border']};
        border-radius: 8px;
        padding: 8px 12px;
        min-height: 20px;
        font-size: 14px;
    }}
    
    QComboBox:hover {{
        border-color: {COLORS['dark']['primary']};
    }}
    
    QComboBox:focus {{
        border-color: {COLORS['dark']['primary']};
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {COLORS['dark']['surface']};
        color: {COLORS['dark']['text_primary']};
        border: 2px solid {COLORS['dark']['border']};
        border-radius: 8px;
        selection-background-color: {COLORS['dark']['light_accent']};
    }}
    
    /* Улучшенные стили для полей ввода чисел */
    QSpinBox, QDoubleSpinBox {{
        background-color: {COLORS['dark']['surface']};
        color: {COLORS['dark']['text_primary']};
        border: 2px solid {COLORS['dark']['border']};
        border-radius: 8px;
        padding: 8px 12px;
        min-height: 20px;
        font-size: 14px;
        font-weight: 500;
        font-family: 'Segoe UI', 'Arial', sans-serif;
    }}
    
    QSpinBox:hover, QDoubleSpinBox:hover {{
        border-color: {COLORS['dark']['primary']};
    }}
    
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {COLORS['dark']['primary']};
        background-color: {COLORS['dark']['light_accent']};
    }}
    
    QSpinBox::up-button, QDoubleSpinBox::up-button {{
        background-color: {COLORS['dark']['primary']};
        border: 2px solid {COLORS['dark']['primary']};
        border-radius: 4px;
        width: 20px;
        height: 16px;
        margin: 1px;
    }}
    
    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
        background-color: {COLORS['dark']['secondary']};
        border-color: {COLORS['dark']['secondary']};
    }}
    
    QSpinBox::up-button:pressed, QDoubleSpinBox::up-button:pressed {{
        background-color: {COLORS['dark']['primary']};
        border-color: {COLORS['dark']['primary']};
    }}
    
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        background-color: {COLORS['dark']['primary']};
        border: 2px solid {COLORS['dark']['primary']};
        border-radius: 4px;
        width: 20px;
        height: 16px;
        margin: 1px;
    }}
    
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
        background-color: {COLORS['dark']['secondary']};
        border-color: {COLORS['dark']['secondary']};
    }}
    
    QSpinBox::down-button:pressed, QDoubleSpinBox::down-button:pressed {{
        background-color: {COLORS['dark']['primary']};
        border-color: {COLORS['dark']['primary']};
    }}
    
    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
        color: white;
        width: 8px;
        height: 8px;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 8px solid white;
        background: none;
        image: none;
    }}
    
    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
        color: white;
        width: 8px;
        height: 8px;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 8px solid white;
        background: none;
        image: none;
    }}
    
    QLineEdit {{
        background-color: {COLORS['dark']['surface']};
        color: {COLORS['dark']['text_primary']};
        border: 2px solid {COLORS['dark']['border']};
        border-radius: 8px;
        padding: 8px 12px;
        min-height: 20px;
        font-size: 14px;
        font-weight: 500;
        font-family: 'Segoe UI', 'Arial', sans-serif;
    }}
    
    QLineEdit:hover {{
        border-color: {COLORS['dark']['primary']};
    }}
    
    QLineEdit:focus {{
        border-color: {COLORS['dark']['primary']};
        background-color: {COLORS['dark']['light_accent']};
    }}
    
    QCheckBox {{
        color: {COLORS['dark']['text_primary']};
        font-size: 14px;
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {COLORS['dark']['border']};
        border-radius: 4px;
        background-color: {COLORS['dark']['surface']};
    }}
    
    QCheckBox::indicator:hover {{
        border-color: {COLORS['dark']['primary']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {COLORS['dark']['primary']};
        border-color: {COLORS['dark']['primary']};
    }}
    
    QTextEdit {{
        background-color: {COLORS['dark']['surface']};
        color: {COLORS['dark']['text_primary']};
        border: 2px solid {COLORS['dark']['border']};
        border-radius: 8px;
        padding: 8px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 13px;
    }}
    
    QTextEdit:focus {{
        border-color: {COLORS['dark']['primary']};
    }}
    
    QLabel {{
        color: {COLORS['dark']['text_primary']};
        font-size: 14px;
    }}
    
    QMenuBar {{
        background-color: {COLORS['dark']['surface']};
        color: {COLORS['dark']['text_primary']};
        border-bottom: 1px solid {COLORS['dark']['border']};
    }}
    
    QMenuBar::item {{
        background: transparent;
        padding: 8px 12px;
        border-radius: 4px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {COLORS['dark']['light_accent']};
    }}
    
    QStatusBar {{
        background-color: {COLORS['dark']['surface']};
        color: {COLORS['dark']['text_secondary']};
        border-top: 1px solid {COLORS['dark']['border']};
    }}
    
    /* Стили для диалогов */
    QDialog {{
        background-color: {COLORS['dark']['background']};
        color: {COLORS['dark']['text_primary']};
    }}
    
    QScrollArea {{
        background-color: {COLORS['dark']['background']};
        border: none;
    }}
    
    QScrollArea QWidget {{
        background-color: {COLORS['dark']['background']};
    }}
    
    /* Стили для кнопок диалога */
    QDialog QPushButton {{
        background-color: {COLORS['dark']['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: 600;
        min-height: 20px;
    }}
    
    QDialog QPushButton:hover {{
        background-color: {COLORS['dark']['secondary']};
    }}
    
    QDialog QPushButton:pressed {{
        background-color: {COLORS['dark']['primary']};
    }}
    
    QDialog QPushButton[class="secondary"] {{
        background-color: {COLORS['dark']['border']};
        color: {COLORS['dark']['text_primary']};
    }}
    
    QDialog QPushButton[class="secondary"]:hover {{
        background-color: {COLORS['dark']['hover']};
    }}
    
    /* Дополнительные стили для улучшения видимости кнопок со стрелками */
    QSpinBox::up-button:disabled, QDoubleSpinBox::up-button:disabled {{
        background-color: {COLORS['dark']['text_disabled']};
        border-color: {COLORS['dark']['text_disabled']};
    }}
    
    QSpinBox::down-button:disabled, QDoubleSpinBox::down-button:disabled {{
        background-color: {COLORS['dark']['text_disabled']};
        border-color: {COLORS['dark']['text_disabled']};
    }}
    
    QSpinBox::up-arrow:disabled, QDoubleSpinBox::up-arrow:disabled {{
        border-bottom-color: {COLORS['dark']['background']};
    }}
    
    QSpinBox::down-arrow:disabled, QDoubleSpinBox::down-arrow:disabled {{
        border-top-color: {COLORS['dark']['background']};
    }}
    """

def get_colors(theme='light'):
    """Возвращает цвета для указанной темы"""
    return COLORS.get(theme, COLORS['light'])