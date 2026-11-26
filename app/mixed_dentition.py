"""Herramienta cualitativa de espacio para Moyers y Tanaka-Johnston."""
import math
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QSplitter, QWidget,
    QLabel, QPushButton, QComboBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialogButtonBox, QTextEdit, QMessageBox, QFileDialog, QCheckBox,
)
from .moyers import MoyersCanvas, predict_moyers_75

# Media ± DE, mm, para modelos de una muestra mexicana de Nayarit.
# Referencias internas aproximadas; no sustituyen medición física individual.
REFERENCE_TEETH = {
    "lower_lateral": {"label": "Incisivo lateral inferior", "mean": 6.1, "sd": 0.5},
    "upper_lateral": {"label": "Incisivo lateral superior", "mean": 7.1, "sd": 0.66},
    "upper_central": {"label": "Incisivo central superior", "mean": 8.8, "sd": 0.61},
}
INCISOR_POINTS = [
    ("42_M", "42 · mesial"), ("42_D", "42 · distal"),
    ("41_M", "41 · mesial"), ("41_D", "41 · distal"),
    ("31_M", "31 · mesial"), ("31_D", "31 · distal"),
    ("32_M", "32 · mesial"), ("32_D", "32 · distal"),
]
ARCH_POINTS = [
    ("ref_M", "Borde mesial del diente de referencia"),
    ("ref_D", "Borde distal del diente de referencia"),
    ("lat_R", "Distal del incisivo lateral derecho · inicio"),
    ("mol_R", "Mesial del primer molar derecho · final"),
    ("lat_L", "Distal del incisivo lateral izquierdo · inicio"),
    ("mol_L", "Mesial del primer molar izquierdo · final"),
]

def tanaka_johnston(incisor_sum, arch):
    if arch == "superior":
        return 11.0 + float(incisor_sum) / 2.0
    if arch == "inferior":
        return 10.5 + float(incisor_sum) / 2.0
    raise ValueError("Arcada no válida.")

def _incisor_sum_range(widths_px):
    if not widths_px or any(k not in widths_px for k in ("42", "41", "31", "32")):
        return None
    ref_px = (widths_px["42"] + widths_px["32"]) / 2.0
    if ref_px <= 0:
        return None
    tooth = REFERENCE_TEETH["lower_lateral"]
    total_px = sum(widths_px.values())
    return (
        total_px * (tooth["mean"] - tooth["sd"]) / ref_px,
        total_px * (tooth["mean"] + tooth["sd"]) / ref_px,
    )

def _available_range(path_px, reference_px, reference_key):
    if path_px is None or reference_px is None or reference_px <= 0:
        return None
    tooth = REFERENCE_TEETH[reference_key]
    return (
        path_px * (tooth["mean"] - tooth["sd"]) / reference_px,
        path_px * (tooth["mean"] + tooth["sd"]) / reference_px,
    )

def _required_range(incisor_range, method, arch, sex):
    if not incisor_range:
        return None
    lo, hi = incisor_range
    try:
        if method == "moyers":
            a = predict_moyers_75(lo, sex, arch)
            b = predict_moyers_75(hi, sex, arch)
        else:
            a, b = tanaka_johnston(lo, arch), tanaka_johnston(hi, arch)
    except ValueError:
        return None
    return min(a, b), max(a, b)

def _qualitative_result(available, required):
    if not available or not required:
        return "Pendiente"
    # Solo afirmamos un resultado si todo el intervalo de incertidumbre coincide.
    low = available[0] - required[1]
    high = available[1] - required[0]
    if low >= 0:
        return "Hay espacio"
    if high < 0:
        return "No hay espacio"
    return "No concluyente"

