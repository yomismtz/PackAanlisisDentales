"""Edición de copias; la transformación de perspectiva no calibra medidas."""
from pathlib import Path
import numpy as np
import cv2

def load_image(path):
    p=Path(path)
    if p.suffix.lower()==".dcm":
        try: import pydicom
        except ImportError as e: raise RuntimeError("Instala pydicom para abrir DICOM.") from e
        ds=pydicom.dcmread(str(p)); a=ds.pixel_array.astype(np.float32)
        lo,hi=np.percentile(a,[1,99]); a=np.clip((a-lo)/max(hi-lo,1)*255,0,255).astype("uint8")
        if getattr(ds,"PhotometricInterpretation","")=="MONOCHROME1": a=255-a
        return cv2.cvtColor(a,cv2.COLOR_GRAY2BGR)
    raw=np.fromfile(str(p),dtype=np.uint8); im=cv2.imdecode(raw,cv2.IMREAD_UNCHANGED)
    if im is None: raise ValueError("No se pudo leer la imagen.")
    if im.ndim==2: im=cv2.cvtColor(im,cv2.COLOR_GRAY2BGR)
    if im.shape[2]==4: im=cv2.cvtColor(im,cv2.COLOR_BGRA2BGR)
    return im

def adjust(im,brightness=0,contrast=100,sharpness=100):
    x=np.clip(im.astype(np.float32)*(contrast/100)+brightness,0,255).astype(np.uint8)
    if sharpness!=100:
        blur=cv2.GaussianBlur(x,(0,0),2); x=cv2.addWeighted(x,sharpness/100,blur,1-sharpness/100,0)
    return x

def rectify(im,corners):
    if len(corners)!=4: raise ValueError("Selecciona las cuatro esquinas.")
    pts=np.asarray(corners,dtype=np.float32)
    tl,tr,br,bl=pts
    w=int(max(np.linalg.norm(br-bl),np.linalg.norm(tr-tl))); h=int(max(np.linalg.norm(tr-br),np.linalg.norm(tl-bl)))
    if w<20 or h<20: raise ValueError("El recorte es demasiado pequeño.")
    target=np.float32([[0,0],[w-1,0],[w-1,h-1],[0,h-1]])
    return cv2.warpPerspective(im,cv2.getPerspectiveTransform(pts,target),(w,h))

def remove_background(im):
    h,w=im.shape[:2]; mask=np.zeros((h,w),np.uint8)
    rect=(max(1,int(w*.04)),max(1,int(h*.04)),max(2,int(w*.92)),max(2,int(h*.92)))
    bg=np.zeros((1,65),np.float64); fg=np.zeros((1,65),np.float64)
    cv2.grabCut(im,mask,rect,bg,fg,5,cv2.GC_INIT_WITH_RECT)
    alpha=np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),255,0).astype(np.uint8)
    out=cv2.cvtColor(im,cv2.COLOR_BGR2BGRA); out[:,:,3]=alpha; return out
