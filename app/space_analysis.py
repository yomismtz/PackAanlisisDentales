"""Análisis de espacio por perímetro de arcada para el método de Carey."""
from __future__ import annotations

import math
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QSplitter, QWidget,
    QLabel, QPushButton, QComboBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialogButtonBox, QTextEdit, QMessageBox,
)
from .moyers import MoyersCanvas


CAREY_TEETH = {
    "superior": ("15", "14", "13", "12", "11", "21", "22", "23", "24", "25"),
    "inferior": ("45", "44", "43", "42", "41", "31", "32", "33", "34", "35"),
}


def polyline_length(points):
    """Length of a traced line in image pixels; no physical scale is inferred."""
    if not isinstance(points, (list, tuple)) or len(points) < 2:
        return None
    coordinates = []
    for point in points:
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            return None
        x, y = float(point[0]), float(point[1])
        if not math.isfinite(x) or not math.isfinite(y):
            return None
        coordinates.append((x, y))
    length = sum(
        math.hypot(b[0] - a[0], b[1] - a[1])
        for a, b in zip(coordinates, coordinates[1:])
    )
    return length if length > 0 else None


def calculate_carey_arch(points, trace, teeth):
    """Compare arch perimeter with the mesiodistal material of teeth 5–5."""
    if not isinstance(points, dict):
        return None
    available = polyline_length(trace)
    if available is None:
        return None

    required = 0.0
    for tooth in teeth:
        mesial = points.get(f"{tooth}_M")
        distal = points.get(f"{tooth}_D")
        if not mesial or not distal or len(mesial) != 2 or len(distal) != 2:
            return None
        values = (*mesial, *distal)
        if not all(math.isfinite(float(value)) for value in values):
            return None
        width = math.hypot(float(distal[0]) - float(mesial[0]),
                           float(distal[1]) - float(mesial[1]))
        if width <= 0:
            return None
        required += width

    discrepancy = available - required
    if math.isclose(discrepancy, 0.0, abs_tol=1e-6):
        classification = "Equilibrio geométrico relativo"
    elif discrepancy > 0:
        classification = "Exceso de espacio relativo"
    else:
        classification = "Déficit de espacio relativo"

    return {
        "available_px": round(available, 2),
        "required_px": round(required, 2),
        "discrepancy_px": round(discrepancy, 2),
        "classification": classification,
    }


class CareyCanvas(MoyersCanvas):
    def draw_geometry(self, points, trace, teeth):
        for item in self.marks:
            self.scene_obj.removeItem(item)
        self.marks = []
        if self.pixmap_item is None:
            return

        path = [tuple(point) for point in trace]
        if len(path) >= 2:
            pen = QPen(QColor("#F4C95D"), 3)
            for first, second in zip(path, path[1:]):
                line = self.scene_obj.addLine(
                    first[0], first[1], second[0], second[1], pen
                )
                line.setZValue(3)
                self.marks.append(line)

        for tooth in teeth:
            first, second = points.get(f"{tooth}_M"), points.get(f"{tooth}_D")
            if first and second:
                line = self.scene_obj.addLine(
                    first[0], first[1], second[0], second[1],
                    QPen(QColor("#22B8B0"), 2),
                )
                line.setZValue(4)
                self.marks.append(line)

        for code, (x, y) in points.items():
            dot = self.scene_obj.addEllipse(
                x - 4, y - 4, 8, 8,
                QPen(QColor("#22B8B0"), 2), QColor("#FFFFFF")
            )
            label = self.scene_obj.addText(code)
            label.setDefaultTextColor(QColor("#FFFFFF"))
            label.setPos(x + 6, y - 16)
            self.marks.extend([dot, label])


