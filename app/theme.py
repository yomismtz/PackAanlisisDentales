"""Paleta de interfaz y paletas cromáticas disponibles en los informes AVIS."""
from pathlib import Path
import sys

REPORT_PALETTES = {
    "buho_real": {"name": "Búho real", "bird_file": "buho_real.png", "colors": {"plum": "#49372D", "primary": "#795A42", "accent": "#D58B31", "mint": "#E9DDC8", "background": "#F8F4EB", "surface": "#FFFFFF", "soft": "#ECE2D2", "border": "#CFB999", "text": "#302923", "muted": "#75695C"}},
    "colibri": {"name": "Colibrí", "bird_file": "colibri.png", "colors": {"plum": "#263C50", "primary": "#087F75", "accent": "#C34C8A", "mint": "#D9F0E8", "background": "#F4F9F7", "surface": "#FFFFFF", "soft": "#E3F1EC", "border": "#BFDCD4", "text": "#263C50", "muted": "#536A66"}},
    "guacamayo_azul": {"name": "Guacamayo azul", "bird_file": "guacamayo_azul.png", "colors": {"plum": "#173B63", "primary": "#1769AA", "accent": "#D49B18", "mint": "#D8EEE5", "background": "#F4F8FB", "surface": "#FFFFFF", "soft": "#E4EFF6", "border": "#BDD1E0", "text": "#173B63", "muted": "#60778B"}},
    "guacamaya_roja": {"name": "Guacamaya roja", "bird_file": "guacamaya_roja.png", "colors": {"plum": "#38262C", "primary": "#D9272E", "accent": "#D9A51E", "mint": "#F4E4D6", "background": "#FBF5EF", "surface": "#FFFFFF", "soft": "#F3E4D7", "border": "#DCC5B4", "text": "#38262C", "muted": "#77665F"}},
    "quetzal": {"name": "Quetzal", "bird_file": "quetzal.png", "colors": {"plum": "#183D35", "primary": "#087E70", "accent": "#C8463F", "mint": "#D8EEE5", "background": "#F5F9F4", "surface": "#FFFFFF", "soft": "#E4F1E7", "border": "#C8B26D", "text": "#183D35", "muted": "#60766E"}},
    "faisan": {"name": "Faisán", "bird_file": "faisan.png", "colors": {"plum": "#49352D", "primary": "#A45136", "accent": "#C18B2B", "mint": "#E9DDC9", "background": "#FAF6EF", "surface": "#FFFFFF", "soft": "#F0E6D6", "border": "#D8C3A7", "text": "#49352D", "muted": "#74675E"}},
    "ninfa": {"name": "Ninfa", "bird_file": "ninfa.png", "colors": {"plum": "#3B4146", "primary": "#737B81", "accent": "#D87542", "mint": "#EEECE3", "background": "#FAF9F3", "surface": "#FFFFFF", "soft": "#EEECE3", "border": "#D2D0C6", "text": "#30363B", "muted": "#74777B"}},
    "pavo_real": {"name": "Pavo real", "bird_file": "pavo_real.png", "colors": {"plum": "#23304F", "primary": "#087E80", "accent": "#A58A36", "mint": "#D9EEE7", "background": "#F4F8F8", "surface": "#FFFFFF", "soft": "#E3F0ED", "border": "#BBD5CF", "text": "#23304F", "muted": "#61747D"}},
    "tucan": {"name": "Tucán", "bird_file": "tucan.png", "colors": {"plum": "#202124", "primary": "#323D43", "accent": "#E97824", "mint": "#F5E8C8", "background": "#FBF8F0", "surface": "#FFFFFF", "soft": "#F5F1E8", "border": "#CEC7B7", "text": "#202124", "muted": "#686A6B"}},
    "agapornis": {"name": "Agapornis", "bird_file": "agapornis.png", "colors": {"plum": "#553B59", "primary": "#328C55", "accent": "#D98567", "mint": "#D9EEE6", "background": "#FFFCF4", "surface": "#FFFFFF", "soft": "#EFE7F2", "border": "#D7C9D9", "text": "#3F3643", "muted": "#5F6F69"}},
}


def report_bird_path(palette_id="colibri"):
    palette = REPORT_PALETTES.get(palette_id, REPORT_PALETTES["colibri"])
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return root / "clients" / "web" / "public" / "birds" / palette["bird_file"]


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
