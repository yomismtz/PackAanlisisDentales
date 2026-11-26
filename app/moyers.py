"""Análisis de espacio de dentición mixta según Moyers al percentil 75 %."""
import math
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPen, QPixmap
from PySide6.QtWidgets import (
    QDialog, QGraphicsView, QGraphicsScene, QLabel, QPushButton, QComboBox,
    QVBoxLayout, QHBoxLayout, QSplitter, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialogButtonBox, QTextEdit, QFormLayout, QMessageBox,
    QTabWidget, QWidget, QFileDialog, QCheckBox
)

# Tabla de predicción Moyers, percentil 75 %. Valores en mm por hemiarcada.
# La suma de referencia es la de los cuatro incisivos mandibulares permanentes.
INCISOR_SUMS = [19.5 + i * 0.5 for i in range(13)]
PREDICTION_75 = {
    "Masculino": {
        "superior": [20.3,20.5,20.8,21.0,21.3,21.5,21.8,22.0,22.3,22.5,22.8,23.0,23.3],
        "inferior": [20.3,20.5,20.8,21.0,21.3,21.5,21.8,22.0,22.3,22.5,22.8,23.0,23.3],
    },
    "Femenino": {
        "superior": [20.4,20.5,20.6,20.8,20.9,21.0,21.2,21.3,21.5,21.6,21.8,21.9,22.1],
        "inferior": [19.6,19.8,20.1,20.3,20.6,20.8,21.1,21.3,21.6,21.9,22.1,22.4,22.7],
    },
}

def predict_moyers_75(incisor_sum, sex, arch):
    """Interpolación lineal dentro del rango publicado; fuera del rango no extrapola."""
    if sex not in PREDICTION_75 or arch not in ("superior", "inferior"):
        raise ValueError("Selecciona sexo y arcada válidos.")
    if incisor_sum < INCISOR_SUMS[0] or incisor_sum > INCISOR_SUMS[-1]:
        raise ValueError("La suma de incisivos está fuera del rango tabulado (19.5–25.5 mm).")
    for i, value in enumerate(INCISOR_SUMS):
        if math.isclose(incisor_sum, value, abs_tol=1e-8):
            return PREDICTION_75[sex][arch][i]
    for i in range(len(INCISOR_SUMS)-1):
        lo, hi = INCISOR_SUMS[i], INCISOR_SUMS[i+1]
        if lo < incisor_sum < hi:
            ratio = (incisor_sum-lo)/(hi-lo)
            a, b = PREDICTION_75[sex][arch][i:i+2]
            return round(a + ratio*(b-a), 2)
    raise ValueError("No se pudo interpolar la tabla de Moyers.")

def moyers_discrepancy(available, required):
    """Discrepancia = espacio disponible - espacio requerido."""
    value = round(available-required, 2)
    if math.isclose(value, 0.0, abs_tol=0.005):
        return value, "Espacio exacto"
    if value > 0:
        return value, "Existe espacio excedente para la erupción de permanentes"
    return value, "Existe déficit de espacio para la erupción de permanentes"

INCISOR_POINTS = [
    ("42_M","42 · mesial"),("42_D","42 · distal"),
    ("41_M","41 · mesial"),("41_D","41 · distal"),
    ("31_M","31 · mesial"),("31_D","31 · distal"),
    ("32_M","32 · mesial"),("32_D","32 · distal"),
]
ARCH_POINTS = [
    ("lat_R","Distal del incisivo lateral · derecho"),
    ("mol_R","Límite mesial del primer molar / distal del segundo temporal · derecho"),
    ("lat_L","Distal del incisivo lateral · izquierdo"),
    ("mol_L","Límite mesial del primer molar / distal del segundo temporal · izquierdo"),
]

