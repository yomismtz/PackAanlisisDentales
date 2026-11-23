"""Trazado guiado y comparación bilateral del análisis panorámico de Levandoski."""
import math
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import (QDialog, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
 QGraphicsLineItem, QGraphicsTextItem, QLabel, QComboBox, QPushButton, QGridLayout,
 QVBoxLayout, QHBoxLayout, QSplitter, QTableWidget, QTableWidgetItem, QHeaderView,
 QDialogButtonBox, QTextEdit, QFormLayout, QInputDialog, QMessageBox)

POINTS = [
 ("M_sup","Referencia de línea media maxilar"),
 ("M_inf","Referencia de línea media mandibular"),
 ("Cd_R","Condilion derecho"), ("Cd_L","Condilion izquierdo"),
 ("Go_R","Gonion derecho"), ("Go_L","Gonion izquierdo"),
 ("Kr_R","Coronion derecho"), ("Kr_L","Coronion izquierdo"),
 ("U1_R","Incisal central superior (lado derecho)"),
 ("U1_L","Incisal central superior (lado izquierdo)"),
 ("L1_R","Incisal central inferior (lado derecho)"),
 ("L1_L","Incisal central inferior (lado izquierdo)"),
]
POINT_LABELS=dict(POINTS)
LINE_PAIRS=[
 ("Cd-Go derecha","Cd_R","Go_R"),("Cd-Go izquierda","Cd_L","Go_L"),
 ("Go-Kr derecha","Go_R","Kr_R"),("Go-Kr izquierda","Go_L","Kr_L"),
 ("Cd-Kr derecha","Cd_R","Kr_R"),("Cd-Kr izquierda","Cd_L","Kr_L"),
 ("Cd-U1 superior derecha","Cd_R","U1_R"),("Cd-U1 superior izquierda","Cd_L","U1_L"),
 ("Cd-L1 inferior derecha","Cd_R","L1_R"),("Cd-L1 inferior izquierda","Cd_L","L1_L"),
 ("Go a línea media derecha","Go_R","M_inf"),("Go a línea media izquierda","Go_L","M_inf"),
 ("Cd a línea media derecha","Cd_R","M_sup"),("Cd a línea media izquierda","Cd_L","M_sup"),
]
class LevandoskiCanvas(QGraphicsView):
 point_clicked=Signal(float,float)
 def __init__(self,parent=None):
  super().__init__(parent); self.scene=QGraphicsScene(self); self.setScene(self.scene)
  self.setBackgroundBrush(QColor("#22262e")); self.image_item=None; self.pix=None
  self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
  self.annotation_items=[]
 def show_image(self,image):
  from .imaging import load_image
  from PySide6.QtGui import QPixmap
  if isinstance(image,str):
   self.pix=QPixmap(image)
  else:
   self.pix=QPixmap.fromImage(image)
  self.scene.clear(); self.image_item=self.scene.addPixmap(self.pix)
  self.scene.setSceneRect(self.image_item.boundingRect())
  self.fitInView(self.scene.sceneRect(),Qt.AspectRatioMode.KeepAspectRatio)
 def draw_marks(self,points):
  for item in self.annotation_items:
   self.scene.removeItem(item)
  self.annotation_items=[]
  if not self.image_item:return
  pen=QPen(QColor("#28c5c2"),2)
  for _,a,b in LINE_PAIRS:
   if a in points and b in points:
    line=self.scene.addLine(points[a][0],points[a][1],points[b][0],points[b][1],pen); line.setZValue(4); self.annotation_items.append(line)
  for key,(x,y) in points.items():
   dot=self.scene.addEllipse(x-5,y-5,10,10,QPen(QColor("#ff9f43"),2),QColor("#ffffff"));dot.setZValue(8)
   label=self.scene.addText(key);label.setDefaultTextColor(QColor("#ffffff"));label.setPos(x+8,y-18);label.setZValue(9)
   self.annotation_items.extend([dot,label])
 def mousePressEvent(self,event):
  if event.button()==Qt.MouseButton.LeftButton and self.active_point:
   p=self.mapToScene(event.position().toPoint())
   if self.scene.sceneRect().contains(p):
    self.point_clicked.emit(p.x(),p.y());event.accept();return
  super().mousePressEvent(event)
 def set_point_mode(self,enabled):
  self.active_point=enabled
  self.setDragMode(QGraphicsView.DragMode.NoDrag if enabled else QGraphicsView.DragMode.ScrollHandDrag)
 def wheelEvent(self,event):
  if self.pix:
   self.scale(1.15 if event.angleDelta().y()>0 else 1/1.15,1.15 if event.angleDelta().y()>0 else 1/1.15);event.accept()
  else:super().wheelEvent(event)

