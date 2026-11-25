"""Captura estructurada de clasificación de Baumé y relaciones intermaxilares."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QSplitter, QWidget,
    QLabel, QComboBox, QTabWidget, QTextEdit, QPushButton, QDialogButtonBox,
)
from .moyers import MoyersCanvas


def _image_tabs(images):
    tabs = QTabWidget()
    for label, path in images.items():
        page = QWidget()
        layout = QVBoxLayout(page)
        canvas = MoyersCanvas()
        canvas.setMinimumSize(520, 390)
        if path:
            canvas.show_image(path)
            layout.addWidget(canvas, 1)
        else:
            layout.addWidget(QLabel("Imagen no disponible para esta vista."), 1)
        tabs.addTab(page, label)
    return tabs


class StructuredOcclusionDialog(QDialog):
    TITLE = "AVIS · Evaluación oclusal"
    INTRO = ""
    GROUPS = ()

    def __init__(self, images=None, existing=None, parent=None):
        super().__init__(parent)
        self.existing = existing or {}
        all_saved = self.existing.get("values", {}) or {}
        saved = all_saved.get("Evaluación estructurada", {}) or {}
        self.legacy_values = dict(all_saved.get("Registro previo (formato anterior)", {}) or {})
        for label, value in all_saved.items():
            if label not in ("Evaluación estructurada", "Método", "Registro previo (formato anterior)") and value not in (None, ""):
                self.legacy_values[label] = value
        self.fields = {}
        self.setWindowTitle(self.TITLE)
        self.resize(1380, 880)
        self.setMinimumSize(1080, 700)

        left = QVBoxLayout()
        left.addWidget(_image_tabs(images or {}), 1)
        left_widget = QWidget()
        left_widget.setLayout(left)

        right_widget = QWidget()
        right = QVBoxLayout(right_widget)
        self.status = QComboBox()
        self.status.addItems(["Pendiente", "En proceso", "Completo"])
        self.status.setCurrentText(self.existing.get("status", "Pendiente"))
        form = QFormLayout()
        form.addRow("Estado", self.status)
        right.addLayout(form)

        for group_title, definitions in self.GROUPS:
            box = QWidget()
            group_form = QFormLayout(box)
            for label, options in definitions:
                combo = QComboBox()
                combo.addItem("Seleccionar", "")
                combo.addItems(list(options))
                saved_value = saved.get(label, "")
                index = combo.findText(saved_value)
                if index >= 0:
                    combo.setCurrentIndex(index)
                self.fields[label] = combo
                group_form.addRow(label, combo)
            right.addWidget(QLabel(group_title))
            right.addWidget(box)

        if self.legacy_values:
            legacy_notice = QLabel(
                "Este expediente contiene campos manuales de una versión anterior. "
                "Se conservarán como antecedente; completa las nuevas clasificaciones para actualizar el análisis."
            )
            legacy_notice.setWordWrap(True)
            right.addWidget(legacy_notice)
        right.addWidget(QLabel("Observaciones"))
        self.observations = QTextEdit(self.existing.get("observations", ""))
        self.observations.setMaximumHeight(70)
        right.addWidget(self.observations)
        right.addWidget(QLabel("Conclusión profesional"))
        self.conclusion = QTextEdit(self.existing.get("conclusion", ""))
        self.conclusion.setMaximumHeight(80)
        right.addWidget(self.conclusion)
        right.addStretch()

        split = QSplitter()
        split.addWidget(left_widget)
        split.addWidget(right_widget)
        split.setStretchFactor(0, 3)
        split.setStretchFactor(1, 2)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        intro = QLabel(self.INTRO)
        intro.setWordWrap(True)
        layout.addWidget(intro)
        layout.addWidget(split, 1)
        layout.addWidget(buttons)

    def values(self):
        return (
            self.status.currentText(),
            {
                "Evaluación estructurada": {
                    label: combo.currentText()
                    for label, combo in self.fields.items()
                },
                "Método": self.__class__.__name__,
                **({"Registro previo (formato anterior)": self.legacy_values} if self.legacy_values else {}),
            },
            self.observations.toPlainText().strip(),
            self.conclusion.toPlainText().strip(),
        )


class BaumeDialog(StructuredOcclusionDialog):
    TITLE = "AVIS · Clasificación de Baumé"
    INTRO = (
        "Registra por separado el tipo de arco superior e inferior, los espacios primates "
        "y el plano terminal en cada lado. Tipo I corresponde a arcada con espacios "
        "fisiológicos; Tipo II, sin espacios. El plano terminal se clasifica observando "
        "las caras distales de los segundos molares temporales en oclusión. AVIS no predice "
        "automáticamente la futura clase de Angle."
    )
    GROUPS = (
        ("Tipo de arco", (
            ("Tipo de arcada superior", (
                "Tipo I · con espacios fisiológicos",
                "Tipo II · sin espacios fisiológicos",
                "No evaluable",
            )),
            ("Tipo de arcada inferior", (
                "Tipo I · con espacios fisiológicos",
                "Tipo II · sin espacios fisiológicos",
                "No evaluable",
            )),
        )),
        ("Espacios primates", (
            ("Espacio primate superior derecho", ("Presente", "Ausente", "No evaluable")),
            ("Espacio primate superior izquierdo", ("Presente", "Ausente", "No evaluable")),
            ("Espacio primate inferior derecho", ("Presente", "Ausente", "No evaluable")),
            ("Espacio primate inferior izquierdo", ("Presente", "Ausente", "No evaluable")),
        )),
        ("Planos terminales", (
            ("Plano terminal derecho", (
                "Recto", "Escalón mesial", "Escalón mesial exagerado",
                "Escalón distal", "No evaluable",
            )),
            ("Plano terminal izquierdo", (
                "Recto", "Escalón mesial", "Escalón mesial exagerado",
                "Escalón distal", "No evaluable",
            )),
        )),
    )


class IntermaxillaryDialog(StructuredOcclusionDialog):
    TITLE = "AVIS · Relaciones intermaxilares"
    INTRO = (
        "Registra las relaciones sagitales, verticales y transversales observadas en oclusión. "
        "Las clases molares y caninas se registran por lado. Overjet y sobremordida se expresan "
        "como categorías descriptivas, sin milímetros ni umbrales automáticos."
    )
    GROUPS = (
        ("Relación sagital", (
            ("Relación molar derecha", ("Clase I", "Clase II", "Clase III", "No evaluable")),
            ("Relación molar izquierda", ("Clase I", "Clase II", "Clase III", "No evaluable")),
            ("Relación canina derecha", ("Clase I", "Clase II", "Clase III", "No evaluable")),
            ("Relación canina izquierda", ("Clase I", "Clase II", "Clase III", "No evaluable")),
            ("Overjet", (
                "Positivo · incisivos superiores por delante",
                "Borde a borde / cero",
                "Negativo · invertido",
                "No evaluable",
            )),
        )),
        ("Relación vertical", (
            ("Sobremordida vertical", (
                "Sin alteración aparente",
                "Aumentada / profunda",
                "Borde a borde",
                "Mordida abierta anterior",
                "Mordida abierta posterior",
                "No evaluable",
            )),
        )),
        ("Relación transversal", (
            ("Relación transversal", (
                "Sin mordida cruzada",
                "Mordida cruzada anterior",
                "Mordida cruzada posterior derecha",
                "Mordida cruzada posterior izquierda",
                "Mordida cruzada posterior bilateral",
                "Mordida en tijera derecha",
                "Mordida en tijera izquierda",
                "Mordida en tijera bilateral",
                "No evaluable",
            )),
        )),
        ("Líneas medias y cierre", (
            ("Línea media superior", (
                "Centrada", "Desviada a derecha", "Desviada a izquierda", "No evaluable",
            )),
            ("Línea media inferior", (
                "Centrada", "Desviada a derecha", "Desviada a izquierda", "No evaluable",
            )),
            ("Desviación mandibular al cierre", (
                "No observada", "Hacia la derecha", "Hacia la izquierda",
                "Hacia anterior", "No evaluable",
            )),
        )),
    )