class MoyersCanvas(QGraphicsView):
    point_clicked = Signal(float, float)
    def __init__(self):
        super().__init__()
        self.scene_obj = QGraphicsScene(self); self.setScene(self.scene_obj)
        self.setBackgroundBrush(QColor("#22262e"))
        self.pixmap_item = None; self.active = False; self.marks = []
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
    def show_image(self, path):
        self.scene_obj.clear(); self.marks=[]; self.pixmap_item=None
        if path and Path(path).is_file():
            pix=QPixmap(str(path))
            if not pix.isNull():
                self.pixmap_item=self.scene_obj.addPixmap(pix)
                self.scene_obj.setSceneRect(self.pixmap_item.boundingRect())
                self.resetTransform()
                self.fitInView(self.scene_obj.sceneRect(),Qt.AspectRatioMode.KeepAspectRatio)
    def set_point_mode(self, enabled):
        self.active=enabled
        self.setDragMode(QGraphicsView.DragMode.NoDrag if enabled else QGraphicsView.DragMode.ScrollHandDrag)
    def draw_points(self, points):
        for item in self.marks:
            self.scene_obj.removeItem(item)
        self.marks=[]
        if self.pixmap_item is None:return
        for key,(x,y) in points.items():
            dot=self.scene_obj.addEllipse(x-5,y-5,10,10,QPen(QColor("#22B8B0"),2),QColor("#FFFFFF"))
            label=self.scene_obj.addText(key);label.setDefaultTextColor(QColor("#FFFFFF"));label.setPos(x+7,y-18)
            self.marks.extend([dot,label])
    def mousePressEvent(self,event):
        if self.active and event.button()==Qt.MouseButton.LeftButton:
            p=self.mapToScene(event.position().toPoint())
            if self.scene_obj.sceneRect().contains(p):
                self.point_clicked.emit(p.x(),p.y());event.accept();return
        super().mousePressEvent(event)
    def wheelEvent(self,event):
        if self.pixmap_item:
            factor=1.15 if event.angleDelta().y()>0 else 1/1.15
            self.scale(factor,factor);event.accept()
        else:super().wheelEvent(event)

