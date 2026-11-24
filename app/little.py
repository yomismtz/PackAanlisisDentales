"""Índice de irregularidad de Little para modelos superiores e inferiores."""
import math
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPen, QPixmap
from PySide6.QtWidgets import (QDialog, QGraphicsView, QGraphicsScene, QLabel, QPushButton,
    QComboBox, QVBoxLayout, QHBoxLayout, QSplitter, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialogButtonBox, QTextEdit, QFormLayout, QMessageBox)

CONTACTS = [
    ("P1", "Referencia en el sector del canino derecho"),
    ("P2", "Referencia entre lateral y central derechos"),
    ("P3", "Referencia interincisiva derecha"),
    ("P4", "Referencia interincisiva izquierda"),
    ("P5", "Referencia entre central y lateral izquierdos"),
    ("P6", "Referencia en el sector del canino izquierdo"),
]
SEGMENTS = [
    ("P1–P2", "P1", "P2"), ("P2–P3", "P2", "P3"),
    ("P3–P4", "P3", "P4"), ("P4–P5", "P4", "P5"),
    ("P5–P6", "P5", "P6"),
]

def little_measurements(points):
    measures = {}
    for label, first, second in SEGMENTS:
        if first in points and second in points:
            measures[label] = math.hypot(points[second][0]-points[first][0],
                                         points[second][1]-points[first][1])
    return measures, sum(measures.values()) if len(measures) == 5 else None