class MixedDentitionCanvas(MoyersCanvas):
    """Canvas de puntos con regla visual y trazos de recorrido curvo."""
    def draw_points(self, points, reference_pairs=(), paths=None):
        for item in self.marks:
            self.scene_obj.removeItem(item)
        self.marks = []
        if self.pixmap_item is None:
            return
        for first, second in reference_pairs:
            if first in points and second in points:
                a, b = points[first], points[second]
                pen = QPen(QColor("#F4C95D"), 3)
                self.marks.append(self.scene_obj.addLine(a[0], a[1], b[0], b[1], pen))
                dx, dy = b[0]-a[0], b[1]-a[1]
                length = math.hypot(dx, dy)
                if length:
                    nx, ny = -dy/length, dx/length
                    for i in range(11):
                        t = i/10
                        x, y = a[0]+dx*t, a[1]+dy*t
                        half = 7 if i in (0, 5, 10) else 4
                        self.marks.append(self.scene_obj.addLine(
                            x-nx*half, y-ny*half, x+nx*half, y+ny*half, pen
                        ))
        for side, path in (paths or {}).items():
            start, end = ("lat_R", "mol_R") if side == "Derecho" else ("lat_L", "mol_L")
            if start in points and end in points and path:
                coords = [points[start], *path, points[end]]
                pen = QPen(QColor("#22B8B0"), 3)
                for a, b in zip(coords, coords[1:]):
                    self.marks.append(self.scene_obj.addLine(a[0], a[1], b[0], b[1], pen))
                for x, y in path:
                    self.marks.append(self.scene_obj.addEllipse(
                        x-3, y-3, 6, 6, QPen(QColor("#22B8B0"), 1), QColor("#FFFFFF")
                    ))
        for key, (x, y) in points.items():
            dot = self.scene_obj.addEllipse(
                x-5, y-5, 10, 10, QPen(QColor("#22B8B0"), 2), QColor("#FFFFFF")
            )
            label = self.scene_obj.addText(key)
            label.setDefaultTextColor(QColor("#FFFFFF"))
            label.setPos(x+7, y-18)
            self.marks.extend([dot, label])


