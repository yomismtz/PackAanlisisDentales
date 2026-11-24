"""Análisis fotográfico guiado por puntos, referencias y mediciones."""
import math
from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPen, QPixmap
from PySide6.QtWidgets import (
    QDialog, QGraphicsView, QGraphicsScene, QLabel, QPushButton, QComboBox,
    QVBoxLayout, QHBoxLayout, QSplitter, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialogButtonBox, QTextEdit, QFormLayout, QMessageBox,
    QLineEdit, QGroupBox, QGridLayout
)

CONFIG = {
 "facial_frontal": {
  "title":"Análisis facial frontal vertical","slot":"extra_frontal",
  "points":[("Tr","Tr · implantación del cabello"),("Of","Of · borde superior de cejas"),
   ("N","N · nasion"),("Sn","Sn · subnasal"),("Me","Me · mentón"),("Sts","Stomion superior"),("Sti","Stomion inferior")],
  "measures":[("Tercio superior Tr–Of","Tr","Of"),("Tercio medio Of–Sn","Of","Sn"),("Tercio inferior Sn–Me","Sn","Me"),
   ("N–Sn","N","Sn"),("Sn–Me","Sn","Me"),("N–Me","N","Me"),("Sn–St","Sn","Sts"),("St–Me","Sti","Me")],
  "formula":"frontal"
 },
 "facial_profile": {
  "title":"Análisis facial sagital vertical","slot":"extra_profile",
  "points":[("Tr","Tr · implantación del cabello"),("Of","Of · borde superior de cejas"),
   ("N","N · nasion blando"),("Sn","Sn · subnasal"),("Me","Me · mentón"),("Sts","Stomion superior"),("Sti","Stomion inferior")],
  "measures":[("Tercio superior Tr–Of","Tr","Of"),("Tercio medio Of–Sn","Of","Sn"),("Tercio inferior Sn–Me","Sn","Me"),
   ("N–Sn","N","Sn"),("Sn–Me","Sn","Me"),("N–Me","N","Me"),("Sn–St","Sn","Sts"),("St–Me","Sti","Me")],
  "formula":"profile"
 },
 "facial_midlines": {
  "title":"Análisis de líneas medias","slot":"extra_frontal",
  "points":[("ICD","Canto interno derecho"),("ICI","Canto interno izquierdo"),("LS","Centro del labio superior / filtro"),
   ("NAR","Punta nasal"),("MENT","Centro del mentón"),("UIS","Línea media incisivos superiores"),("LIS","Línea media incisivos inferiores")],
  "measures":[("Distancia intercantal","ICD","ICI")],"formula":"midlines"
 },
 "facial_levels": {
  "title":"Análisis de niveles faciales","slot":"extra_frontal",
  "points":[("OD","Punto ocular derecho"),("OI","Punto ocular izquierdo"),("CD","Canino superior derecho"),
   ("CI","Canino superior izquierdo"),("ID","Canino inferior derecho"),("II","Canino inferior izquierdo"),
   ("MD","Cuerpo mandibular derecho"),("MI","Cuerpo mandibular izquierdo"),("MTD","Mentón derecho"),("MTI","Mentón izquierdo")],
  "measures":[("Nivel ocular","OD","OI"),("Nivel caninos superiores","CD","CI"),("Nivel caninos inferiores","ID","II"),
   ("Nivel mandibular","MD","MI"),("Nivel mentoniano","MTD","MTI")],"formula":"levels"
 },
 "facial_contour": {
  "title":"Análisis de contorno facial","slot":"extra_frontal",
  "points":[("ZG_R","Punto cigomático derecho"),("ZG_L","Punto cigomático izquierdo"),
   ("MA_R","Ángulo mandibular derecho"),("MA_L","Ángulo mandibular izquierdo"),
   ("CB_R","Cuerpo mandibular derecho"),("CB_L","Cuerpo mandibular izquierdo"),
   ("ME_R","Mentón derecho"),("ME_L","Mentón izquierdo"),("AL_R","Ala nasal derecha"),("AL_L","Ala nasal izquierda")],
  "measures":[("Ancho cigomático","ZG_R","ZG_L"),("Ancho mandibular","CB_R","CB_L"),("Ancho nasal","AL_R","AL_L")],
  "formula":"contour"
 },
 "powell": {
  "title":"Análisis de Powell","slot":"extra_profile",
  "points":[("G","Glabela"),("N","Nasion blando"),("R","Radix nasal"),("Prn","Punta nasal / pronasale"),
   ("Pg","Pogonion blando"),("C","Punto cervical"),("H","Punto horizontal cervical")],
  "measures":[],"formula":"powell"
 },
 "smile": {
  "title":"Análisis de sonrisa","slot":"extra_smiling",
  "points":[("LC_R","Comisura derecha"),("LC_L","Comisura izquierda"),("PUP_R","Centro pupilar derecho"),
   ("PUP_L","Centro pupilar izquierdo"),("CU_R","Punta de canino superior derecho"),
   ("CU_L","Punta de canino superior izquierdo"),("ST","Centro del labio superior"),
   ("LI","Centro del labio inferior"),("D11","Borde incisal central superior derecho"),
   ("D21","Borde incisal central superior izquierdo")],
  "measures":[],"formula":"smile"
 },
 "facial_projections": {
  "title":"Análisis de proyecciones","slot":"extra_profile",
  "points":[("N","Nasion blando · referencia TVL"),("G","Glabela"),("OR","Reborde orbitario"),
   ("MAL","Pómulo / malar"),("SUBP","Punto subpupilar"),("BB","Base basal"),("LS","Labio superior"),
   ("PRN","Punta nasal"),("LI","Labio inferior"),("PG","Pogonion blando")],
  "measures":[],"formula":"projections"
 },
 "facial_symmetry": {
  "title":"Análisis de simetrías horizontales","slot":"extra_frontal",
  "points":[("F_R","Contorno facial lateral derecho"),("CL_R","Canto lateral derecho"),("CM_R","Canto medial derecho"),
   ("CM_L","Canto medial izquierdo"),("CL_L","Canto lateral izquierdo"),("F_L","Contorno facial lateral izquierdo"),
   ("AL_R","Ala nasal derecha"),("AL_L","Ala nasal izquierda"),("PU_R","Centro pupilar derecho"),
   ("PU_L","Centro pupilar izquierdo"),("COM_R","Comisura derecha"),("COM_L","Comisura izquierda")],
  "measures":[("Quinto lateral derecho","F_R","CL_R"),("Quinto ocular derecho","CL_R","CM_R"),
   ("Quinto central","CM_R","CM_L"),("Quinto ocular izquierdo","CM_L","CL_L"),("Quinto lateral izquierdo","CL_L","F_L"),
   ("Ancho nasal","AL_R","AL_L"),("Ancho bucal","COM_R","COM_L"),("Distancia intercantal","CM_R","CM_L")],
  "formula":"symmetry"
 }
}
SMILE_FIELDS = {
 "Línea de los labios":["Alta","Media","Baja"],
 "Arco de sonrisa":["Consonante","Paralelo","No consonante"],
 "Curvatura del labio superior":["Alta","Recta","Baja"],
 "Espacios negativos":["Presentes","Ausentes"],
 "Simetría de sonrisa":["Simétrica","Asimétrica"],
 "Plano oclusal frontal":["Aceptable","No aceptable"],
 "Componente dental":["Aceptable","No aceptable"],
 "Componente gingival":["Aceptable","No aceptable"]
}
CONTOUR_FIELDS = {
 "Forma facial":["Redonda","Cuadrada","Alargada"],
 "Tamaño facial":["Estrecho","Ancho","Normal"],
 "Cigomático derecho":["Grande","Ancho","Normal","Estrecho"],
 "Cigomático izquierdo":["Grande","Ancho","Normal","Estrecho"],
 "Ángulo mandibular derecho":["Grande","Ancho","Normal","Estrecho"],
 "Ángulo mandibular izquierdo":["Grande","Ancho","Normal","Estrecho"],
 "Cuerpo mandibular derecho":["Grande","Ancho","Normal","Estrecho"],
 "Cuerpo mandibular izquierdo":["Grande","Ancho","Normal","Estrecho"],
 "Mentón derecho":["Grande","Ancho","Normal","Estrecho"],
 "Mentón izquierdo":["Grande","Ancho","Normal","Estrecho"],
 "Base alar derecha":["Grande","Ancha","Normal","Estrecha"],
 "Base alar izquierda":["Grande","Ancha","Normal","Estrecha"]
}

