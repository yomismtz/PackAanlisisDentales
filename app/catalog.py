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
 "nance_carey":"Carey · discrepancia de espacio (dentición permanente)","tanaka_johnston":"Tanaka-Johnston",
 "baume":"Baumé","palatal_height":"Altura del paladar","facial_frontal":"Análisis facial frontal",
 "facial_profile":"Análisis facial de perfil","facial_midlines":"Líneas medias",
 "smile":"Análisis de sonrisa","facial_symmetry":"Simetrías horizontales · quintos",
 "facial_levels":"Análisis de niveles faciales","facial_contour":"Análisis de contorno facial",
 "powell":"Análisis de Powell","facial_projections":"Análisis de proyecciones"
}
# Cada grupo representa un conjunto de vistas que debe estar cargado completo.
# Si un análisis tiene más de un grupo, cualquiera de las alternativas es válida.
ANALYSIS_REQUIREMENTS = {
    "steiner": (("ceph_lateral",),),
    "cranio_cervical": (("ceph_lateral",),),
    "cervical_maturation": (("ceph_lateral",),),
    "panoramic_systematic": (("panoramic",),),
    "levandoski": (("panoramic",),),
    "dental_age": (("panoramic",),),
    "carpal": (("carpal",),),
    # La integración requiere dos fuentes principales: maduración dental y cervical.
    # La radiografía carpal se conserva como estudio complementario opcional.
    "maturation_integration": (("panoramic", "ceph_lateral"),),
    "intermaxillary": (
        ("intra_right", "intra_left", "intra_frontal"),
        ("model_both_right", "model_both_left", "model_both_front"),
    ),
    "moyers": (("model_upper_occlusal", "model_lower_occlusal"),),
    "nance_carey": (("model_upper_occlusal", "model_lower_occlusal"),),
    "tanaka_johnston": (("model_upper_occlusal", "model_lower_occlusal"),),
    "baume": (
        ("intra_upper", "intra_lower", "intra_right", "intra_left"),
        ("model_upper_occlusal", "model_lower_occlusal", "model_both_right", "model_both_left"),
    ),
    "little_upper": (("model_upper_occlusal",),),
    "little_lower": (("model_lower_occlusal",),),
    "facial_frontal": (("extra_frontal",),),
    "facial_midlines": (("extra_frontal",),),
    "facial_levels": (("extra_frontal",),),
    "facial_contour": (("extra_frontal",),),
    "facial_symmetry": (("extra_frontal",),),
    "smile": (("extra_smiling",),),
    "facial_profile": (("extra_profile",),),
    "powell": (("extra_profile",),),
    "facial_projections": (("extra_profile",),),
}
# Altura palatina permanece fuera de la oferta automática: el expediente solo
# admite imágenes 2D y todavía no tiene captura 3D ni medición física validada.
UNAVAILABLE_ANALYSES = {"palatal_height"}

BY_SLOT = {
    slot: [
        analysis for analysis, alternatives in ANALYSIS_REQUIREMENTS.items()
        if any(slot in required_group for required_group in alternatives)
    ]
    for slot in SLOTS
}


def analyses_for_slot(key):
    """Devuelve análisis candidatos asociados a una vista, no su disponibilidad final."""
    return [(analysis, ANALYSES[analysis]) for analysis in BY_SLOT.get(key, [])]


def analyses_for_available_slots(slot_keys):
    """Devuelve análisis cuyas vistas requeridas están todas cargadas."""
    available_slots = set(slot_keys)
    result = []
    for analysis, alternatives in ANALYSIS_REQUIREMENTS.items():
        if any(set(required_group).issubset(available_slots) for required_group in alternatives):
            result.append((analysis, ANALYSES[analysis]))
    return result


def analysis_available_for_slot(analysis_key, slot_key, available_analysis_keys):
    """Comprueba que el análisis esté disponible y relacionado con la vista seleccionada."""
    return (
        analysis_key in available_analysis_keys
        and analysis_key in BY_SLOT.get(slot_key, [])
    )

CARPAL_STAGES=[
 (1,"PP2=","10.6","8.1"),(2,"MP3=","12.0","8.1"),(3,"Pisi / H1 / R=","12.6","9.6"),
 (4,"S / H2","13.0","10.6"),(5,"MP3 Cap / R Cap / PP1 Cap","14.0","11.0"),
 (6,"DP3u","15.0","13.0"),(7,"PP3u","15.9","13.3"),(8,"MP3u","15.9","13.9"),(9,"Ru","18.5","16.0")]
