"""Campos basados en el documento clínico aportado. No se inventan criterios ausentes."""
STEINER = [
 ("SNA","82° ± 2°"),("S-N / Po-Or","7° ± 3°"),("Frankfort-plano palatino","5° ± 2°"),
 ("SNB","80° ± 2°"),("SND","77° ± 2°"),("Segmento SL","51 mm ± 2 mm"),
 ("Segmento SE","23 mm ± 2 mm"),("Ar-Go-Me","125° ± 2°"),("Go-Gn a SN","32° ± 5°"),
 ("ANB","2° ± 1°"),("AB-Go-Gn","74° ± 2°"),("IS-SN","104° ± 2°"),
 ("IS-NA angular","22° ± 2°"),("IS-NA lineal","4 mm ± 1 mm"),("II-NB angular","16° ± 1°"),
 ("II-NB lineal","4 mm ± 1 mm"),("Plano oclusal-SN","16° ± 1°"),
 ("Ángulo interincisal","135° ± 4°"),("Labio superior a línea S","0 mm ± 2 mm"),
 ("Labio inferior a línea S","0 mm · referencia del documento"),("Pg-NB","4 mm ± 1 mm")]
CRANIO = [
 ("Inclinación de SN","Positiva o negativa"),("ANB","2° ± 2°"),("SN-GoGn","32° ± 5°"),
 ("SN-PoOr","6°–10°"),("SN-CVT","96°–102°"),("SN-OPT","94°–100°"),
 ("SNBa–C3","120°–130°"),("McGregor-plano odontoideo","96°–106°"),
 ("Alineación C2–C4","Las partes distales deben estar alineadas")]
FIELDS = {
 "steiner":STEINER, "cranio_cervical":CRANIO,
 "levandoski":[(x,"") for x in [
  "Rama mandibular derecha (mm)","Rama mandibular izquierda (mm)",
  "Cóndilo a incisivo central maxilar derecho (mm)","Cóndilo a incisivo central maxilar izquierdo (mm)",
  "Cóndilo a incisivo central mandibular derecho (mm)","Cóndilo a incisivo central mandibular izquierdo (mm)",
  "Cóndilo a gonion derecho (mm)","Cóndilo a gonion izquierdo (mm)",
  "Ancho de rama derecha (mm)","Ancho de rama izquierda (mm)"]],
 "intermaxillary":[(x,"") for x in [
  "Relación molar derecha","Relación molar izquierda","Relación canina derecha","Relación canina izquierda",
  "Overjet · categoría descriptiva","Sobremordida vertical · categoría descriptiva","Relación transversal",
  "Línea media superior","Línea media inferior","Desviación mandibular al cierre"]],
 "moyers":[(x,"") for x in ["OD 42 (mm)","OD 41 (mm)","OD 31 (mm)","OD 32 (mm)","Suma incisivos inferiores (mm)","Valor tabular Moyers 75 % superior (mm)","Valor tabular Moyers 75 % inferior (mm)","Espacio disponible (mm)","Discrepancia (mm)"]],
 "nance_carey":[(x,"") for x in ["Espacio requerido superior (mm)","Espacio requerido inferior (mm)","Espacio disponible superior (mm)","Espacio disponible inferior (mm)","Discrepancia superior (mm)","Discrepancia inferior (mm)"]],
 "tanaka_johnston":[(x,"") for x in ["Suma de incisivos inferiores (mm)","Predicción superior por lado (mm)","Predicción inferior por lado (mm)","Espacio disponible superior (mm)","Espacio disponible inferior (mm)"]],
 "baume":[(x,"") for x in [
  "Tipo de arcada superior","Tipo de arcada inferior",
  "Espacio primate superior derecho","Espacio primate superior izquierdo",
  "Espacio primate inferior derecho","Espacio primate inferior izquierdo",
  "Plano terminal derecho","Plano terminal izquierdo"]],
 "carpal":[(x,"") for x in ["Edad cronológica","Sexo registrado","Estadio carpal (1–9)","Edad ósea estimada (años)","Interpretación profesional"]],
 "cervical_maturation":[(x,"") for x in ["Estadio vertebral","Descripción","Interpretación profesional"]],
 "panoramic_systematic":[(x,"") for x in ["Calidad técnica y cobertura","Dentición y secuencia de erupción","Estructuras óseas revisadas","Periodonto y soporte óseo","Cóndilos y ATM","Senos maxilares","Hallazgos y localización"]],
}
def fields_for(key):
    return FIELDS.get(key, [(x,"") for x in {
      "dental_age":["Método de estimación utilizado","Referencia / tabla","Hallazgos de desarrollo y erupción","Edad dental estimada (años)","Diferencia respecto a edad cronológica (años)"],
      "maturation_integration":["Edad cronológica","Edad dental y método","Edad ósea / carpal","Maduración cervical","Relación entre indicadores","Síntesis profesional"],
      "facial_frontal":["Tercios faciales","Línea media","Niveles faciales","Contorno y simetría","Observaciones"],
      "facial_profile":["Tercios faciales","Proyección de tejidos blandos","Ángulos de perfil","Observaciones"],
      "facial_midlines":["Punta nasal","Filtro","Mentón","Línea media incisivos superiores/inferiores","Niveles faciales"],
      "smile":["Línea de labios","Arco de sonrisa","Corredores bucales","Exposición gingival","Simetría"],
      "facial_symmetry":["Quintos faciales","Ancho nasal","Distancia intercantal","Ancho bucal","Discrepancias"]
    }.get(key,["Medición / hallazgo","Observaciones"])])
