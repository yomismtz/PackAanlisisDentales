"""Gestión local de archivos: el original nunca se sobrescribe."""
import os, shutil, uuid
from pathlib import Path

def app_data_dir():
    root = Path(os.getenv("LOCALAPPDATA", Path.home()/".local"/"share")) / "PackAnalisisDentales"
    root.mkdir(parents=True,exist_ok=True); return root

def database_path(): return app_data_dir() / "expedientes.sqlite3"

def patient_dir(pid):
    p=app_data_dir()/"pacientes"/pid; p.mkdir(parents=True,exist_ok=True); return p

def import_media(pid, source, slot):
    source=Path(source)
    if not source.is_file(): raise FileNotFoundError(source)
    folder=patient_dir(pid)/slot; folder.mkdir(exist_ok=True)
    dest=folder/(uuid.uuid4().hex[:12]+source.suffix.lower())
    shutil.copy2(source,dest)
    return dest

def save_processed(pid, image, suffix=".png"):
    import cv2
    path=patient_dir(pid)/("edit_"+uuid.uuid4().hex[:12]+suffix)
    ok, data=cv2.imencode(suffix,image)
    if not ok: raise ValueError("No se pudo procesar la imagen.")
    data.tofile(str(path)); return path