class PhotoCanvas(QGraphicsView):
 point_clicked=Signal(float,float)
 def __init__(self,parent=None):
  super().__init__(parent); self.scene_obj=QGraphicsScene(self); self.setScene(self.scene_obj)
  self.setBackgroundBrush(QColor("#22262e")); self.pixmap_item=None; self.active=False; self.marks=[]
  self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
 def show_image(self,path):
  self.scene_obj.clear(); self.marks=[]; self.pixmap_item=None
  if path and Path(path).is_file():
   pix=QPixmap(str(path))
   if not pix.isNull():
    self.pixmap_item=self.scene_obj.addPixmap(pix); self.scene_obj.setSceneRect(self.pixmap_item.boundingRect())
    self.resetTransform(); self.fitInView(self.scene_obj.sceneRect(),Qt.AspectRatioMode.KeepAspectRatio)
 def draw_points(self,points):
  for item in self.marks:self.scene_obj.removeItem(item)
  self.marks=[]
  if self.pixmap_item is None:return
  pen=QPen(QColor("#22B8B0"),2)
  for key,(x,y) in points.items():
   dot=self.scene_obj.addEllipse(x-5,y-5,10,10,pen,QColor("#FFFFFF"))
   label=self.scene_obj.addText(key); label.setDefaultTextColor(QColor("#FFFFFF")); label.setPos(x+7,y-18)
   self.marks.extend([dot,label])
  if "N" in points and self.parent() is not None:
   pass
 def set_point_mode(self,enabled):
  self.active=enabled; self.setDragMode(QGraphicsView.DragMode.NoDrag if enabled else QGraphicsView.DragMode.ScrollHandDrag)
 def mousePressEvent(self,event):
  if self.active and event.button()==Qt.MouseButton.LeftButton:
   p=self.mapToScene(event.position().toPoint())
   if self.scene_obj.sceneRect().contains(p):
    self.point_clicked.emit(p.x(),p.y()); event.accept(); return
  super().mousePressEvent(event)
 def wheelEvent(self,event):
  if self.pixmap_item:
   factor=1.15 if event.angleDelta().y()>0 else 1/1.15; self.scale(factor,factor); event.accept()
  else:super().wheelEvent(event)

