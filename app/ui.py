"""Interfaz de escritorio para expedientes, captura y análisis odontológicos."""
import mimetypes, tempfile
from pathlib import Path
import cv2
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QImage, QPixmap, QPen, QColor
from PySide6.QtWidgets import *

from .catalog import GROUPS, SLOTS, ANALYSES, analyses_for_slot, CARPAL_STAGES
from .analysis_forms import fields_for
from .database import Database
from .storage import database_path, import_media, save_processed
from . import imaging

STYLE = """
QWidget{font-family:'Segoe UI';font-size:10pt;background:#f4f7fb;color:#213345}
QFrame#Panel,QGroupBox{background:white;border:1px solid #dce4ec;border-radius:10px}
QPushButton{background:#e7eef5;border:1px solid #cdd9e4;border-radius:7px;padding:7px 10px}
QPushButton#Primary{background:#1d668e;color:white;border:0;font-weight:600}
QLineEdit,QTextEdit,QComboBox{background:white;border:1px solid #cbd6e0;border-radius:6px;padding:6px}
QListWidget,QTableWidget{background:white;border:1px solid #dce4ec;border-radius:8px}
QHeaderView::section{background:#edf2f7;padding:6px;border:0;font-weight:600}
"""

def pixmap_from_cv(im):
    if im.ndim == 2:
        h,w=im.shape; q=QImage(im.data,w,h,w,QImage.Format.Format_Grayscale8).copy()
    elif im.shape[2] == 4:
        rgba=cv2.cvtColor(im,cv2.COLOR_BGRA2RGBA); h,w,_=rgba.shape
        q=QImage(rgba.data,w,h,w*4,QImage.Format.Format_RGBA8888).copy()
    else:
        rgb=cv2.cvtColor(im,cv2.COLOR_BGR2RGB); h,w,_=rgb.shape
        q=QImage(rgb.data,w,h,w*3,QImage.Format.Format_RGB888).copy()
    return QPixmap.fromImage(q)

class NewPatient(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle("Nuevo expediente"); self.setMinimumWidth(440)
        self.name=QLineEdit(); self.birth=QLineEdit(); self.birth.setPlaceholderText("AAAA-MM-DD")
        self.sex=QComboBox(); self.sex.addItems(["No especificado","Femenino","Masculino","Otro"])
        self.phone=QLineEdit(); self.email=QLineEdit(); self.notes=QTextEdit(); self.notes.setMaximumHeight(75)
        f=QFormLayout(); f.addRow("Nombre completo *",self.name); f.addRow("Fecha de nacimiento",self.birth)
        f.addRow("Sexo",self.sex); f.addRow("Teléfono",self.phone); f.addRow("Correo",self.email); f.addRow("Notas",self.notes)
        b=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel)
        b.accepted.connect(self.accept); b.rejected.connect(self.reject)
        l=QVBoxLayout(self); l.addLayout(f); l.addWidget(QLabel("Se guardará en la base local de esta computadora.")); l.addWidget(b)
    def values(self):
        sex="" if self.sex.currentIndex()==0 else self.sex.currentText()
        return dict(full_name=self.name.text().strip(),birth_date=self.birth.text().strip(),sex=sex,
                    phone=self.phone.text().strip(),email=self.email.text().strip(),notes=self.notes.toPlainText().strip())
    def accept(self):
        if not self.name.text().strip(): QMessageBox.warning(self,"Dato requerido","Escribe el nombre del paciente."); return
        if self.birth.text().strip():
            from datetime import date
            try: date.fromisoformat(self.birth.text().strip())
            except ValueError: QMessageBox.warning(self,"Fecha inválida","Usa AAAA-MM-DD."); return
        super().accept()

