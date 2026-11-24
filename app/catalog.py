from dataclasses import dataclass

@dataclass(frozen=True)
class Slot:
    key: str
    label: str
    group: str
    required: bool = True
    capture_guide: str = ""

GROUPS = [
 ("Radiografías", [Slot("ceph_lateral","Lateral de cráneo","Radiografías"),Slot("panoramic","Panorámica","Radiografías")]),
 ("Fotografías extraorales", [Slot("extra_frontal","Frontal en reposo · seria","Fotografías extraorales", True, "Fotografía frontal en reposo: rostro de frente, cabeza en posición natural y sin inclinación, mirada al frente, labios relajados y sin sonreír. Cabello recogido, frente completamente despejada y ambas orejas descubiertas. Iluminación uniforme y fondo neutro."),Slot("extra_smiling","Frontal sonriendo","Fotografías extraorales", True, "Fotografía frontal con sonrisa amplia y natural, mostrando dientes y encía visible. Rostro de frente, cabeza sin inclinación, mirada al frente, cabello recogido, frente despejada y ambas orejas descubiertas. Deben verse completas las dos comisuras."),Slot("extra_profile","Perfil lateral · serio","Fotografías extraorales", True, "Fotografía lateral de perfil en reposo. Mantener siempre el mismo lado (derecho o izquierdo), cabeza en posición natural, mirada al frente y labios relajados. Cabello recogido, frente despejada y oreja del lado fotografiado descubierta. Deben verse nariz, labios, mentón y contorno cervical.")]),
 ("Fotografías intraorales", [
  Slot("intra_right","Lateral derecha","Fotografías intraorales"),Slot("intra_left","Lateral izquierda","Fotografías intraorales"),
  Slot("intra_frontal","Frontal en oclusión","Fotografías intraorales"),Slot("intra_upper","Oclusal superior","Fotografías intraorales"),
  Slot("intra_lower","Oclusal inferior","Fotografías intraorales"),Slot("intra_extra","Vista adicional","Fotografías intraorales",False)]),
 ("Modelos superiores", [Slot("model_upper_right","Lateral derecha","Modelos superiores"),Slot("model_upper_left","Lateral izquierda","Modelos superiores"),Slot("model_upper_front","Frontal","Modelos superiores"),Slot("model_upper_occlusal","Vista oclusal","Modelos superiores")]),
 ("Modelos inferiores", [Slot("model_lower_right","Lateral derecha","Modelos inferiores"),Slot("model_lower_left","Lateral izquierda","Modelos inferiores"),Slot("model_lower_front","Frontal","Modelos inferiores"),Slot("model_lower_occlusal","Vista oclusal","Modelos inferiores")]),
 ("Modelos en oclusión", [Slot("model_both_right","Lateral derecha","Modelos en oclusión"),Slot("model_both_left","Lateral izquierda","Modelos en oclusión"),Slot("model_both_front","Frontal","Modelos en oclusión")]),
 ("Maduración", [Slot("carpal","Radiografía carpal","Maduración",False)])
]
SLOTS = {s.key:s for _,group in GROUPS for s in group}
ANALYSES = {
 "steiner":"Cefalometría de Steiner","cranio_cervical":"Posición craneofacial y postura cráneo-cervical",
 "cervical_maturation":"Maduración vertebral cervical · CS1–CS6","panoramic_systematic":"Análisis sistemático panorámico",
 "levandoski":"Análisis de Levandoski","little_upper":"Índice de Little · modelo superior","little_lower":"Índice de Little · modelo inferior","dental_age":"Edad dental · Método de Nolla",
 "maturation_integration":"Integración de maduración","carpal":"Maduración esquelética · radiografía carpal",
 "intermaxillary":"Relaciones intermaxilares","moyers":"Moyers I · 75 %",
 "nance_carey":"Discrepancia óseo-dentaria · Nance y Carey","tanaka_johnston":"Tanaka-Johnston",
 "baume":"Baumé","palatal_height":"Altura del paladar","facial_frontal":"Análisis facial frontal",
 "facial_profile":"Análisis facial de perfil","facial_midlines":"Líneas medias",
 "smile":"Análisis de sonrisa","facial_symmetry":"Simetrías horizontales · quintos"
}
BY_SLOT = {
 "ceph_lateral":["steiner","cranio_cervical","cervical_maturation","maturation_integration"],
 "panoramic":["panoramic_systematic","levandoski","dental_age","maturation_integration"],
 "carpal":["carpal","maturation_integration"],
 "extra_frontal":["facial_frontal","facial_midlines","facial_levels","facial_contour","facial_symmetry"],
 "extra_smiling":["smile"],
 "extra_profile":["facial_profile","powell","facial_projections"]
}
for key in ("intra_right","intra_left","intra_frontal","intra_upper","intra_lower","intra_extra",
 "model_upper_right","model_upper_left","model_upper_front","model_upper_occlusal",
 "model_lower_right","model_lower_left","model_lower_front","model_lower_occlusal",
 "model_both_right","model_both_left","model_both_front"):
    BY_SLOT[key]=["intermaxillary","moyers","nance_carey","tanaka_johnston","baume","palatal_height"]
BY_SLOT["model_upper_occlusal"].append("little_upper")
BY_SLOT["model_lower_occlusal"].append("little_lower")

def analyses_for_slot(key):
    return [(k,ANALYSES[k]) for k in BY_SLOT.get(key,[])]

CARPAL_STAGES=[
 (1,"PP2=","10.6","8.1"),(2,"MP3=","12.0","8.1"),(3,"Pisi / H1 / R=","12.6","9.6"),
 (4,"S / H2","13.0","10.6"),(5,"MP3 Cap / R Cap / PP1 Cap","14.0","11.0"),
 (6,"DP3u","15.0","13.0"),(7,"PP3u","15.9","13.3"),(8,"MP3u","15.9","13.9"),(9,"Ru","18.5","16.0")]