class PhotoAnalysisDialog(QDialog):
 def __init__(self,key,image_path,existing=None,patient_sex="",parent=None):
  super().__init__(parent); self.key=key; self.cfg=CONFIG[key]; self.existing=existing or {}
  self.saved=self.existing.get("values",{}); self.points={k:tuple(v) for k,v in self.saved.get("Puntos",{}).items()}
  self.setWindowTitle("AVIS · "+self.cfg["title"]); self.resize(1420,900); self.setMinimumSize(1080,700)
  self.canvas=PhotoCanvas(); self.canvas.show_image(image_path); self.canvas.point_clicked.connect(self.place_point)
  self.status=QComboBox(); self.status.addItems(["Pendiente","En proceso","Completo"]); self.status.setCurrentText(self.existing.get("status","Pendiente"))
  self.point_select=QComboBox(); self.point_select.addItem("Selecciona el punto anatómico","")
  for code,label in self.cfg["points"]:self.point_select.addItem(f"{code} · {label}",code)
  self.place=QPushButton("Colocar / corregir punto"); self.place.clicked.connect(self.activate_point)
  self.delete=QPushButton("Eliminar punto"); self.delete.clicked.connect(self.delete_point)
  self.scale=QLineEdit(str(self.saved.get("Calibración mm/px",""))); self.scale.setPlaceholderText("mm por píxel (si aplica)")
  self.scale.textChanged.connect(self.update_results)
  self.results=QTableWidget(0,3); self.results.setHorizontalHeaderLabels(["Medición","Resultado","Referencia / comparación"])
  self.results.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
  self.observations=QTextEdit(self.existing.get("observations","")); self.observations.setMaximumHeight(65)
  self.conclusion=QTextEdit(self.existing.get("conclusion","")); self.conclusion.setMaximumHeight(65)
  self.fields={}
  extra=QWidget(); grid=QGridLayout(extra); grid.setContentsMargins(0,0,0,0)
  choices=SMILE_FIELDS if self.cfg["formula"]=="smile" else CONTOUR_FIELDS if self.cfg["formula"]=="contour" else {}
  for i,(label,opts) in enumerate(choices.items()):
   cb=QComboBox(); cb.addItems(["Sin evaluar"]+opts); cb.setCurrentText(self.saved.get("Evaluación visual",{}).get(label,"Sin evaluar"))
   cb.currentTextChanged.connect(self.update_results); self.fields[label]=cb
   grid.addWidget(QLabel(label),i//2,(i%2)*2); grid.addWidget(cb,i//2,(i%2)*2+1)
  extra_box=QGroupBox("Evaluación visual · sin cálculo automático"); extra_box.setLayout(grid)
  left=QVBoxLayout(); left.addWidget(QLabel("Selecciona un punto, activa la colocación y haz clic sobre la fotografía. Rueda: zoom · arrastrar: desplazamiento."))
  row=QHBoxLayout(); row.addWidget(self.point_select,2); row.addWidget(self.place); row.addWidget(self.delete); left.addLayout(row)
  left.addWidget(self.canvas,1)
  right=QVBoxLayout(); form=QFormLayout(); form.addRow("Estado",self.status); form.addRow("Calibración (mm/px)",self.scale); right.addLayout(form)
  right.addWidget(QLabel("Mediciones, proporciones y cálculos")); right.addWidget(self.results,1)
  if choices:right.addWidget(extra_box)
  right.addWidget(QLabel("Observaciones")); right.addWidget(self.observations); right.addWidget(QLabel("Conclusión profesional")); right.addWidget(self.conclusion)
  split=QSplitter(Qt.Orientation.Horizontal); lw=QWidget(); lw.setLayout(left); rw=QWidget(); rw.setLayout(right)
  split.addWidget(lw); split.addWidget(rw); split.setStretchFactor(0,3); split.setStretchFactor(1,2)
  buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel)
  buttons.accepted.connect(self.save); buttons.rejected.connect(self.reject)
  layout=QVBoxLayout(self); layout.addWidget(split,1); layout.addWidget(buttons)
  self.canvas.draw_points(self.points); self.update_results()
 def activate_point(self):
  code=self.point_select.currentData()
  if not code:QMessageBox.information(self,"Punto","Selecciona primero el punto anatómico.");return
  if self.canvas.pixmap_item is None:QMessageBox.warning(self,"Fotografía requerida","Carga la fotografía correspondiente en el expediente.");return
  self.active_code=code; self.canvas.set_point_mode(True)
 def place_point(self,x,y):
  code=getattr(self,"active_code",None)
  if not code:return
  self.points[code]=(x,y); self.canvas.set_point_mode(False); self.canvas.draw_points(self.points); self.update_results()
 def delete_point(self):
  code=self.point_select.currentData()
  if code:self.points.pop(code,None); self.canvas.draw_points(self.points); self.update_results()
 def distance_px(self,a,b):
  if a not in self.points or b not in self.points:return None
  return math.hypot(self.points[b][0]-self.points[a][0],self.points[b][1]-self.points[a][1])
 def scale_value(self):
  try:
   x=float(self.scale.text().replace(",",".")); return x if x>0 else None
  except ValueError:return None
 def distance(self,a,b):
  d=self.distance_px(a,b); s=self.scale_value()
  return d*s if d is not None and s is not None else None
 def angle(self,a,b,c):
  if any(x not in self.points for x in (a,b,c)):return None
  p,q,r=self.points[a],self.points[b],self.points[c]
  v=(p[0]-q[0],p[1]-q[1]); w=(r[0]-q[0],r[1]-q[1])
  den=math.hypot(*v)*math.hypot(*w)
  if not den:return None
  return math.degrees(math.acos(max(-1,min(1,(v[0]*w[0]+v[1]*w[1])/den))))
 def add_result(self,rows,label,value,reference=""):
  rows.append((label,value,reference))
 def update_results(self,*args):
  rows=[]; formula=self.cfg["formula"]; scale=self.scale_value()
  if formula in ("frontal","profile"):
   for label,a,b in self.cfg["measures"]:
    d=self.distance(a,b)
    self.add_result(rows,label,f"{d:.2f} mm" if d is not None else "Pendiente")
   total=self.distance("N","Me")
   ns=self.distance("N","Sn"); sm=self.distance("Sn","Me")
   if total and ns is not None and sm is not None:
    p1=ns/total*100;p2=sm/total*100
    self.add_result(rows,"N–Sn (%)",f"{p1:.1f} %","Ideal 43 %")
    self.add_result(rows,"Sn–Me (%)",f"{p2:.1f} %","Ideal 57 %")
   snst=self.distance("Sn","Sts"); stme=self.distance("Sti","Me")
   if snst is not None and stme is not None and snst+stme:
    self.add_result(rows,"Sn–St (%)",f"{snst/(snst+stme)*100:.1f} %","Referencia 1/3")
    self.add_result(rows,"St–Me (%)",f"{stme/(snst+stme)*100:.1f} %","Referencia 2/3")
   if formula=="profile" and "Sts" in self.points and "Sti" in self.points:
    gap=abs(self.points["Sts"][1]-self.points["Sti"][1])*(scale or 1)
    self.add_result(rows,"Espacio interlabial",f"{gap:.2f} {'mm' if scale else 'px'}","Norma indicada: 0–3 mm")
  elif formula=="midlines":
   if all(k in self.points for k in ("ICD","ICI","LS")):
    xref=(self.points["ICD"][0]+self.points["ICI"][0])/2
    for label,key in (("Punta nasal","NAR"),("Filtro / labio superior","LS"),("Mentón","MENT"),("Incisivos superiores","UIS"),("Incisivos inferiores","LIS")):
     if key in self.points:
      delta=(self.points[key][0]-xref)*(scale or 1)
      self.add_result(rows,label,f"{delta:+.2f} {'mm' if scale else 'px'}","Derecha / izquierda respecto a línea media")
  elif formula=="levels":
   for label,a,b in self.cfg["measures"]:
    if a in self.points and b in self.points:
     dy=(self.points[b][1]-self.points[a][1])*(scale or 1)
     dx=self.points[b][0]-self.points[a][0]
     ang=math.degrees(math.atan2(dy,dx))
     self.add_result(rows,label,f"{ang:.2f}°",f"Desnivel {abs(dy):.2f} {'mm' if scale else 'px'}")
  elif formula=="powell":
   for label,a,b,c,norm in (("Nasofrontal","G","N","R","115°–130°"),("Mesofacial","N","Pg","Prn","Mujer 30° · Hombre 40°"),("Nasomentón","Prn","Pg","N","120°–132°"),("Mentocervical","N","Pg","C","80°–95°")):
    val=self.angle(a,b,c)
    self.add_result(rows,label,f"{val:.2f}°" if val is not None else "Pendiente",norm)
  elif formula=="projections":
   if "N" in self.points:
    x0=self.points["N"][0]
    for label,key,norm in (("Glabela","G","-8.5 mm"),("Reborde orbitario","OR","-18.7 / -22.4 mm"),
     ("Pómulo","MAL","-20.6 / -25.2 mm"),("Punto subpupilar","SUBP","-14.8 / -18.4 mm"),
     ("Base basal","BB","13 / 15 mm"),("Labio superior","LS","3.7 / 3.3 mm"),
     ("Punta nasal","PRN","16.0 / 17.4 mm"),("Labio inferior","LI","-1.9 / -1.0 mm"),("Pogonion","PG","-2.6 / -3.5 mm")):
     if key in self.points:
      dx=(self.points[key][0]-x0)*(scale or 1)
      self.add_result(rows,label,f"{dx:+.2f} {'mm' if scale else 'px'}",norm)
  elif formula=="symmetry":
   for label,a,b in self.cfg["measures"]:
    d=self.distance(a,b)
    self.add_result(rows,label,f"{d:.2f} mm" if d is not None else "Pendiente","Comparar quintos y proporciones")
  elif formula=="contour":
   for label,a,b in self.cfg["measures"]:
    d=self.distance(a,b)
    self.add_result(rows,label,f"{d:.2f} mm" if d is not None else "Pendiente","Comparación bilateral / referencia")
  self.results.setRowCount(len(rows)); self.results.clearContents()
  for r,row in enumerate(rows):
   for c,val in enumerate(row):self.results.setItem(r,c,QTableWidgetItem(str(val)))
 def save(self):
  if not self.points and not any(x.currentText()!="Sin evaluar" for x in self.fields.values()):
   QMessageBox.warning(self,"Análisis vacío","Coloca los puntos anatómicos o registra los criterios visuales.");return
  vals={"Puntos":self.points,"Calibración mm/px":self.scale_value(),
   "Mediciones":{self.results.item(r,0).text():{"resultado":self.results.item(r,1).text(),"referencia":self.results.item(r,2).text()}
    for r in range(self.results.rowCount())},
   "Evaluación visual":{k:v.currentText() for k,v in self.fields.items()}}
  self.accepted_values=vals; self.accept()
 def values(self):
  return self.status.currentText(),self.accepted_values,self.observations.toPlainText().strip(),self.conclusion.toPlainText().strip()