class CameraCapture(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle("Capturar imagen"); self.setMinimumSize(720,540)
        self.capture=None; self.last=None; self.output_path=None
        self.preview=QLabel("Conectando con la cámara…"); self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumSize(640,430); self.preview.setStyleSheet("background:#172532;color:white")
        self.device=QSpinBox(); self.device.setRange(0,5); self.device.setPrefix("Cámara ")
        self.device.valueChanged.connect(self.open_camera)
        self.status=QLabel("Permite el acceso a la cámara en Windows.")
        take=QPushButton("Capturar"); cancel=QPushButton("Cancelar")
        take.clicked.connect(self.take_photo); cancel.clicked.connect(self.reject)
        row=QHBoxLayout(); row.addWidget(self.device); row.addStretch(); row.addWidget(take); row.addWidget(cancel)
        l=QVBoxLayout(self); l.addWidget(self.preview,1); l.addWidget(self.status); l.addLayout(row)
        self.timer=QTimer(self); self.timer.timeout.connect(self.refresh); self.open_camera(0)
    def open_camera(self,index):
        self.timer.stop()
        if self.capture is not None: self.capture.release()
        self.capture=cv2.VideoCapture(index,cv2.CAP_DSHOW if hasattr(cv2,"CAP_DSHOW") else 0)
        if self.capture.isOpened(): self.status.setText(f"Cámara {index} conectada."); self.timer.start(35)
        else: self.status.setText("No se pudo abrir la cámara. Revisa permisos o selecciona otra.")
    def refresh(self):
        ok,frame=self.capture.read() if self.capture else (False,None)
        if ok:
            self.last=frame; self.preview.setPixmap(pixmap_from_cv(frame).scaled(self.preview.size(),Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
    def take_photo(self):
        if self.last is None: QMessageBox.warning(self,"Sin imagen","La cámara aún no entrega una imagen."); return
        path=Path(tempfile.gettempdir())/("pack_capture_"+next(tempfile._get_candidate_names())+".png")
        ok,buf=cv2.imencode(".png",self.last)
        if ok: buf.tofile(str(path)); self.output_path=str(path); self.accept()
    def done(self,result):
        self.timer.stop()
        if self.capture: self.capture.release(); self.capture=None
        super().done(result)

class Canvas(QGraphicsView):
    def __init__(self,parent=None):
        super().__init__(parent); self.scene_obj=QGraphicsScene(self); self.setScene(self.scene_obj)
        self.setBackgroundBrush(QColor("#111a24")); self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.pix=None; self.corners=[]
    def show_image(self,im):
        self.scene_obj.clear(); self.corners=[]
        self.pix=self.scene_obj.addPixmap(pixmap_from_cv(im)); self.scene_obj.setSceneRect(self.pix.boundingRect())
        self.fitInView(self.scene_obj.sceneRect(),Qt.AspectRatioMode.KeepAspectRatio)
    def choose_corners(self):
        self.corners=[]
        for item in list(self.scene_obj.items()):
            if item is not self.pix: self.scene_obj.removeItem(item)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
    def mousePressEvent(self,event):
        if self.pix and self.dragMode()==QGraphicsView.DragMode.NoDrag and event.button()==Qt.MouseButton.LeftButton:
            p=self.mapToScene(event.position().toPoint())
            if self.scene_obj.sceneRect().contains(p) and len(self.corners)<4:
                self.corners.append((p.x(),p.y()))
                dot=self.scene_obj.addEllipse(p.x()-7,p.y()-7,14,14,QPen(QColor("#ffae42"),3))
                dot.setBrush(QColor("#ffae42"))
                self.scene_obj.addText(str(len(self.corners))).setPos(p.x()+8,p.y()+8)
                if len(self.corners)==4: self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
                return
        super().mousePressEvent(event)

class ImageEditor(QDialog):
    def __init__(self,pid,path,allow_background,parent=None):
        super().__init__(parent); self.pid=pid; self.path=path; self.saved_path=None
        self.setWindowTitle("Editar copia de la imagen"); self.resize(1000,750)
        self.original=imaging.load_image(path); self.canvas=Canvas(); self.canvas.show_image(self.original)
        self.brightness=QSlider(Qt.Orientation.Horizontal); self.brightness.setRange(-100,100)
        self.contrast=QSlider(Qt.Orientation.Horizontal); self.contrast.setRange(50,200); self.contrast.setValue(100)
        self.sharp=QSlider(Qt.Orientation.Horizontal); self.sharp.setRange(50,200); self.sharp.setValue(100)
        self.bg=QPushButton("Eliminar fondo"); self.bg.setEnabled(allow_background)
        self.scan=QPushButton("Marcar 4 esquinas"); self.rectify=QPushButton("Rectificar")
        self.save=QPushButton("Guardar copia"); self.save.setObjectName("Primary")
        self.status=QLabel("El original se conserva. Los ajustes se guardan como una copia derivada.")
        self.brightness.valueChanged.connect(self.update_preview); self.contrast.valueChanged.connect(self.update_preview); self.sharp.valueChanged.connect(self.update_preview)
        self.scan.clicked.connect(self.canvas.choose_corners); self.rectify.clicked.connect(self.rectify_image)
        self.bg.clicked.connect(self.remove_bg); self.save.clicked.connect(self.save_copy)
        controls=QFormLayout(); controls.addRow("Brillo",self.brightness); controls.addRow("Contraste",self.contrast); controls.addRow("Nitidez",self.sharp)
        actions=QHBoxLayout()
        for w in [self.scan,self.rectify,self.bg,self.save]: actions.addWidget(w)
        l=QVBoxLayout(self); l.addWidget(self.canvas,1); l.addLayout(controls); l.addLayout(actions); l.addWidget(self.status)
    def update_preview(self):
        out=imaging.adjust(self.original,self.brightness.value(),self.contrast.value(),self.sharp.value())
        self.canvas.show_image(out)
    def rectify_image(self):
        try:
            self.original=imaging.rectify(self.original,self.canvas.corners); self.canvas.show_image(self.original); self.status.setText("Perspectiva corregida. Esto no calibra la escala clínica.")
        except Exception as e: QMessageBox.warning(self,"No se pudo rectificar",str(e))
    def remove_bg(self):
        try:
            self.original=imaging.remove_background(self.original); self.canvas.show_image(self.original)
            self.status.setText("Fondo estimado. Revisa manualmente los bordes antes de usar la imagen.")
        except Exception as e: QMessageBox.warning(self,"No se pudo quitar el fondo",str(e))
    def save_copy(self):
        try:
            out=imaging.adjust(self.original,self.brightness.value(),self.contrast.value(),self.sharp.value())
            self.saved_path=str(save_processed(self.pid,out))
            self.accept()
        except Exception as e: QMessageBox.critical(self,"Error al guardar",str(e))

class AnalysisDialog(QDialog):
    def __init__(self,key,existing=None,parent=None):
        super().__init__(parent); self.key=key; existing=existing or {}
        self.setWindowTitle(ANALYSES[key]); self.resize(780,680)
        self.status=QComboBox(); self.status.addItems(["Pendiente","En proceso","Completo"]); self.status.setCurrentText(existing.get("status","Pendiente"))
        self.table=QTableWidget(); fields=fields_for(key); special=key in ("steiner","cranio_cervical")
        self.table.setColumnCount(3 if special else 2)
        self.table.setHorizontalHeaderLabels(["Parámetro","Norma / referencia","Valor del paciente"] if special else ["Parámetro","Valor registrado"])
        self.table.setRowCount(len(fields)); saved=existing.get("values",{})
        for r,(label,norm) in enumerate(fields):
            a=QTableWidgetItem(label); a.setFlags(a.flags() & ~Qt.ItemFlag.ItemIsEditable); self.table.setItem(r,0,a)
            if special:
                b=QTableWidgetItem(norm); b.setFlags(b.flags() & ~Qt.ItemFlag.ItemIsEditable); self.table.setItem(r,1,b); col=2
            else: col=1
            self.table.setItem(r,col,QTableWidgetItem(str(saved.get(label,""))))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.obs=QTextEdit(existing.get("observations","")); self.conclusion=QTextEdit(existing.get("conclusion","")); self.conclusion.setMaximumHeight(90)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
        l=QVBoxLayout(self); l.addWidget(QLabel("Registro profesional. Las normas provienen del documento de referencia; confirma la técnica y la calibración."))
        f=QFormLayout(); f.addRow("Estado",self.status); l.addLayout(f); l.addWidget(self.table,1)
        if key=="carpal":
            tab=QTableWidget(len(CARPAL_STAGES),4); tab.setHorizontalHeaderLabels(["Estadio","Código","Masculino","Femenino"])
            for r,row in enumerate(CARPAL_STAGES):
                for c,v in enumerate(row):
                    cell=QTableWidgetItem(str(v)); cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable); tab.setItem(r,c,cell)
            l.addWidget(QLabel("Edades aproximadas en años según la tabla del documento.")); l.addWidget(tab)
        l.addWidget(QLabel("Observaciones")); l.addWidget(self.obs); l.addWidget(QLabel("Conclusión profesional")); l.addWidget(self.conclusion); l.addWidget(buttons)
    def values(self):
        vals={}
        for r in range(self.table.rowCount()):
            label=self.table.item(r,0).text(); vals[label]=self.table.item(r,self.table.columnCount()-1).text().strip()
        return self.status.currentText(),vals,self.obs.toPlainText().strip(),self.conclusion.toPlainText().strip()

class MediaRow(QFrame):
    def __init__(self,workspace,slot):
        super().__init__(); self.ws=workspace; self.slot=slot
        self.setObjectName("Panel"); self.media=None
        self.title=QLabel(slot.label); self.title.setStyleSheet("font-weight:600")
        self.filename=QLabel("Sin archivo"); self.filename.setWordWrap(True)
        self.state=QLabel("Pendiente")
        self.up=QPushButton("Subir archivo"); self.cam=QPushButton("Tomar foto"); self.edit=QPushButton("Ver / editar")
        self.analyze=QPushButton("Abrir análisis")
        self.up.clicked.connect(self.upload); self.cam.clicked.connect(self.camera); self.edit.clicked.connect(self.open_editor)
        self.analyze.clicked.connect(lambda:self.ws.open_slot(self.slot.key))
        h=QHBoxLayout(); h.addWidget(self.title,1); h.addWidget(self.state)
        b=QHBoxLayout()
        for x in (self.up,self.cam,self.edit,self.analyze): b.addWidget(x)
        l=QVBoxLayout(self); l.setContentsMargins(10,8,10,8); l.addLayout(h); l.addWidget(self.filename); l.addLayout(b)
        self.refresh()
    def refresh(self):
        self.media=self.ws.db.get_media_for_slot(self.ws.pid,self.slot.key)
        if self.media:
            self.state.setText("Cargado"); self.filename.setText(Path(self.media["filename"]).name+" · "+Path(self.media["current_path"]).name); self.edit.setEnabled(True); self.analyze.setEnabled(True)
        else:
            self.state.setText("Pendiente" if self.slot.required else "Opcional"); self.filename.setText("Sin archivo"); self.edit.setEnabled(False); self.analyze.setEnabled(False)
    def upload(self):
        p,_=QFileDialog.getOpenFileName(self,"Seleccionar imagen","","Imágenes/DICOM (*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp *.dcm);;Todos (*.*)")
        if p: self.ws.add_file(self.slot.key,p)
    def camera(self):
        dlg=CameraCapture(self)
        if dlg.exec()==QDialog.DialogCode.Accepted and dlg.output_path: self.ws.add_file(self.slot.key,dlg.output_path)
    def open_editor(self):
        if not self.media:return
        allow=self.slot.key.startswith(("extra_","intra_","model_"))
        dlg=ImageEditor(self.ws.pid,self.media["current_path"],allow,self)
        if dlg.exec()==QDialog.DialogCode.Accepted and dlg.saved_path:
            self.ws.db.update_media_path(self.media["id"],dlg.saved_path); self.ws.refresh()

class Workspace(QWidget):
    def __init__(self,db,pid,back):
        super().__init__(); self.db=db; self.pid=pid; self.back=back; self.patient=db.get_patient(pid); self.rows={}
        if not self.patient: raise ValueError("No se encontró el expediente.")
        head=QHBoxLayout(); btn=QPushButton("← Expedientes"); btn.clicked.connect(back)
        title=QLabel(f"{self.patient['full_name']}  ·  {self.patient['record_number']}"); title.setStyleSheet("font-size:16pt;font-weight:700")
        pdf=QPushButton("Exportar informe PDF"); pdf.clicked.connect(self.export_pdf)
        head.addWidget(btn); head.addWidget(title,1); head.addWidget(pdf)
        self.tabs=QTabWidget(); self.files=self.build_files(); self.analyses=QListWidget()
        self.analyses.itemDoubleClicked.connect(self.open_analysis_item)
        self.tabs.addTab(self.build_overview(),"Resumen"); self.tabs.addTab(self.files,"Radiografías, fotografías y modelos")
        page=QWidget(); pl=QVBoxLayout(page); pl.addWidget(QLabel("Los análisis disponibles se activan al cargar el estudio correspondiente.")); pl.addWidget(self.analyses)
        openbtn=QPushButton("Abrir análisis seleccionado"); openbtn.clicked.connect(self.open_selected); pl.addWidget(openbtn)
        self.tabs.addTab(page,"Análisis")
        l=QVBoxLayout(self); l.addLayout(head); l.addWidget(self.tabs,1); self.refresh()
    def build_overview(self):
        w=QWidget(); l=QVBoxLayout(w); self.summary=QLabel(); self.summary.setWordWrap(True); l.addWidget(self.summary)
        for label,key in [("Nacimiento","birth_date"),("Sexo","sex"),("Teléfono","phone"),("Correo","email"),("Notas","notes")]:
            l.addWidget(QLabel(label+": "+(self.patient.get(key) or "—")))
        go=QPushButton("Comenzar carga de estudios"); go.clicked.connect(lambda:self.tabs.setCurrentWidget(self.files)); l.addWidget(go); l.addStretch()
        return w
    def build_files(self):
        w=QWidget(); l=QVBoxLayout(w); scroll=QScrollArea(); scroll.setWidgetResizable(True); inner=QWidget(); il=QVBoxLayout(inner)
        for group,slots in GROUPS:
            box=QGroupBox(group); bl=QVBoxLayout(box)
            for slot in slots:
                row=MediaRow(self,slot); self.rows[slot.key]=row; bl.addWidget(row)
            il.addWidget(box)
        il.addStretch(); scroll.setWidget(inner); l.addWidget(QLabel("En cada vista puedes subir un archivo o tomar una fotografía con la cámara conectada.")); l.addWidget(scroll)
        return w
    def add_file(self,slot,src):
        try:
            stored=import_media(self.pid,src,slot); self.db.add_media(self.pid,slot,stored,stored,Path(src).name); self.refresh()
        except Exception as e: QMessageBox.critical(self,"No se pudo guardar",str(e))
    def refresh(self):
        for row in self.rows.values(): row.refresh()
        required=[s for _,group in GROUPS for s in group if s.required]
        done=sum(bool(self.db.get_media_for_slot(self.pid,s.key)) for s in required)
        counts=self.db.counts_for_patient(self.pid)
        self.summary.setText(f"Vistas requeridas cargadas: {done}/{len(required)}\nArchivos: {counts['media']} · Análisis registrados: {counts['analyses']} · Completos: {counts['complete']}\nLos archivos anteriores de una vista se conservan como historial.")
        available={}
        for item in self.db.media_for_patient(self.pid):
            for key,title in analyses_for_slot(item["slot_key"]): available[key]=title
        self.analyses.clear(); saved=self.db.analysis_for_patient(self.pid)
        for key,title in available.items():
            entry=QListWidgetItem(f"{title} · {saved.get(key,{}).get('status','Pendiente')}"); entry.setData(Qt.ItemDataRole.UserRole,key); self.analyses.addItem(entry)
    def open_slot(self,slot):
        options=analyses_for_slot(slot)
        if not options:return
        key=options[0][0]
        for i in range(self.analyses.count()):
            item=self.analyses.item(i)
            if item.data(Qt.ItemDataRole.UserRole)==key:
                self.analyses.setCurrentItem(item); break
        self.tabs.setCurrentIndex(2); self.open_selected()
    def open_selected(self):
        item=self.analyses.currentItem()
        if item:self.open_analysis_item(item)
    def open_analysis_item(self,item):
        key=item.data(Qt.ItemDataRole.UserRole); existing=self.db.analysis_for_patient(self.pid).get(key,{})
        dlg=AnalysisDialog(key,existing,self)
        if dlg.exec()==QDialog.DialogCode.Accepted:
            status,vals,obs,con=dlg.values(); self.db.save_analysis(self.pid,key,status,vals,obs,con); self.refresh()
    def export_pdf(self):
        path,_=QFileDialog.getSaveFileName(self,"Guardar informe",f"Informe_{self.patient['record_number']}.pdf","PDF (*.pdf)")
        if not path:return
        if not path.lower().endswith(".pdf"):path+=".pdf"
        try:
            from .export_report import export_patient_pdf
            export_patient_pdf(path,self.patient,self.db.media_for_patient(self.pid),self.db.analysis_for_patient(self.pid))
            QMessageBox.information(self,"Informe generado","Se guardó el informe PDF.")
        except Exception as e: QMessageBox.critical(self,"Error al generar informe",str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.db=Database(database_path()); self.setWindowTitle("Pack Análisis Dentales"); self.resize(1320,880)
        self.central=QVBoxLayout(); host=QWidget(); host.setLayout(self.central); self.setCentralWidget(host); self.home()
    def clear(self):
        while self.central.count():
            x=self.central.takeAt(0); w=x.widget()
            if w:w.deleteLater()
    def home(self):
        self.clear(); page=QWidget(); l=QHBoxLayout(page)
        panel=QFrame(); panel.setObjectName("Panel"); panel.setFixedWidth(280); pl=QVBoxLayout(panel)
        brand=QLabel("Pack Análisis Dentales"); brand.setStyleSheet("font-size:19pt;font-weight:700;color:#1d668e")
        new=QPushButton("＋ Nuevo registro"); new.setObjectName("Primary"); new.clicked.connect(self.new_patient)
        pl.addWidget(brand); pl.addWidget(QLabel("Expedientes clínicos y análisis ortodóncicos")); pl.addWidget(new); pl.addStretch()
        main=QVBoxLayout(); main.addWidget(QLabel("Expedientes de pacientes"))
        self.search=QLineEdit(); self.search.setPlaceholderText("Buscar por nombre o número de expediente…"); self.search.textChanged.connect(self.fill_patients)
        self.list=QListWidget(); self.list.itemDoubleClicked.connect(self.open_selected)
        openb=QPushButton("Abrir expediente"); openb.clicked.connect(self.open_selected)
        main.addWidget(self.search); main.addWidget(self.list,1); main.addWidget(openb)
        l.addWidget(panel); l.addLayout(main,1); self.central.addWidget(page); self.fill_patients()
    def fill_patients(self):
        if not hasattr(self,"list"):return
        self.list.clear()
        for p in self.db.list_patients(self.search.text()):
            item=QListWidgetItem(p["full_name"]+"\n"+p["record_number"]); item.setData(Qt.ItemDataRole.UserRole,p["id"]); self.list.addItem(item)
    def new_patient(self):
        dlg=NewPatient(self)
        if dlg.exec()==QDialog.DialogCode.Accepted:
            try:self.open_patient(self.db.create_patient(**dlg.values())["id"])
            except Exception as e:QMessageBox.critical(self,"No se pudo crear",str(e))
    def open_selected(self,item=None):
        item=item or self.list.currentItem()
        if item:self.open_patient(item.data(Qt.ItemDataRole.UserRole))
    def open_patient(self,pid):
        self.clear(); self.central.addWidget(Workspace(self.db,pid,self.home))
        
def run_app():
    app=QApplication.instance() or QApplication([])
    app.setApplicationName("Pack Análisis Dentales"); app.setStyleSheet(STYLE)
    win=MainWindow(); win.show(); return app.exec()