def _dist(a,b):return math.hypot(b[0]-a[0],b[1]-a[1])
class LevandoskiDialog(QDialog):
 def __init__(self,image_path=None,existing=None,parent=None):
  super().__init__(parent); self.existing=existing or {}; vals=self.existing.get("values",{})
  self.points={k:tuple(v) for k,v in vals.get("Puntos",{}).items() if isinstance(v,(list,tuple)) and len(v)==2}
  self.scale=float(vals.get("px/mm")) if vals.get("px/mm") else None
  self.calibration_mm=float(vals.get("Calibración mm")) if vals.get("Calibración mm") else None
  self.calibration_pts={k:tuple(v) for k,v in vals.get("Calibración puntos",{}).items()}
  self._cal=[]; self.setWindowTitle("AVIS · Análisis panorámico de Levandoski");self.resize(1440,900);self.setMinimumSize(1050,700)
  self.canvas=LevandoskiCanvas();self.canvas.setMinimumSize(600,500);self.canvas.point_clicked.connect(self.on_click)
  self.status=QComboBox();self.status.addItems(["Pendiente","En proceso","Completo"]);self.status.setCurrentText(self.existing.get("status","Pendiente"))
  self.point_select=QComboBox();self.point_select.addItem("Selecciona punto anatómico","")
  for k,label in POINTS:self.point_select.addItem(f"{k} · {label}",k)
  self.place=QPushButton("Colocar / corregir punto");self.place.clicked.connect(self.activate)
  self.delete=QPushButton("Eliminar punto");self.delete.clicked.connect(self.remove)
  self.calibrate=QPushButton("Calibrar escala");self.calibrate.clicked.connect(self.begin_calibration)
  self.clear=QPushButton("Limpiar puntos");self.clear.clicked.connect(self.clear_points)
  self.status_text=QLabel("Selecciona un punto, pulsa colocar y haz clic en la radiografía. Rueda para zoom; arrastra para desplazarte.");self.status_text.setWordWrap(True)
  if image_path:
   try:
    from .imaging import load_image
    self.canvas.show_image(load_image(image_path))
   except Exception as e:self.status_text.setText(f"No se pudo abrir la panorámica: {e}")
  else:self.status_text.setText("No se encontró panorámica cargada para este expediente.")
  self.progress=QLabel();self.scale_info=QLabel()
  self.table=QTableWidget(0,4);self.table.setHorizontalHeaderLabels(["Medición","Derecha (px/mm)","Izquierda (px/mm)","Diferencia"])
  self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch);self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
  self.obs=QTextEdit(self.existing.get("observations",""));self.obs.setMaximumHeight(75)
  self.conclusion=QTextEdit(self.existing.get("conclusion",""));self.conclusion.setMaximumHeight(75)
  left=QVBoxLayout();left.addWidget(QLabel("Panorámica · marca los puntos anatómicos"));left.addWidget(self.canvas,1);left.addWidget(self.status_text)
  leftw=__import__('PySide6.QtWidgets',fromlist=['QWidget']).QWidget();leftw.setLayout(left)
  rightw=__import__('PySide6.QtWidgets',fromlist=['QWidget']).QWidget();right=QVBoxLayout(rightw)
  form=QFormLayout();form.addRow("Estado",self.status);form.addRow("Punto",self.point_select);right.addLayout(form)
  controls=QGridLayout();controls.addWidget(self.place,0,0);controls.addWidget(self.delete,0,1);controls.addWidget(self.calibrate,1,0);controls.addWidget(self.clear,1,1);right.addLayout(controls)
  right.addWidget(self.progress);right.addWidget(self.scale_info);right.addWidget(QLabel("Comparación bilateral (las distancias en mm requieren calibración)"));right.addWidget(self.table,1)
  right.addWidget(QLabel("Observaciones"));right.addWidget(self.obs);right.addWidget(QLabel("Conclusión / interpretación"));right.addWidget(self.conclusion)
  splitter=QSplitter(Qt.Orientation.Horizontal);splitter.addWidget(leftw);splitter.addWidget(rightw);splitter.setStretchFactor(0,3);splitter.setStretchFactor(1,2)
  buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject)
  layout=QVBoxLayout(self);layout.addWidget(QLabel("Coloca los puntos; AVIS genera segmentos y compara lados. Este trazado es educativo y no establece diagnóstico por sí solo."));layout.addWidget(splitter,1);layout.addWidget(buttons)
  self.update_view()
 def activate(self):
  key=self.point_select.currentData()
  if not key:QMessageBox.information(self,"Punto","Selecciona un punto anatómico.");return
  self.canvas.set_point_mode(True);self.status_text.setText("Haz clic para colocar: "+POINT_LABELS[key]);self._active=key
 def on_click(self,x,y):
  if getattr(self,"_active",None):
   self.points[self._active]=(x,y);self.canvas.set_point_mode(False);self._active=None;self.update_view()
   self.status_text.setText("Punto guardado. Selecciona otro o vuelve a colocarlo para corregir.")
   return
  if getattr(self,"_cal_stage",None):
   stage=self._cal_stage
   self.calibration_pts["Cal A" if stage==1 else "Cal B"]=(x,y)
   if stage==1:self._cal_stage=2;self.canvas.set_point_mode(True);self.status_text.setText("Marca el segundo extremo de la distancia conocida.")
   else:
    d=_dist(self.calibration_pts["Cal A"],self.calibration_pts["Cal B"])
    if d>0:
     mm,ok=QInputDialog.getDouble(self,"Calibrar","Distancia real (mm):",10.0,0.01,1000,2)
     if ok:self.scale=d/mm;self.calibration_mm=mm
    self._cal_stage=None;self.canvas.set_point_mode(False);self.update_view()
 def remove(self):
  k=self.point_select.currentData()
  if k:self.points.pop(k,None);self.update_view()
 def clear_points(self):
  if QMessageBox.question(self,"Confirmar","¿Eliminar todos los puntos y calibración?")==QMessageBox.StandardButton.Yes:
   self.points.clear();self.scale=None;self.calibration_mm=None;self.calibration_pts={};self.update_view()
 def begin_calibration(self):
  if not self.canvas.image_item:QMessageBox.warning(self,"Sin imagen","Carga la panorámica primero.");return
  self._cal_stage=1;self.canvas.set_point_mode(True);self.status_text.setText("Marca el primer extremo de una distancia conocida.")
 def update_view(self):
  self.canvas.draw_marks(self.points)
  self.progress.setText(f"Puntos colocados: {len(self.points)}/{len(POINTS)}")
  self.scale_info.setText("Escala calibrada" if self.scale else "Sin calibración: se muestran diferencias en píxeles")
  rows=[]
  for label,a,b in LINE_PAIRS:
   if a in self.points and b in self.points:
    d=_dist(self.points[a],self.points[b]);rows.append((label,d,None if not self.scale else d/self.scale))
  self.table.setRowCount(len(rows))
  # organize bilateral pairs for comparison
  pairs={"Condilion–Gonion":("Cd-Go derecha","Cd-Go izquierda"),"Gonion–Coronion":("Go-Kr derecha","Go-Kr izquierda"),"Condilion–Coronion":("Cd-Kr derecha","Cd-Kr izquierda"),"Condilion–incisal superior":("Cd-U1 superior derecha","Cd-U1 superior izquierda"),"Condilion–incisal inferior":("Cd-L1 inferior derecha","Cd-L1 inferior izquierda"),"Gonion a línea media":("Go a línea media derecha","Go a línea media izquierda"),"Condilion a línea media":("Cd a línea media derecha","Cd a línea media izquierda")}
  row=0
  for title,(right_name,left_name) in pairs.items():
   r=next((v for v in rows if v[0]==right_name),None);l=next((v for v in rows if v[0]==left_name),None)
   vals=[title,"—" if not r else f"{r[1]:.1f} px" if not self.scale else f"{r[2]:.2f} mm","—" if not l else f"{l[1]:.1f} px" if not self.scale else f"{l[2]:.2f} mm","—" if not r or not l else f"{abs(r[1]-l[1]):.1f} px" if not self.scale else f"{abs(r[2]-l[2]):.2f} mm"]
   self.table.setItem(row,0,QTableWidgetItem(vals[0]))
   for col in range(1,4):self.table.setItem(row,col,QTableWidgetItem(vals[col]))
   row+=1
  self.table.resizeRowsToContents()
 def values(self):
  vals={"Puntos":{k:list(v) for k,v in self.points.items()},"px/mm":self.scale,"Calibración mm":self.calibration_mm,"Calibración puntos":{k:list(v) for k,v in self.calibration_pts.items()},"Mediciones calculadas":{}}
  for label,a,b in LINE_PAIRS:
   if a in self.points and b in self.points:
    d=_dist(self.points[a],self.points[b]);vals["Mediciones calculadas"][label]={"px":d,"mm":None if not self.scale else d/self.scale}
  return self.status.currentText(),vals,self.obs.toPlainText().strip(),self.conclusion.toPlainText().strip()
