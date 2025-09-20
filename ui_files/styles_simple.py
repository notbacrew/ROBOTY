# -*- coding: utf-8 -*-
"""
Упрощенные стили для приложения ROBOTY
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
        transition: background-color 0.3s ease, color 0.3s ease;
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
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(106, 13, 173, 0.3);
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS['light']['primary']};
        transform: translateY(0px);
        box-shadow: 0 2px 6px rgba(106, 13, 173, 0.2);
    }}
    
    QPushButton[class="secondary"] {{
        background-color: {COLORS['light']['border']};
        color: {COLORS['light']['text_primary']};
    }}
    
    QPushButton[class="secondary"]:hover {{
        background-color: {COLORS['light']['hover']};
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(192, 192, 192, 0.3);
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
        transform: scale(1.05);
    }}
    
    QComboBox {{
        background-color: {COLORS['light']['background']};
        color: {COLORS['light']['text_primary']};
        border: 2px solid {COLORS['light']['border']};
        border-radius: 8px;
        padding: 8px 12px;
        min-height: 20px;
        font-size: 14px;
        transition: all 0.3s ease;
    }}
    
    QComboBox:hover {{
        border-color: {COLORS['light']['primary']};
        box-shadow: 0 0 8px rgba(106, 13, 173, 0.2);
        transform: translateY(-1px);
    }}
    
    QComboBox:focus {{
        border-color: {COLORS['light']['primary']};
        box-shadow: 0 0 12px rgba(106, 13, 173, 0.3);
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {COLORS['light']['background']};
        color: {COLORS['light']['text_primary']};
        border: 2px solid {COLORS['light']['border']};
        border-radius: 8px;
        selection-background-color: {COLORS['light']['light_accent']};
    }}
    
    QSpinBox {{
        background-color: {COLORS['light']['background']};
        color: {COLORS['light']['text_primary']};
        border: 2px solid {COLORS['light']['border']};
        border-radius: 8px;
        padding: 8px 12px;
        min-height: 20px;
        font-size: 14px;
        transition: all 0.3s ease;
    }}
    
    QSpinBox:hover {{
        border-color: {COLORS['light']['primary']};
        box-shadow: 0 0 8px rgba(106, 13, 173, 0.2);
        transform: translateY(-1px);
    }}
    
    QSpinBox:focus {{
        border-color: {COLORS['light']['primary']};
        box-shadow: 0 0 12px rgba(106, 13, 173, 0.3);
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
    """

def get_dark_style():
    """Возвращает стили для темной темы"""
    return f"""
    QMainWindow {{
        background-color: {COLORS['dark']['background']};
        color: {COLORS['dark']['text_primary']};
        transition: background-color 0.3s ease, color 0.3s ease;
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
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(155, 48, 255, 0.3);
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS['dark']['primary']};
        transform: translateY(0px);
        box-shadow: 0 2px 6px rgba(155, 48, 255, 0.2);
    }}
    
    QPushButton[class="secondary"] {{
        background-color: {COLORS['dark']['border']};
        color: {COLORS['dark']['text_primary']};
    }}
    
    QPushButton[class="secondary"]:hover {{
        background-color: {COLORS['dark']['hover']};
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(80, 80, 80, 0.3);
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
        transform: scale(1.05);
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
    
    QSpinBox {{
        background-color: {COLORS['dark']['surface']};
        color: {COLORS['dark']['text_primary']};
        border: 2px solid {COLORS['dark']['border']};
        border-radius: 8px;
        padding: 8px 12px;
        min-height: 20px;
        font-size: 14px;
    }}
    
    QSpinBox:hover {{
        border-color: {COLORS['dark']['primary']};
    }}
    
    QSpinBox:focus {{
        border-color: {COLORS['dark']['primary']};
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
    """

def get_colors(theme='light'):
    """Возвращает цвета для указанной темы"""
    return COLORS.get(theme, COLORS['light'])
