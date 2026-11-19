"""Paleta única de ocho colores para toda la aplicación."""
PALETTE = {
    "primary": "#356B72",
    "secondary": "#8CA7A2",
    "accent": "#D99A72",
    "background": "#F3F4F1",
    "surface": "#FFFFFF",
    "surface_alt": "#E7ECE9",
    "text": "#273B43",
    "muted": "#788A87",
}
def stylesheet():
    c=PALETTE
    return f"""
    QWidget {{ font-family:'Segoe UI'; font-size:10pt; background:{c['background']}; color:{c['text']}; }}
    QMainWindow,QDialog {{ background:{c['background']}; }}
    QFrame#Panel,QGroupBox {{ background:{c['surface']}; border:1px solid {c['surface_alt']}; border-radius:10px; }}
    QGroupBox {{ margin-top:12px; padding:12px 8px 8px 8px; font-weight:600; }}
    QGroupBox::title {{ subcontrol-origin:margin; left:12px; padding:0 5px; color:{c['primary']}; }}
    QPushButton {{ background:{c['surface_alt']}; color:{c['text']}; border:1px solid {c['secondary']}; border-radius:7px; padding:7px 10px; }}
    QPushButton:hover {{ background:{c['secondary']}; color:{c['text']}; }}
    QPushButton:pressed {{ background:{c['primary']}; color:{c['surface']}; }}
    QPushButton:disabled {{ background:{c['surface_alt']}; color:{c['muted']}; border-color:{c['surface_alt']}; }}
    QPushButton#Primary {{ background:{c['primary']}; color:{c['surface']}; border:0; font-weight:600; }}
    QPushButton#Primary:hover {{ background:{c['text']}; }}
    QLineEdit,QTextEdit,QComboBox,QSpinBox {{ background:{c['surface']}; color:{c['text']}; border:1px solid {c['secondary']}; border-radius:6px; padding:6px; selection-background-color:{c['primary']}; selection-color:{c['surface']}; }}
    QLineEdit:focus,QTextEdit:focus,QComboBox:focus,QSpinBox:focus {{ border:2px solid {c['primary']}; }}
    QListWidget,QTableWidget,QTreeWidget {{ background:{c['surface']}; color:{c['text']}; border:1px solid {c['surface_alt']}; border-radius:8px; alternate-background-color:{c['background']}; gridline-color:{c['surface_alt']}; }}
    QHeaderView::section {{ background:{c['surface_alt']}; color:{c['text']}; padding:6px; border:0; font-weight:600; }}
    QTabWidget::pane {{ background:{c['surface']}; border:1px solid {c['surface_alt']}; border-radius:8px; top:-1px; }}
    QTabBar::tab {{ background:{c['surface_alt']}; color:{c['muted']}; padding:9px 14px; margin-right:3px; border-top-left-radius:7px; border-top-right-radius:7px; }}
    QTabBar::tab:selected {{ background:{c['primary']}; color:{c['surface']}; }}
    QToolTip {{ background:{c['surface_alt']}; color:{c['text']}; border:1px solid {c['secondary']}; padding:5px; }}
    QSlider::handle:horizontal {{ background:{c['accent']}; border:1px solid {c['primary']}; width:14px; margin:-5px 0; border-radius:7px; }}
    QSlider::handle:vertical {{ background:{c['accent']}; border:1px solid {c['primary']}; height:14px; margin:0 -5px; border-radius:7px; }}
    QScrollBar:vertical {{ background:{c['background']}; width:11px; margin:2px; }}
    QScrollBar::handle:vertical {{ background:{c['secondary']}; min-height:24px; border-radius:5px; }}
    QScrollBar:horizontal {{ background:{c['background']}; height:11px; margin:2px; }}
    QScrollBar::handle:horizontal {{ background:{c['secondary']}; min-width:24px; border-radius:5px; }}
    QScrollBar::add-line,QScrollBar::sub-line {{ width:0; height:0; }}
    """
