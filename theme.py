"""Light / dark palettes and the application stylesheet."""

LIGHT = {
    "bg": "#f4f6f8", "card": "#ffffff", "text": "#1f2933", "muted": "#7b8794",
    "border": "#e1e5ea", "hover": "#eef1f4", "tile": "#f4f6f8",
    "accent": "#10b981", "accent_hover": "#0d9668", "accent_text": "#0d9668",
    "accent_soft": "#d1fae5", "error": "#dc2626", "warn": "#b45309",
    "protein": "#3b82f6", "carbs": "#f59e0b", "fat": "#ef4444",
}

DARK = {
    "bg": "#0f1419", "card": "#1a2129", "text": "#e6edf3", "muted": "#8b98a5",
    "border": "#2a343e", "hover": "#232d37", "tile": "#232d37",
    "accent": "#10b981", "accent_hover": "#34d399", "accent_text": "#34d399",
    "accent_soft": "#12372e", "error": "#f87171", "warn": "#fbbf24",
    "protein": "#60a5fa", "carbs": "#fbbf24", "fat": "#f87171",
}

# Live palette; widgets that custom-paint read from here.
c = dict(LIGHT)
name = "light"


def set_theme(theme_name):
    global name
    name = theme_name
    c.clear()
    c.update(DARK if theme_name == "dark" else LIGHT)


def stylesheet():
    return f"""
QWidget {{
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 14px;
    color: {c['text']};
}}
QWidget#root, QWidget#page {{ background: {c['bg']}; }}

QFrame#sidebar {{
    background: {c['card']};
    border: none;
    border-right: 1px solid {c['border']};
}}
QFrame#sidebar QLabel {{ background: transparent; }}
QLabel#brand {{ font-size: 17px; font-weight: 700; }}
QPushButton#nav {{
    background: transparent; color: {c['muted']}; border: none;
    border-radius: 8px; padding: 10px 14px; text-align: left; font-weight: 600;
}}
QPushButton#nav:hover {{ background: {c['hover']}; color: {c['text']}; }}
QPushButton#nav:checked {{ background: {c['accent_soft']}; color: {c['accent_text']}; }}

QFrame#card {{
    background: {c['card']};
    border: 1px solid {c['border']};
    border-radius: 14px;
}}
QFrame#card QLabel {{ background: transparent; border: none; }}

QLabel#title {{ font-size: 24px; font-weight: 700; }}
QLabel#subtitle {{ color: {c['muted']}; }}
QLabel#sectionTitle {{ font-size: 15px; font-weight: 600; }}
QLabel#fieldLabel {{ color: {c['muted']}; font-size: 12px; font-weight: 600; }}
QLabel#error {{ color: {c['error']}; font-size: 13px; }}
QLabel#warning {{ color: {c['warn']}; font-size: 13px; }}
QLabel#placeholder {{ color: {c['muted']}; font-size: 14px; }}
QLabel#disclaimer {{ color: {c['muted']}; font-size: 11px; }}

QLineEdit, QComboBox {{
    background: {c['card']};
    border: 1px solid {c['border']};
    border-radius: 8px;
    padding: 8px 10px;
    min-height: 20px;
    selection-background-color: {c['accent']};
}}
QLineEdit:hover, QComboBox:hover {{ border-color: {c['muted']}; }}
QLineEdit:focus, QComboBox:focus {{ border: 1px solid {c['accent']}; }}
QComboBox::drop-down {{ border: none; width: 26px; }}
QComboBox QAbstractItemView {{
    background: {c['card']};
    border: 1px solid {c['border']};
    selection-background-color: {c['accent_soft']};
    selection-color: {c['text']};
    outline: none;
}}
QToolTip {{
    background: {c['card']}; color: {c['text']}; border: 1px solid {c['border']};
}}

QPushButton {{
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 600;
}}
QPushButton#primary {{ background: {c['accent']}; color: white; border: none; }}
QPushButton#primary:hover {{ background: {c['accent_hover']}; }}
QPushButton#secondary {{
    background: transparent; color: {c['muted']}; border: 1px solid {c['border']};
}}
QPushButton#secondary:hover {{ background: {c['hover']}; color: {c['text']}; }}

QPushButton#segment {{
    background: transparent; color: {c['muted']}; border: none; padding: 7px 14px;
}}
QPushButton#segment:checked {{ background: {c['card']}; color: {c['text']}; }}
QFrame#segmentBar {{ background: {c['border']}; border-radius: 10px; }}

QFrame#tile {{ background: {c['tile']}; border: none; border-radius: 12px; }}
QFrame#tile QLabel {{ background: transparent; }}
QLabel#tileValue {{ font-size: 26px; font-weight: 700; }}
QLabel#tileUnit {{ color: {c['muted']}; font-size: 12px; }}
QLabel#tileName {{ color: {c['muted']}; font-size: 12px; font-weight: 600; }}
QLabel#tileName[tone="protein"] {{ color: {c['protein']}; }}
QLabel#tileName[tone="carbs"] {{ color: {c['carbs']}; }}
QLabel#tileName[tone="fat"] {{ color: {c['fat']}; }}
QLabel#tileName[tone="accent"] {{ color: {c['accent_text']}; }}
"""
