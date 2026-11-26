"""Análisis fotográfico guiado por puntos, referencias y mediciones."""
import math
from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPen, QPixmap
from PySide6.QtWidgets import (
    QDialog, QGraphicsView, QGraphicsScene, QLabel, QPushButton, QComboBox,
    QVBoxLayout, QHBoxLayout, QSplitter, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialogButtonBox, QTextEdit, QFormLayout, QMessageBox,
    QGroupBox, QGridLayout
)
from .photo_geometry import (
    bilateral_difference, line_angle_difference_degrees,
    line_inclination_degrees, segment_proportions_percent,
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
MIDLINE_FIELDS = {
 "Punta de la nariz": ["Derecha","Centrada","Izquierda"],
 "Filtro": ["Derecha","Centrado","Izquierda"],
 "Mentón": ["Derecha","Centrado","Izquierda"],
 "Línea media incisivos superiores": ["Derecha","Centrada","Izquierda"],
 "Línea media incisivos inferiores": ["Derecha","Centrada","Izquierda"]
}
LEVEL_FIELDS = {
 "Ojos · desviación": ["Derecha","Centrada","Izquierda"],
 "Ojos · inclinación": ["Arriba","Abajo","Sin inclinación"],
 "Caninos superiores · desviación": ["Derecha","Centrados","Izquierda"],
 "Caninos superiores · inclinación": ["Arriba","Abajo","Sin inclinación"],
 "Caninos inferiores · desviación": ["Derecha","Centrados","Izquierda"],
 "Caninos inferiores · inclinación": ["Arriba","Abajo","Sin inclinación"],
 "Cuerpo mandibular · desviación": ["Derecha","Centrado","Izquierda"],
 "Cuerpo mandibular · inclinación": ["Arriba","Abajo","Sin inclinación"],
 "Nivel mentoniano · desviación": ["Derecha","Centrado","Izquierda"],
 "Nivel mentoniano · inclinación": ["Arriba","Abajo","Sin inclinación"]
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

PHOTO_GUIDES = {
 "extra_frontal": "FOTOGRAFÍA REQUERIDA · FRONTAL EN REPOSO. Rostro de frente, cabeza en posición natural, mirada al frente y labios relajados, sin sonreír. Cabello recogido, frente completamente despejada y ambas orejas descubiertas. Iluminación uniforme y fondo neutro.",
 "extra_profile": "FOTOGRAFÍA REQUERIDA · PERFIL LATERAL EN REPOSO. Mantener siempre el mismo lado, cabeza en posición natural, mirada al frente y labios relajados. Cabello recogido, frente despejada y oreja del lado fotografiado descubierta. Deben verse nariz, labios, mentón y cuello.",
 "extra_smiling": "FOTOGRAFÍA REQUERIDA · FRONTAL SONRIENDO. Sonrisa amplia y natural, mostrando dientes y encía visible. Rostro de frente, cabeza sin inclinación, mirada al frente, cabello recogido, frente despejada y ambas orejas descubiertas. Deben verse ambas comisuras."
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
  # En sonrisa se dibujan las dos referencias que se comparan.
  for a,b in (("PUP_R","PUP_L"),("LC_R","LC_L")):
   if a in points and b in points:
    line=self.scene_obj.addLine(points[a][0],points[a][1],points[b][0],points[b][1],pen)
    line.setZValue(4); self.marks.append(line)
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
  self.results=QTableWidget(0,3); self.results.setHorizontalHeaderLabels(["Medición","Resultado","Referencia / comparación"])
  self.results.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
  self.observations=QTextEdit(self.existing.get("observations","")); self.observations.setMaximumHeight(65)
  self.conclusion=QTextEdit(self.existing.get("conclusion","")); self.conclusion.setMaximumHeight(65)
  self.fields={}
  extra=QWidget(); grid=QGridLayout(extra); grid.setContentsMargins(0,0,0,0)
  choices=(SMILE_FIELDS if self.cfg["formula"]=="smile" else
           CONTOUR_FIELDS if self.cfg["formula"]=="contour" else
           MIDLINE_FIELDS if self.cfg["formula"]=="midlines" else
           LEVEL_FIELDS if self.cfg["formula"]=="levels" else {})
  for i,(label,opts) in enumerate(choices.items()):
   cb=QComboBox(); cb.addItems(["Sin evaluar"]+opts); cb.setCurrentText(self.saved.get("Evaluación visual",{}).get(label,"Sin evaluar"))
   cb.currentTextChanged.connect(self.update_results); self.fields[label]=cb
   grid.addWidget(QLabel(label),i//2,(i%2)*2); grid.addWidget(cb,i//2,(i%2)*2+1)
  extra_box=QGroupBox("Criterios visuales"); extra_box.setLayout(grid)
  if self.cfg["formula"]=="smile":
   self.smile_hint=QLabel(
    "Simetría: marca el centro de cada pupila y ambas comisuras. "
    "Se trazan la línea bipupilar y la línea comisural; se calcula la diferencia angular. "
    "La clasificación clínica se registra en el criterio visual."
   )
   self.smile_hint.setWordWrap(True)
   grid.addWidget(self.smile_hint, len(choices)//2+1, 0, 1, 4)
  left=QVBoxLayout()
  guide=QLabel(PHOTO_GUIDES[self.cfg["slot"]]); guide.setWordWrap(True)
  guide.setStyleSheet("background:#eee8f5;color:#48263F;padding:10px;border-radius:6px;font-weight:600")
  left.addWidget(guide)
  left.addWidget(QLabel("Selecciona un punto, activa la colocación y haz clic sobre la fotografía. Rueda: zoom · arrastrar: desplazamiento."))
  row=QHBoxLayout(); row.addWidget(self.point_select,2); row.addWidget(self.place); row.addWidget(self.delete); left.addLayout(row)
  left.addWidget(self.canvas,1)
  right=QVBoxLayout(); form=QFormLayout(); form.addRow("Estado",self.status); right.addLayout(form)
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
 def distance(self,a,b):
  return self.distance_px(a,b)
 def vertical_distance(self,a,b):
  if a not in self.points or b not in self.points:return None
  return abs(self.points[b][1]-self.points[a][1])
 def horizontal_distance(self,a,b):
  if a not in self.points or b not in self.points:return None
  return abs(self.points[b][0]-self.points[a][0])
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
  rows=[]; formula=self.cfg["formula"]
  if formula in ("frontal","profile"):
   for label,a,b in self.cfg["measures"]:
    d=self.vertical_distance(a,b)
    self.add_result(rows,label,f"{d:.2f} px" if d is not None else "Pendiente",
                    "Distancia relativa en píxeles de la fotografía")
   total_nm=self.vertical_distance("N","Me")
   ns=self.vertical_distance("N","Sn"); sm=self.vertical_distance("Sn","Me")
   if total_nm and ns is not None and sm is not None:
    p1=ns/total_nm*100;p2=sm/total_nm*100
    self.add_result(rows,"N–Sn (%)",f"{p1:.1f} %","Proporción vertical dentro de N–Me")
    self.add_result(rows,"Sn–Me (%)",f"{p2:.1f} %","Proporción vertical dentro de N–Me")
   thirds=(self.vertical_distance("Tr","Of"),
           self.vertical_distance("Of","Sn"),
           self.vertical_distance("Sn","Me"))
   if all(value is not None for value in thirds):
    percentages=segment_proportions_percent(thirds)
    if percentages is not None:
     for label,value in zip(("Tercio superior (%)","Tercio medio (%)","Tercio inferior (%)"),percentages):
      self.add_result(rows,label,f"{value:.1f} %","Proporción de la suma de los tres tercios Tr–Me")
   if all(k in self.points for k in ("Sn","Sts","Sti","Me")):
    st_y=(self.points["Sts"][1]+self.points["Sti"][1])/2
    sn_y=self.points["Sn"][1]; me_y=self.points["Me"][1]
    snst=abs(st_y-sn_y); stme=abs(me_y-st_y)
    if snst+stme:
     self.add_result(rows,"Sn–St (%)",f"{snst/(snst+stme)*100:.1f} %","Proporción relativa de la imagen")
     self.add_result(rows,"St–Me (%)",f"{stme/(snst+stme)*100:.1f} %","Proporción relativa de la imagen")
  elif formula=="smile":
   required=("PUP_R","PUP_L","LC_R","LC_L")
   if all(key in self.points for key in required):
    difference=line_angle_difference_degrees(
     self.points["PUP_R"],self.points["PUP_L"],
     self.points["LC_R"],self.points["LC_L"],
    )
    if difference is not None:
     self.add_result(rows,"Diferencia angular bipupilar–comisural",f"{difference:.2f}°",
                     "Ángulo agudo entre ambas líneas (0° paralelas; 90° perpendiculares); no es una clasificación clínica")
  elif formula=="midlines":
   # Eje de referencia: centro del puente nasal (punto medio intercantal)
   # y centro del labio superior. La desviación es perpendicular y relativa.
   if all(k in self.points for k in ("ICD","ICI","LS")):
    bridge=((self.points["ICD"][0]+self.points["ICI"][0])/2,
            (self.points["ICD"][1]+self.points["ICI"][1])/2)
    lip=self.points["LS"]
    vx,vy=lip[0]-bridge[0],lip[1]-bridge[1]
    norm=math.hypot(vx,vy)
    if norm:
     for label,key in (("Punta de la nariz","NAR"),("Filtro","LS"),("Mentón","MENT"),
                       ("Línea media incisivos superiores","UIS"),("Línea media incisivos inferiores","LIS")):
      if key in self.points:
       p=self.points[key]
       signed=(vx*(p[1]-bridge[1])-vy*(p[0]-bridge[0]))/norm
       self.add_result(rows,label,f"{signed:+.2f} px",
                       "Desviación perpendicular relativa al eje puente nasal–labio superior")
  elif formula=="levels":
   for label,a,b in self.cfg["measures"]:
    if a in self.points and b in self.points:
     dy=self.points[b][1]-self.points[a][1]
     ang=line_inclination_degrees(self.points[a],self.points[b])
     if ang is not None:
      self.add_result(rows,label,f"{ang:+.2f}°",
                      f"Desnivel relativo {abs(dy):.2f} px; inclinación respecto a la horizontal de la imagen; completar la dirección en evaluación visual")
  elif formula=="powell":
   for label,a,b,c,norm in (("Nasofrontal","G","N","R","115°–130°"),("Mesofacial","N","Pg","Prn","Mujer 30° · Hombre 40°"),("Nasomentón","Prn","Pg","N","120°–132°"),("Mentocervical","N","Pg","C","80°–95°")):
    val=self.angle(a,b,c)
    self.add_result(rows,label,f"{val:.2f}°" if val is not None else "Pendiente",norm)
  elif formula=="projections":
   if "N" in self.points:
    x0=self.points["N"][0]
    for label,key in (("Glabela","G"),("Reborde orbitario","OR"),("Pómulo","MAL"),
                      ("Punto subpupilar","SUBP"),("Base basal","BB"),("Labio superior","LS"),
                      ("Punta nasal","PRN"),("Labio inferior","LI"),("Pogonion","PG")):
     if key in self.points:
      dx=self.points[key][0]-x0
      self.add_result(rows,label,f"{dx:+.2f} px",
                      "Desviación horizontal relativa respecto a N; no representa milímetros")
  elif formula=="symmetry":
   for label,a,b in self.cfg["measures"]:
    d=self.distance(a,b)
    self.add_result(rows,label,f"{d:.2f} px" if d is not None else "Pendiente",
                    "Distancia relativa en la misma fotografía; no equivale a milímetros")
   for label,right_pair,left_pair in (
    ("Diferencia entre quintos laterales derecho–izquierdo",("F_R","CL_R"),("CL_L","F_L")),
    ("Diferencia entre quintos oculares derecho–izquierdo",("CL_R","CM_R"),("CM_L","CL_L")),
   ):
    comparison=bilateral_difference(self.distance(*right_pair),self.distance(*left_pair))
    if comparison is not None:
     diff,percent=comparison
     value=f"{diff:.2f} px"+(f" ({percent:.1f} % relativo)" if percent is not None else "")
     self.add_result(rows,label,value,
                     "Diferencia absoluta entre longitudes bilaterales marcadas; no constituye diagnóstico por sí sola")
  elif formula=="contour":
   for label,a,b in self.cfg["measures"]:
    d=self.horizontal_distance(a,b)
    self.add_result(rows,label,f"{d:.2f} px" if d is not None else "Pendiente",
                    "Separación horizontal relativa en la fotografía; no equivale a milímetros")
   for label,right_pair,left_pair in (
    ("Diferencia bilateral cigomático–ángulo mandibular",("ZG_R","MA_R"),("ZG_L","MA_L")),
    ("Diferencia bilateral ángulo–cuerpo mandibular",("MA_R","CB_R"),("MA_L","CB_L")),
    ("Diferencia bilateral cuerpo mandibular–mentón",("CB_R","ME_R"),("CB_L","ME_L")),
   ):
    comparison=bilateral_difference(self.distance(*right_pair),self.distance(*left_pair))
    if comparison is not None:
     diff,percent=comparison
     value=f"{diff:.2f} px"+(f" ({percent:.1f} % relativo)" if percent is not None else "")
     self.add_result(rows,label,value,
                     "Diferencia absoluta entre longitudes bilaterales marcadas; no constituye diagnóstico por sí sola")
  self.results.setRowCount(len(rows)); self.results.clearContents()
  for r,row in enumerate(rows):
   for c,val in enumerate(row):self.results.setItem(r,c,QTableWidgetItem(str(val)))
 def save(self):
  if not self.points and not any(x.currentText()!="Sin evaluar" for x in self.fields.values()):
   QMessageBox.warning(self,"Análisis vacío","Coloca los puntos anatómicos o registra los criterios visuales.");return
  vals={"Puntos":self.points,"Unidad":"px_relativos",
   "Mediciones":{self.results.item(r,0).text():{"resultado":self.results.item(r,1).text(),"referencia":self.results.item(r,2).text()}
    for r in range(self.results.rowCount())},
   "Evaluación visual":{k:v.currentText() for k,v in self.fields.items()}}
  self.accepted_values=vals; self.accept()
 def values(self):
  return self.status.currentText(),self.accepted_values,self.observations.toPlainText().strip(),self.conclusion.toPlainText().strip()