class LittleCanvas(QGraphicsView):
    point_clicked = Signal(float, float)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene_obj = QGraphicsScene(self)
        self.setScene(self.scene_obj)
        self.setBackgroundBrush(QColor("#22262e"))
        self.pixmap_item = None
        self.active = False
        self.marks = []
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
    def show_image(self, path):
        pix = QPixmap(path)
        if pix.isNull():
            raise ValueError("El archivo no contiene una imagen compatible.")
        self.scene_obj.clear()
        self.marks = []
        self.pixmap_item = self.scene_obj.addPixmap(pix)
        self.scene_obj.setSceneRect(self.pixmap_item.boundingRect())
        self.resetTransform()
        self.fitInView(self.scene_obj.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    def render_points(self, points):
        for item in self.marks:
            self.scene_obj.removeItem(item)
        self.marks = []
        if self.pixmap_item is None:
            return
        pen = QPen(QColor("#22B8B0"), 2)
        for _, first, second in SEGMENTS:
            if first in points and second in points:
                a, b = points[first], points[second]
                self.marks.append(self.scene_obj.addLine(a[0], a[1], b[0], b[1], pen))
        for key, (x, y) in points.items():
            dot = self.scene_obj.addEllipse(x-5, y-5, 10, 10,
                QPen(QColor("#6D45A6"), 2), QColor("#FFFFFF"))
            label = self.scene_obj.addText(key)
            label.setDefaultTextColor(QColor("#FFFFFF"))
            label.setPos(x+7, y-18)
            self.marks.extend([dot, label])
    def set_point_mode(self, active):
        self.active = active
        self.setDragMode(QGraphicsView.DragMode.NoDrag if active
                         else QGraphicsView.DragMode.ScrollHandDrag)
    def mousePressEvent(self, event):
        if self.active and event.button() == Qt.MouseButton.LeftButton:
            point = self.mapToScene(event.position().toPoint())
            if self.scene_obj.sceneRect().contains(point):
                self.point_clicked.emit(point.x(), point.y())
                event.accept()
                return
        super().mousePressEvent(event)
    def wheelEvent(self, event):
        if self.pixmap_item is not None:
            factor = 1.15 if event.angleDelta().y() > 0 else 1/1.15
            self.scale(factor, factor)
            event.accept()
        else:
            super().wheelEvent(event)
    def fit_image(self):
        if self.pixmap_item is not None:
            self.resetTransform()
            self.fitInView(self.scene_obj.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

class LittleDialog(QDialog):
    def __init__(self, image_path=None, existing=None, arch="Superior", parent=None):
        super().__init__(parent)
        self.arch = arch
        self.existing = existing or {}
        saved = self.existing.get("values", {})
        self.points = {key: tuple(value) for key, value in saved.get("Puntos", {}).items()
                       if isinstance(value, (list, tuple)) and len(value) == 2}
        self.setWindowTitle(f"AVIS · Índice de irregularidad de Little · {arch}")
        self.resize(1380, 850)
        self.setMinimumSize(1050, 680)
        self.canvas = LittleCanvas()
        self.canvas.setMinimumSize(620, 500)
        self.canvas.point_clicked.connect(self.on_point)
        self.point_box = QComboBox()
        self.point_box.addItem("Selecciona punto de contacto", "")
        for key, description in CONTACTS:
            self.point_box.addItem(f"{key} · {description}", key)
        self.place = QPushButton("Colocar / corregir punto")
        self.place.clicked.connect(self.activate)
        self.delete = QPushButton("Eliminar punto")
        self.delete.clicked.connect(self.remove)
        self.clear = QPushButton("Limpiar puntos")
        self.clear.clicked.connect(self.clear_points)
        self.fit = QPushButton("Ajustar imagen")
        self.fit.clicked.connect(self.canvas.fit_image)
        self.status = QComboBox()
        self.status.addItems(["Pendiente", "En proceso", "Completo"])
        self.status.setCurrentText(self.existing.get("status", "Pendiente"))
        self.hint = QLabel("Selecciona un contacto, activa colocación y haz clic en la imagen. Rueda para zoom; arrastra para desplazarte.")
        self.hint.setWordWrap(True)
        self.progress = QLabel()
        self.table = QTableWidget(5, 2)
        self.table.setHorizontalHeaderLabels(["Segmento", "Distancia relativa (px)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.total = QLabel()
        self.diagnosis = QLabel()
        self.diagnosis.setWordWrap(True)
        self.obs = QTextEdit(self.existing.get("observations", ""))
        self.obs.setMaximumHeight(70)
        self.conclusion = QTextEdit(self.existing.get("conclusion", ""))
        self.conclusion.setMaximumHeight(70)
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Modelo · puntos de contacto de los seis dientes anteriores"))
        left_layout.addWidget(self.canvas, 1)
        left_layout.addWidget(self.hint)
        left = __import__("PySide6.QtWidgets", fromlist=["QWidget"]).QWidget()
        left.setLayout(left_layout)
        right = __import__("PySide6.QtWidgets", fromlist=["QWidget"]).QWidget()
        right_layout = QVBoxLayout(right)
        form = QFormLayout()
        form.addRow("Estado", self.status)
        form.addRow("Punto", self.point_box)
        right_layout.addLayout(form)
        actions = QHBoxLayout()
        actions.addWidget(self.place)
        actions.addWidget(self.delete)
        right_layout.addLayout(actions)
        right_layout.addWidget(self.clear)
        right_layout.addWidget(self.fit)
        right_layout.addWidget(self.progress)
        right_layout.addWidget(self.table)
        right_layout.addWidget(self.total)
        right_layout.addWidget(self.diagnosis)
        right_layout.addWidget(QLabel("Observaciones"))
        right_layout.addWidget(self.obs)
        right_layout.addWidget(QLabel("Conclusión / interpretación"))
        right_layout.addWidget(self.conclusion)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save |
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "Little suma cinco desplazamientos entre seis referencias de contacto de los seis dientes anteriores. "
            "Las distancias se expresan en píxeles relativos; no equivalen a milímetros."
        ))
        layout.addWidget(splitter, 1)
        layout.addWidget(buttons)
        if image_path:
            try:
                self.canvas.show_image(image_path)
            except Exception as exc:
                self.hint.setText(f"No se pudo abrir la imagen: {exc}")
        else:
            self.hint.setText("No se encontró la vista oclusal de esta arcada. Carga el modelo correspondiente.")
        self.update_view()
    def activate(self):
        key = self.point_box.currentData()
        if not key:
            QMessageBox.information(self, "Punto", "Selecciona un punto de contacto.")
            return
        self._active = key
        self.canvas.set_point_mode(True)
        self.hint.setText(f"Haz clic para colocar {key}.")
    def on_point(self, x, y):
        key = getattr(self, "_active", None)
        if key:
            self.points[key] = (x, y)
            self._active = None
            self.canvas.set_point_mode(False)
            self.update_view()
            self.hint.setText("Punto guardado. Selecciona otro o vuelve a colocarlo para corregir.")
    def remove(self):
        key = self.point_box.currentData()
        if key:
            self.points.pop(key, None)
            self.update_view()
    def clear_points(self):
        if QMessageBox.question(self, "Confirmar", "¿Eliminar todos los puntos?") == QMessageBox.StandardButton.Yes:
            self.points.clear()
            self.update_view()
    def update_view(self):
        self.canvas.render_points(self.points)
        self.progress.setText(f"Puntos colocados: {len(self.points)}/6")
        measures, total = little_measurements(self.points)
        for row, (name, _, _) in enumerate(SEGMENTS):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(f"{measures[name]:.2f}" if name in measures else "—"))
        if total is None:
            self.total.setText("Índice de Little: — (faltan puntos)")
            self.diagnosis.setText("Coloca los seis referencias para completar los cinco segmentos.")
        else:
            self.total.setText(f"Índice de Little: {total:.2f} px relativos")
            self.diagnosis.setText(
                "Índice cuantitativo calculado. No se asigna grado clínico de severidad: "
                "los puntos de corte de Little están expresados en milímetros y esta imagen no tiene calibración 1:1."
            )
    def values(self):
        measures, total = little_measurements(self.points)
        values = {
            "Arcada": self.arch,
            "Puntos": {key: list(value) for key, value in self.points.items()},
            "Unidad": "px_relativos",
            "Segmentos": measures,
            "Indice de Little px relativos": total,
            "Clasificacion clinica": "No asignada: imagen sin calibracion 1:1",
        }
        return (self.status.currentText(), values,
                self.obs.toPlainText().strip(), self.conclusion.toPlainText().strip())