class MixedDentitionDialog(QDialog):
    def __init__(self, upper_image=None, lower_image=None, existing=None,
                 patient_sex="", periapical_image=None, parent=None, method="moyers"):
        super().__init__(parent)
        self.method = method
        self.method_title = "Moyers · percentil 75 %" if method == "moyers" else "Tanaka-Johnston"
        self.existing = existing or {}
        saved = self.existing.get("values", {})
        self.points = {
            key: {p: tuple(v) for p, v in saved.get(key, {}).items()
                  if isinstance(v, (list, tuple)) and len(v) == 2}
            for key in ("incisors", "upper", "lower")
        }
        self.images = {"incisors": periapical_image, "upper": upper_image, "lower": lower_image}
        self.periapical_image = periapical_image
        self.traces = {
            arch: {side: [tuple(p) for p in saved.get("Recorridos", {}).get(arch, {}).get(side, [])
                          if isinstance(p, (list, tuple)) and len(p) == 2]
                   for side in ("Derecho", "Izquierdo")}
            for arch in ("upper", "lower")
        }
        self.path_capture = None
        self.canvases = {}
        self.point_selects = {}
        self.reference_selects = {}
        self.path_buttons = {}

        self.setWindowTitle("AVIS · " + self.method_title)
        self.resize(1500, 930)
        self.setMinimumSize(1150, 750)
        self.status = QComboBox()
        self.status.addItems(["Pendiente", "En proceso", "Completo"])
        self.status.setCurrentText(self.existing.get("status", "Pendiente"))
        self.sex = QComboBox()
        self.sex.addItems(["Seleccionar", "Femenino", "Masculino"])
        if patient_sex in ("Femenino", "Masculino"):
            self.sex.setCurrentText(patient_sex)
        if saved.get("Sexo") in ("Femenino", "Masculino"):
            self.sex.setCurrentText(saved["Sexo"])
        self.incisors_present = QCheckBox(
            "Los cuatro incisivos inferiores permanentes están erupcionados y visibles"
        )
        self.incisors_present.setChecked(saved.get("Incisivos inferiores erupcionados", False))
        if self.incisors_present.isChecked():
            self.images["incisors"] = lower_image
        self.incisors_present.toggled.connect(self._incisor_source_changed)

        self.tabs = QTabWidget()
        self._build_tab("incisors", "Incisivos inferiores · 42, 41, 31 y 32", INCISOR_POINTS)
        self._build_tab("upper", "Arcada superior · espacio disponible", ARCH_POINTS)
        self._build_tab("lower", "Arcada inferior · espacio disponible", ARCH_POINTS)
        self.tabs.currentChanged.connect(self._tab_changed)

        self.source_status = QLabel()
        self.source_status.setWordWrap(True)
        self.upload = QPushButton("Cargar radiografía periapical…")
        self.upload.clicked.connect(self._load_periapical)
        self.incisors_present.toggled.connect(self.update_results)
        self.results = QTableWidget(4, 2)
        self.results.setHorizontalHeaderLabels(["Arcada / hemiarcada", "Resultado"])
        self.results.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.note = QLabel(
            "Marca un incisivo de referencia para crear una regla interna en cada imagen. "
            "Traza el espacio disponible siguiendo la curva del modelo. No se muestran medidas; "
            "la clasificación es orientativa y debe confirmarse sobre el modelo."
        )
        self.note.setWordWrap(True)
        self.observations = QTextEdit(self.existing.get("observations", ""))
        self.observations.setMaximumHeight(65)
        self.conclusion = QTextEdit(self.existing.get("conclusion", ""))
        self.conclusion.setMaximumHeight(65)

        top = QHBoxLayout()
        form = QFormLayout()
        form.addRow("Estado", self.status)
        if method == "moyers":
            form.addRow("Sexo para la tabla de Moyers", self.sex)
        top.addLayout(form)
        top.addStretch()
        source = QHBoxLayout()
        source.addWidget(self.incisors_present)
        source.addWidget(self.upload)
        left = QVBoxLayout()
        left.addLayout(top)
        left.addLayout(source)
        left.addWidget(self.source_status)
        left.addWidget(self.tabs, 1)
        right = QVBoxLayout()
        right.addWidget(QLabel("Resultado cualitativo por hemiarcada"))
        right.addWidget(self.results, 1)
        right.addWidget(self.note)
        right.addWidget(QLabel("Observaciones"))
        right.addWidget(self.observations)
        right.addWidget(QLabel("Conclusión profesional"))
        right.addWidget(self.conclusion)
        split = QSplitter(Qt.Orientation.Horizontal)
        lw, rw = QWidget(), QWidget()
        lw.setLayout(left)
        rw.setLayout(right)
        split.addWidget(lw)
        split.addWidget(rw)
        split.setStretchFactor(0, 3)
        split.setStretchFactor(1, 2)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "Marca los cuatro incisivos inferiores. En cada arcada marca un diente de referencia "
            "y traza cada espacio con varios clics siguiendo su curvatura."
        ))
        layout.addWidget(split, 1)
        layout.addWidget(buttons)
        self._refresh_sources()
        self.update_results()

    def _build_tab(self, key, title, definitions):
        page = QWidget()
        layout = QVBoxLayout(page)
        canvas = MixedDentitionCanvas()
        canvas.setMinimumSize(540, 430)
        canvas.point_clicked.connect(lambda x, y, k=key: self._click(k, x, y))
        self.canvases[key] = canvas
        self.reference_pairs = getattr(self, "reference_pairs", {})
        self.reference_pairs[key] = [("42_M", "42_D"), ("32_M", "32_D")] if key == "incisors" else [("ref_M", "ref_D")]
        selector = QComboBox()
        selector.addItem("Selecciona el punto que vas a colocar", "")
        for code, label in definitions:
            selector.addItem(f"{code} · {label}", code)
        self.point_selects[key] = selector
        actions = QHBoxLayout()
        place = QPushButton("Colocar / corregir punto")
        place.clicked.connect(lambda checked=False, k=key: self._activate_point(k))
        delete = QPushButton("Eliminar punto")
        delete.clicked.connect(lambda checked=False, k=key: self._delete_point(k))
        actions.addWidget(selector, 2)
        actions.addWidget(place)
        actions.addWidget(delete)
        layout.addLayout(actions)
        if key in ("upper", "lower"):
            refs = ("upper_central", "upper_lateral") if key == "upper" else ("lower_lateral",)
            ref_combo = QComboBox()
            for ref in refs:
                ref_combo.addItem(REFERENCE_TEETH[ref]["label"], ref)
            saved_ref = self.existing.get("values", {}).get("Diente de referencia", {}).get(key)
            if saved_ref:
                i = ref_combo.findData(saved_ref)
                if i >= 0:
                    ref_combo.setCurrentIndex(i)
            ref_combo.currentIndexChanged.connect(self.update_results)
            self.reference_selects[key] = ref_combo
            form = QFormLayout()
            form.addRow("Diente usado como regla interna", ref_combo)
            layout.addLayout(form)
            path_row = QHBoxLayout()
            for side, label in (("Derecho", "Trazar espacio derecho"), ("Izquierdo", "Trazar espacio izquierdo")):
                btn = QPushButton(label)
                btn.clicked.connect(lambda checked=False, k=key, s=side: self._toggle_trace(k, s))
                self.path_buttons[(key, side)] = btn
                path_row.addWidget(btn)
            clear = QPushButton("Borrar recorridos")
            clear.clicked.connect(lambda checked=False, k=key: self._clear_traces(k))
            path_row.addWidget(clear)
            layout.addLayout(path_row)
        layout.addWidget(canvas, 1)
        self.tabs.addTab(page, title)

    def _redraw(self, view):
        self.canvases[view].draw_points(
            self.points[view], self.reference_pairs[view], self.traces.get(view, {})
        )

    def _refresh_sources(self):
        for key in ("incisors", "upper", "lower"):
            self.canvases[key].show_image(self.images.get(key))
            self._redraw(key)
        self.source_status.setText(
            "Radiografía periapical cargada" if self.periapical_image
            else "Vista de incisivos tomada del modelo inferior" if self.images.get("incisors")
            else "Carga el modelo inferior o una radiografía periapical."
        )
        self.upload.setEnabled(not self.incisors_present.isChecked())

    def _incisor_source_changed(self, checked):
        if checked:
            self.periapical_image = None
            self.images["incisors"] = self.images.get("lower")
        else:
            self.images["incisors"] = self.periapical_image
            if not self.periapical_image:
                self.points["incisors"].clear()
        self._refresh_sources()
        self.update_results()

    def _load_periapical(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar radiografía periapical", "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)"
        )
        if not path:
            return
        self.periapical_image = path
        self.incisors_present.blockSignals(True)
        self.incisors_present.setChecked(False)
        self.incisors_present.blockSignals(False)
        self.images["incisors"] = path
        self.points["incisors"].clear()
        self._refresh_sources()
        self.tabs.setCurrentIndex(0)

    def _activate_point(self, view):
        code = self.point_selects[view].currentData()
        if not code:
            QMessageBox.information(self, "Punto", "Selecciona primero el punto anatómico.")
            return
        if self.canvases[view].pixmap_item is None:
            QMessageBox.warning(self, "Imagen requerida", "Carga la imagen correspondiente antes de colocar puntos.")
            return
        if self.path_capture:
            self._finish_trace(*self.path_capture, force=True)
        self.canvases[view].set_point_mode(True)
        self.active_view, self.active_key = view, code
        self.source_status.setText("Haz clic para colocar " + code + ".")

    def _click(self, view, x, y):
        if self.path_capture and self.path_capture[0] == view:
            _, side = self.path_capture
            self.traces[view][side].append((float(x), float(y)))
            self._redraw(view)
            self.update_results()
            return
        if getattr(self, "active_view", None) != view or not getattr(self, "active_key", None):
            return
        self.points[view][self.active_key] = (float(x), float(y))
        self.canvases[view].set_point_mode(False)
        self.active_view = self.active_key = None
        self._redraw(view)
        self.update_results()

    def _delete_point(self, view):
        code = self.point_selects[view].currentData()
        if code:
            self.points[view].pop(code, None)
            self._redraw(view)
            self.update_results()

    def _toggle_trace(self, view, side):
        if self.path_capture == (view, side):
            if len(self.traces[view][side]) < 2:
                QMessageBox.information(self, "Recorrido incompleto", "Marca al menos dos puntos sobre la curva.")
                return
            self._finish_trace(view, side)
            return
        if self.path_capture:
            self._finish_trace(*self.path_capture, force=True)
        start, end = ("lat_R", "mol_R") if side == "Derecho" else ("lat_L", "mol_L")
        if start not in self.points[view] or end not in self.points[view]:
            QMessageBox.warning(self, "Faltan referencias", "Coloca primero los dos extremos del espacio.")
            return
        self.traces[view][side] = []
        self.path_capture = (view, side)
        self.canvases[view].set_point_mode(True)
        self.path_buttons[(view, side)].setText("Finalizar recorrido")
        self.source_status.setText("Marca al menos dos puntos siguiendo la curvatura; pulsa de nuevo para finalizar.")
        self._redraw(view)

    def _finish_trace(self, view, side, force=False):
        if len(self.traces[view][side]) < 2 and not force:
            return
        self.path_capture = None
        self.canvases[view].set_point_mode(False)
        self.path_buttons[(view, side)].setText(
            "Trazar espacio derecho" if side == "Derecho" else "Trazar espacio izquierdo"
        )
        self._redraw(view)
        self.update_results()

    def _clear_traces(self, view):
        if self.path_capture and self.path_capture[0] == view:
            self.path_capture = None
            self.canvases[view].set_point_mode(False)
        self.traces[view] = {"Derecho": [], "Izquierdo": []}
        for side in ("Derecho", "Izquierdo"):
            self.path_buttons[(view, side)].setText(
                "Trazar espacio derecho" if side == "Derecho" else "Trazar espacio izquierdo"
            )
        self._redraw(view)
        self.update_results()

    def _tab_changed(self, index):
        if self.path_capture:
            self._finish_trace(*self.path_capture, force=True)
        for canvas in self.canvases.values():
            canvas.set_point_mode(False)

    def _distance(self, view, a, b):
        points = self.points[view]
        if a not in points or b not in points:
            return None
        return math.hypot(points[b][0]-points[a][0], points[b][1]-points[a][1])

    def _incisor_widths(self):
        widths = {}
        for tooth in ("42", "41", "31", "32"):
            value = self._distance("incisors", tooth+"_M", tooth+"_D")
            if value is None:
                return None
            widths[tooth] = value
        return widths

    def _available_path_px(self, arch, side):
        p = self.points[arch]
        start, end = ("lat_R", "mol_R") if side == "Derecho" else ("lat_L", "mol_L")
        path = self.traces[arch][side]
        if start not in p or end not in p or len(path) < 2:
            return None
        coords = [p[start], *path, p[end]]
        return sum(math.hypot(b[0]-a[0], b[1]-a[1]) for a, b in zip(coords, coords[1:]))

    def _result(self, arch, side):
        widths = self._incisor_widths()
        if not widths:
            return "Pendiente"
        ref_px = self._distance(arch, "ref_M", "ref_D")
        path_px = self._available_path_px(arch, side)
        ref_key = self.reference_selects[arch].currentData()
        incisor_range = _incisor_sum_range(widths)
        available = _available_range(path_px, ref_px, ref_key)
        sex = self.sex.currentText() if self.method == "moyers" else ""
        method_arch = "superior" if arch == "upper" else "inferior"
        required = _required_range(incisor_range, self.method, method_arch, sex)
        if path_px is None:
            return "Pendiente"
        if not available or not required:
            return "No concluyente"
        return _qualitative_result(available, required)

    def _results_dict(self):
        result = {}
        for arch, label in (("upper", "Superior"), ("lower", "Inferior")):
            for side in ("Derecho", "Izquierdo"):
                result[f"{label} · {side}"] = self._result(arch, side)
        return result

    def update_results(self, *args):
        values = self._results_dict()
        labels = ("Superior · Derecho", "Superior · Izquierdo", "Inferior · Derecho", "Inferior · Izquierdo")
        self.results.setRowCount(4)
        for row, label in enumerate(labels):
            self.results.setItem(row, 0, QTableWidgetItem(label))
            self.results.setItem(row, 1, QTableWidgetItem(values[label]))

    def _validate_complete(self):
        if not self.incisors_present.isChecked() and not self.periapical_image:
            return "Indica que los incisivos inferiores están erupcionados o carga una radiografía periapical."
        if self._incisor_widths() is None:
            return "Marca los bordes mesial y distal de 42, 41, 31 y 32."
        if self.method == "moyers" and self.sex.currentText() not in ("Femenino", "Masculino"):
            return "Selecciona el sexo requerido por la tabla de Moyers."
        for arch in ("upper", "lower"):
            if self._distance(arch, "ref_M", "ref_D") is None:
                return "Marca el borde mesial y distal del diente usado como regla en ambas arcadas."
            for side in ("Derecho", "Izquierdo"):
                if self._available_path_px(arch, side) is None:
                    return f"Completa el recorrido curvo de espacio: {arch} · {side.lower()}."
        return None

    def _save(self):
        if self.status.currentText() == "Completo":
            issue = self._validate_complete()
            if issue:
                QMessageBox.warning(self, "Análisis incompleto", issue)
                return
        self.accept()

    def values(self):
        values = {
            "Método": self.method_title,
            "Resultado por hemiarcada": self._results_dict(),
            "Puntos": self.points,
            "Recorridos": self.traces,
            "Diente de referencia": {
                arch: self.reference_selects[arch].currentData()
                for arch in ("upper", "lower")
            },
            "Incisivos inferiores erupcionados": self.incisors_present.isChecked(),
            "Fuente incisivos": "Radiografía periapical" if self.periapical_image else "Modelo inferior",
            "Unidad de visualización": "Cualitativa",
        }
        if self.method == "moyers":
            values["Sexo"] = self.sex.currentText()
        if self.periapical_image:
            values["Radiografía periapical"] = self.periapical_image
        return (
            self.status.currentText(), values,
            self.observations.toPlainText().strip(),
            self.conclusion.toPlainText().strip(),
        )