class CareySpaceDialog(QDialog):
    """Carey for permanent dentition; all measurements remain image-relative."""
    def __init__(self, upper_image=None, lower_image=None, existing=None, parent=None):
        super().__init__(parent)
        self.existing = existing or {}
        saved = self.existing.get("values", {}) or {}
        self.legacy_values = dict(saved.get("Registro previo (formato anterior)", {}) or {})
        for label, value in saved.items():
            if label not in ("Arcadas", "Método", "Unidad", "Limitación", "Registro previo (formato anterior)") and value not in (None, ""):
                self.legacy_values[label] = value
        arches = saved.get("Arcadas", {}) or {}
        self.points = {
            arch: {
                code: tuple(value)
                for code, value in (arches.get(arch, {}).get("Puntos", {}) or {}).items()
                if isinstance(value, (list, tuple)) and len(value) == 2
            }
            for arch in ("superior", "inferior")
        }
        self.traces = {
            arch: [
                tuple(point)
                for point in (arches.get(arch, {}).get("Recorrido disponible", []) or [])
                if isinstance(point, (list, tuple)) and len(point) == 2
            ]
            for arch in ("superior", "inferior")
        }
        self.images = {"superior": upper_image, "inferior": lower_image}
        self.canvases = {}
        self.point_selects = {}
        self.trace_buttons = {}
        self.capture = None

        self.setWindowTitle("AVIS · Carey mandibular y perímetro maxilar")
        self.resize(1480, 920)
        self.setMinimumSize(1120, 740)

        self.status = QComboBox()
        self.status.addItems(["Pendiente", "En proceso", "Completo"])
        self.status.setCurrentText(self.existing.get("status", "Pendiente"))

        self.tabs = QTabWidget()
        self._build_arch_tab("superior", "Modelo superior")
        self._build_arch_tab("inferior", "Modelo inferior")

        self.results = QTableWidget(2, 5)
        self.results.setHorizontalHeaderLabels([
            "Arcada", "Disponible (px)", "Requerido (px)",
            "Disponible − requerido (px)", "Resultado",
        ])
        self.results.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.note = QLabel(
            "Carey: traza el perímetro desde mesial del primer molar de un lado "
            "hasta mesial del primer molar contralateral, siguiendo la forma de la arcada. "
            "Marca mesial y distal de cada diente permanente 5–5. AVIS compara ambas "
            "longitudes en píxeles de la misma imagen; no las convierte a milímetros "
            "ni asigna indicaciones de extracción."
        )
        self.note.setWordWrap(True)
        if self.legacy_values:
            self.note.setText(
                self.note.text()
                + " Hay valores manuales de una versión anterior; se conservarán como antecedente."
            )
        self.nance_note = QLabel(
            "Nance en dentición mixta no se automatiza aquí: requiere estimar el tamaño "
            "de caninos y premolares no erupcionados mediante una fuente radiográfica y "
            "corregir la magnificación. No se sustituye por una conversión de píxeles."
        )
        self.nance_note.setWordWrap(True)

        self.observations = QTextEdit(self.existing.get("observations", ""))
        self.observations.setMaximumHeight(65)
        self.conclusion = QTextEdit(self.existing.get("conclusion", ""))
        self.conclusion.setMaximumHeight(65)

        form = QFormLayout()
        form.addRow("Estado", self.status)
        right = QVBoxLayout()
        right.addLayout(form)
        right.addWidget(QLabel("Comparación geométrica por arcada"))
        right.addWidget(self.results, 1)
        right.addWidget(self.note)
        right.addWidget(self.nance_note)
        right.addWidget(QLabel("Observaciones"))
        right.addWidget(self.observations)
        right.addWidget(QLabel("Conclusión profesional"))
        right.addWidget(self.conclusion)

        split = QSplitter(Qt.Orientation.Horizontal)
        left_widget, right_widget = QWidget(), QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(self.tabs, 1)
        right_widget.setLayout(right)
        split.addWidget(left_widget)
        split.addWidget(right_widget)
        split.setStretchFactor(0, 3)
        split.setStretchFactor(1, 2)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "Método disponible: Carey para dentición permanente. El módulo conserva "
            "el registro por separado para arcada superior e inferior."
        ))
        layout.addWidget(split, 1)
        layout.addWidget(buttons)

        for arch in ("superior", "inferior"):
            self._redraw(arch)
        self.update_results()

    def _build_arch_tab(self, arch, title):
        page = QWidget()
        layout = QVBoxLayout(page)
        canvas = CareyCanvas()
        canvas.setMinimumSize(560, 450)
        canvas.point_clicked.connect(lambda x, y, key=arch: self._on_click(key, x, y))
        if self.images.get(arch):
            canvas.show_image(self.images[arch])
        self.canvases[arch] = canvas

        selector = QComboBox()
        selector.addItem("Selecciona un punto mesial o distal", "")
        for tooth in CAREY_TEETH[arch]:
            selector.addItem(f"{tooth} · mesial", f"{tooth}_M")
            selector.addItem(f"{tooth} · distal", f"{tooth}_D")
        self.point_selects[arch] = selector

        place = QPushButton("Colocar / corregir punto")
        place.clicked.connect(lambda checked=False, key=arch: self._activate_point(key))
        trace = QPushButton("Trazar perímetro disponible")
        trace.clicked.connect(lambda checked=False, key=arch: self._toggle_trace(key))
        self.trace_buttons[arch] = trace
        clear = QPushButton("Borrar perímetro")
        clear.clicked.connect(lambda checked=False, key=arch: self._clear_trace(key))

        row = QHBoxLayout()
        row.addWidget(selector, 2)
        row.addWidget(place)
        row.addWidget(trace)
        row.addWidget(clear)
        layout.addLayout(row)
        layout.addWidget(QLabel(
            "Marca los extremos mesial y distal de cada uno de los diez dientes 5–5. "
            "Para el perímetro, coloca varios puntos consecutivos siguiendo la arcada."
        ))
        if self.images.get(arch):
            layout.addWidget(canvas, 1)
        else:
            layout.addWidget(QLabel("No se encontró la imagen oclusal de esta arcada."), 1)
        self.tabs.addTab(page, title)

    def _stop_capture(self):
        if not self.capture:
            return
        arch, mode, _ = self.capture
        self.canvases[arch].set_point_mode(False)
        if mode == "trace":
            self.trace_buttons[arch].setText("Continuar perímetro")
        self.capture = None

    def _activate_point(self, arch):
        code = self.point_selects[arch].currentData()
        if not code:
            QMessageBox.information(self, "Punto", "Selecciona primero el punto dentario.")
            return
        canvas = self.canvases[arch]
        if canvas.pixmap_item is None:
            QMessageBox.warning(self, "Modelo requerido", "Carga la vista oclusal correspondiente.")
            return
        self._stop_capture()
        canvas.set_point_mode(True)
        self.capture = (arch, "point", code)

    def _toggle_trace(self, arch):
        if self.capture == (arch, "trace", None):
            self._stop_capture()
            self.update_results()
            return
        canvas = self.canvases[arch]
        if canvas.pixmap_item is None:
            QMessageBox.warning(self, "Modelo requerido", "Carga la vista oclusal correspondiente.")
            return
        self._stop_capture()
        self.traces[arch] = []
        self.capture = (arch, "trace", None)
        canvas.set_point_mode(True)
        self.trace_buttons[arch].setText("Finalizar perímetro")
        self._redraw(arch)

    def _on_click(self, arch, x, y):
        if not self.capture or self.capture[0] != arch:
            return
        _, mode, code = self.capture
        if mode == "point":
            self.points[arch][code] = (x, y)
            self.capture = None
            self.canvases[arch].set_point_mode(False)
        else:
            self.traces[arch].append((x, y))
        self._redraw(arch)
        self.update_results()

    def _clear_trace(self, arch):
        self.traces[arch] = []
        if self.capture and self.capture[0] == arch:
            self.capture = None
            self.canvases[arch].set_point_mode(False)
        self.trace_buttons[arch].setText("Trazar perímetro disponible")
        self._redraw(arch)
        self.update_results()

    def _redraw(self, arch):
        self.canvases[arch].draw_geometry(
            self.points[arch], self.traces[arch], CAREY_TEETH[arch]
        )

    def update_results(self):
        for row, arch in enumerate(("superior", "inferior")):
            result = calculate_carey_arch(
                self.points[arch], self.traces[arch], CAREY_TEETH[arch]
            )
            method_label = "Perímetro maxilar" if arch == "superior" else "Carey mandibular"
            self.results.setItem(row, 0, QTableWidgetItem(method_label))
            values = (
                "—" if result is None else f"{result['available_px']:.2f}",
                "—" if result is None else f"{result['required_px']:.2f}",
                "—" if result is None else f"{result['discrepancy_px']:+.2f}",
                "Pendiente" if result is None else result["classification"],
            )
            for column, value in enumerate(values, start=1):
                self.results.setItem(row, column, QTableWidgetItem(value))

    def _save(self):
        if not any(self.points.values()) and not any(self.traces.values()):
            QMessageBox.warning(self, "Análisis vacío", "Marca los puntos y traza al menos una arcada.")
            return
        self.accept()

    def values(self):
        arches = {}
        for arch in ("superior", "inferior"):
            result = calculate_carey_arch(
                self.points[arch], self.traces[arch], CAREY_TEETH[arch]
            )
            arches[arch] = {
                "Puntos": {key: list(value) for key, value in self.points[arch].items()},
                "Recorrido disponible": [list(point) for point in self.traces[arch]],
            }
            if result:
                arches[arch].update({
                    "Espacio disponible px": result["available_px"],
                    "Espacio requerido px": result["required_px"],
                    "Discrepancia px": result["discrepancy_px"],
                    "Resultado": result["classification"],
                })
        return (
            self.status.currentText(),
            {
                "Método": "Carey · dentición permanente",
                "Unidad": "px_relativos",
                "Arcadas": arches,
                "Limitación": (
                    "El método Nance para dentición mixta no está automatizado; "
                    "requiere medición radiográfica corregida de dientes no erupcionados."
                ),
                **({"Registro previo (formato anterior)": self.legacy_values} if self.legacy_values else {}),
            },
            self.observations.toPlainText().strip(),
            self.conclusion.toPlainText().strip(),
        )