class MoyersDialog(QDialog):
    """Tres vistas: incisivos inferiores, espacio superior y espacio inferior."""
    def __init__(self, upper_image=None, lower_image=None, existing=None,
                 patient_sex="", periapical_image=None, parent=None):
        super().__init__(parent)
        self.existing=existing or {}; self.saved=self.existing.get("values",{})
        self.points={k:{p:tuple(v) for p,v in self.saved.get(k,{}).items()
                        if isinstance(v,(list,tuple)) and len(v)==2}
                     for k in ("incisors","upper","lower")}
        self.paths={"incisors":periapical_image,"upper":upper_image,"lower":lower_image}
        self.periapical_image=periapical_image
        self._active_view=None; self._active_key=None
        self.setWindowTitle("AVIS · Análisis de dentición mixta · Moyers 75 %")
        self.resize(1480,920); self.setMinimumSize(1120,740)
        self.status=QComboBox();self.status.addItems(["Pendiente","En proceso","Completo"])
        self.status.setCurrentText(self.existing.get("status","Pendiente"))
        self.incisors_present=QCheckBox("Los cuatro incisivos inferiores permanentes están erupcionados y medibles en el modelo")
        self.incisors_present.setChecked(self.saved.get("Incisivos inferiores erupcionados", False))
        self.paths["incisors"] = periapical_image or (lower_image if self.incisors_present.isChecked() else None)
        self.incisors_present.toggled.connect(self._incisor_source_changed)
        self.tabs=QTabWidget(); self.views={}
        self.point_selects={}
        self._build_view_tab("incisors","Incisivos inferiores · 42, 41, 31 y 32",INCISOR_POINTS)
        self._build_view_tab("upper","Arcada superior · espacio disponible",ARCH_POINTS)
        self._build_view_tab("lower","Arcada inferior · espacio disponible",ARCH_POINTS)
        self.tabs.currentChanged.connect(self._tab_changed)
        self.source_status=QLabel()
        self.upload=QPushButton("Cargar radiografía periapical…")
        self.upload.clicked.connect(self._load_periapical)
        self.incisors_present.toggled.connect(self.update_results)
        self.results=QTableWidget(4,2)
        self.results.setHorizontalHeaderLabels(["Arcada / lado","Espacio disponible (px relativos)"])
        self.results.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.inc_sum=QLabel("Suma de incisivos inferiores: —")
        self.pred=QLabel(
            "La tabla clásica de Moyers al 75 % no se calcula: requiere dimensiones reales en mm. "
            "Con fotografías no calibradas AVIS registra únicamente distancias relativas en píxeles."
        )
        self.inc_sum.setStyleSheet("font-size:13pt;font-weight:700")
        self.pred.setWordWrap(True)
        self.obs=QTextEdit(self.existing.get("observations",""));self.obs.setMaximumHeight(65)
        self.conclusion=QTextEdit(self.existing.get("conclusion",""));self.conclusion.setMaximumHeight(65)
        top=QHBoxLayout();form=QFormLayout();form.addRow("Estado",self.status)
        top.addLayout(form);top.addStretch()
        source=QHBoxLayout();source.addWidget(self.incisors_present);source.addWidget(self.upload)
        left=QVBoxLayout();left.addLayout(top);left.addLayout(source);left.addWidget(self.source_status);left.addWidget(self.tabs,1)
        right=QVBoxLayout();right.addWidget(QLabel("Registro geométrico relativo · no es una predicción clínica Moyers"));right.addWidget(self.inc_sum);right.addWidget(self.pred);right.addWidget(self.results,1)
        right.addWidget(QLabel("Observaciones"));right.addWidget(self.obs);right.addWidget(QLabel("Conclusión profesional"));right.addWidget(self.conclusion)
        split=QSplitter(Qt.Orientation.Horizontal);lw=QWidget();lw.setLayout(left);rw=QWidget();rw.setLayout(right)
        split.addWidget(lw);split.addWidget(rw);split.setStretchFactor(0,3);split.setStretchFactor(1,2)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._save);buttons.rejected.connect(self.reject)
        layout=QVBoxLayout(self);layout.addWidget(QLabel("Marca los bordes mesial y distal de cada incisivo inferior y los límites del espacio en cada hemiarcada. Zoom con rueda y desplazamiento arrastrando."));layout.addWidget(split,1);layout.addWidget(buttons)
        self._refresh_sources();self.update_results()

    def _build_view_tab(self,key,title,point_defs):
        w=QWidget();layout=QVBoxLayout(w);canvas=MoyersCanvas();canvas.setMinimumSize(540,430)
        canvas.point_clicked.connect(lambda x,y,k=key:self._place_point(k,x,y))
        self.views[key]=canvas
        select=QComboBox();select.addItem("Selecciona el punto que vas a colocar","")
        for code,label in point_defs:select.addItem(f"{code} · {label}",code)
        self.point_selects[key]=select
        place=QPushButton("Colocar / corregir punto");place.clicked.connect(lambda k=key:self._activate_point(k))
        delete=QPushButton("Eliminar punto");delete.clicked.connect(lambda k=key:self._delete_point(k))
        row=QHBoxLayout();row.addWidget(select,2);row.addWidget(place);row.addWidget(delete)
        layout.addLayout(row);layout.addWidget(canvas,1)
        self.tabs.addTab(w,title)
    def _tab_changed(self,index):
        if index>=0:
            key=("incisors","upper","lower")[index]
            for k,v in self.views.items():v.set_point_mode(False)
    def _refresh_sources(self):
        for key in ("incisors","upper","lower"):
            self.views[key].show_image(self.paths.get(key))
            self.views[key].draw_points(self.points[key])
        if self.paths.get("incisors"):
            label="Vista para medir los cuatro incisivos inferiores: "+("radiografía periapical" if self.periapical_image else "modelo inferior")
        else:label="Falta imagen para medir los incisivos inferiores."
        self.source_status.setText(label)
        self.upload.setEnabled(not self.incisors_present.isChecked())
    def _incisor_source_changed(self,checked):
        if checked:
            self.periapical_image=None
            self.paths["incisors"]=self.paths.get("lower")
        else:
            self.periapical_image=None;self.paths["incisors"]=None
            self.points["incisors"].clear()
        self._refresh_sources();self.update_results()
    def _load_periapical(self):
        path,_=QFileDialog.getOpenFileName(self,"Seleccionar radiografía periapical","","Imágenes (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)")
        if not path:return
        self.periapical_image=path;self.paths["incisors"]=path
        self.points["incisors"].clear()
        self._refresh_sources();self.tabs.setCurrentIndex(0)
    def _activate_point(self,key):
        code=self.point_selects[key].currentData()
        if not code:QMessageBox.information(self,"Punto","Selecciona primero el punto anatómico.");return
        if self.views[key].pixmap_item is None:
            QMessageBox.warning(self,"Imagen requerida","Carga la imagen correspondiente antes de colocar puntos.");return
        self._active_view=key;self._active_key=code
        self.views[key].set_point_mode(True)
        self.source_status.setText("Haz clic para colocar "+code+".")
    def _place_point(self,key,x,y):
        if self._active_view!=key or not self._active_key:return
        self.points[key][self._active_key]=(x,y)
        self.views[key].set_point_mode(False);self._active_view=None;self._active_key=None
        self.views[key].draw_points(self.points[key]);self.update_results()
    def _delete_point(self,key):
        code=self.point_selects[key].currentData()
        if code:self.points[key].pop(code,None);self.views[key].draw_points(self.points[key]);self.update_results()
    def _distance(self,view,a,b):
        p=self.points[view]
        if a not in p or b not in p:return None
        return math.hypot(p[b][0]-p[a][0],p[b][1]-p[a][1])
    def _incisor_measurements(self):
        out={}
        for tooth in ("42","41","31","32"):
            value=self._distance("incisors",tooth+"_M",tooth+"_D")
            if value is None:return None
            out[tooth]=value
        return out
    def _available(self,arch,side):
        p=self.points[arch]
        a,b=("lat_R","mol_R") if side=="Derecho" else ("lat_L","mol_L")
        return self._distance(arch,a,b)
    def update_results(self,*args):
        self.results.setRowCount(4)
        self.results.clearContents()
        measurements=self._incisor_measurements() if (self.incisors_present.isChecked() or self.periapical_image) else None
        inc_sum=round(sum(measurements.values()),2) if measurements else None
        self.inc_sum.setText(
            "Suma de anchos mesiodistales: " +
            (f"{inc_sum:.2f} px relativos" if inc_sum is not None else "pendiente · faltan puntos")
        )
        self.pred.setText(
            "Moyers 75 % no calculado: una suma en píxeles no se puede comparar con una tabla expresada en mm. "
            "Las fotografías no se consideran escala 1:1."
        )
        for row,(arch,label) in enumerate((("upper","Superior"),("lower","Inferior"))):
            for col,side in enumerate(("Derecho","Izquierdo")):
                available=self._available(arch,side)
                vals=[f"{label} · {side}",f"{available:.2f} px" if available is not None else "Pendiente"]
                for c,value in enumerate(vals):
                    self.results.setItem(row*2+col,c,QTableWidgetItem(value))
    def _save(self):
        if not self.incisors_present.isChecked() and not self.periapical_image:
            QMessageBox.warning(
                self,"Imagen requerida",
                "Indica que los incisivos inferiores están presentes en el modelo o carga la radiografía periapical."
            );return
        if self._incisor_measurements() is None:
            QMessageBox.warning(
                self,"Medición incompleta",
                "Marca los bordes mesial y distal de 42, 41, 31 y 32 en la imagen correspondiente."
            );return
        for arch in ("upper","lower"):
            if any(self._available(arch,side) is None for side in ("Derecho","Izquierdo")):
                QMessageBox.warning(
                    self,"Medición incompleta",
                    f"Completa los puntos de ambos lados de la arcada {arch}."
                );return
        self.accept()
    def values(self):
        measures=self._incisor_measurements() or {}
        inc_sum=round(sum(measures.values()),2) if measures else None
        available={}
        for arch,label in (("upper","Superior"),("lower","Inferior")):
            for side in ("Derecho","Izquierdo"):
                value=self._available(arch,side)
                available[f"{label} · {side}"]=round(value,2) if value is not None else None
        values={
            "Unidad":"px_relativos",
            "Metodo":"Trazado geométrico relativo asociado a Moyers; no equivale a una predicción Moyers 75 %",
            "Motivo sin prediccion":"La tabla Moyers 75 % requiere medidas reales en mm y las fotografías no están calibradas 1:1.",
            "Suma de incisivos inferiores (px relativos)":inc_sum if inc_sum is not None else "",
            "Anchos mesiodistales de incisivos (px relativos)":measures,
            "Espacio disponible por hemiarcada (px relativos)":available,
            "Puntos":self.points,
            "Incisivos inferiores erupcionados":self.incisors_present.isChecked(),
            "Fuente incisivos":"Radiografía periapical" if self.periapical_image else "Modelo inferior",
            "Radiografía periapical":self.periapical_image or "",
        }
        return self.status.currentText(),values,self.obs.toPlainText().strip(),self.conclusion.toPlainText().strip()
        return self.status.currentText(),values,self.obs.toPlainText().strip(),self.conclusion.toPlainText().strip()
