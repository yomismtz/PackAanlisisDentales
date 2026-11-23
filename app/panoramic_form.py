"""Formulario panorámico académico estructurado y basado en selecciones."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QGroupBox,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QPushButton, QScrollArea, QTabWidget, QTextEdit, QVBoxLayout, QWidget,
)

STATUS_OPTIONS = ("Pendiente", "En proceso", "Completo")
FDI_TEETH = (
    tuple(str(q) + str(n) for q in (1, 2, 3, 4) for n in range(1, 9))
    + tuple(str(q) + str(n) for q in (5, 6, 7, 8) for n in range(1, 6))
)
REGIONS = (
    "Maxilar posterior derecho", "Maxilar anterior", "Maxilar posterior izquierdo",
    "Mandíbula posterior izquierda", "Mandíbula anterior", "Mandíbula posterior derecha",
    "Maxilar", "Mandíbula", "Línea media", "No determinable",
)
EVALUABILITY = ("Identificada", "No identificada", "No evaluable", "No aplica")
CONFIDENCE = ("Observación", "Sospecha", "Probable", "No concluyente")
YES_NO_NA = ("Sí", "No", "No evaluable", "No aplica")
NORMAL_VARIANT = ("Habitual aparente", "Variación anatómica", "Alterada", "No evaluable")

# Cada campo tiene: clave estable, etiqueta visible, tipo de control y opciones.
# Los criterios son descriptivos y educativos; no generan diagnósticos automáticos.
PANORAMIC_PHASES = [
    {
        "title": "01 · Calidad técnica",
        "help": "Antes de interpretar, comprueba nitidez, contraste, exposición, movimiento, posicionamiento y cobertura. Decide si la imagen permite un análisis completo o solo parcial.",
        "fields": [
            ("aceptacion", "Aceptación de la imagen", "choice", ("Adecuada", "Adecuada con limitaciones", "No diagnóstica")),
            ("nitidez", "Nitidez", "choice", ("Adecuada", "Disminuida", "Muy disminuida", "No evaluable")),
            ("contraste", "Contraste", "choice", ("Adecuado", "Aumentado", "Disminuido", "No evaluable")),
            ("exposicion", "Exposición", "choice", ("Adecuada", "Sobreexpuesta", "Subexpuesta", "No evaluable")),
            ("movimiento", "Movimiento del paciente", "choice", ("No evidente", "Leve", "Marcado", "No determinable")),
            ("posicionamiento", "Posicionamiento", "choice", ("Adecuado", "Rotación", "Cabeza inclinada", "Mentón alto", "Mentón bajo", "Paciente adelantado", "Paciente retrasado", "Lengua fuera del paladar", "Otro error", "No evaluable")),
            ("errores", "Errores técnicos identificados", "multi", ("Rotación", "Inclinación", "Mentón alto", "Mentón bajo", "Paciente adelantado", "Paciente retrasado", "Lengua fuera del paladar", "Movimiento", "Artefacto", "Exposición inadecuada", "Otro")),
            ("cobertura", "Regiones comprometidas o no incluidas", "multi", REGIONS + ("Cóndilos", "Ramas mandibulares", "Bordes inferiores")),
            ("evaluabilidad_general", "Evaluabilidad global", "choice", ("Evaluable", "Evaluable con limitaciones", "No evaluable")),
            ("calidad_detalle", "Comprobación de calidad (detalle)", "multi", ("Cresta nítida y distinguible", "Contraste suficiente entre estructuras", "Exposición permite valorar densidades", "Sin movimiento que comprometa lectura", "Sin artefactos relevantes", "Cobertura anatómica suficiente", "Una o más condiciones no se cumplen")),
            ("limitaciones_calidad", "Limitaciones que afectan la interpretación", "multi", ("Región anterior distorsionada", "Región posterior distorsionada", "Cóndilos recortados", "Bordes mandibulares recortados", "Superposición marcada", "Movimiento", "Artefacto", "Exposición", "Otra limitación", "Sin limitaciones relevantes")),
        ],
    },
    {
        "title": "02 · Orientación y regiones",
        "help": "Confirma derecha e izquierda desde la perspectiva del paciente, localiza la línea media y recorre las seis regiones para evitar omisiones.",
        "fields": [
            ("orientacion", "Orientación derecha–izquierda", "choice", ("Correcta", "Dudosa", "Invertida", "No determinable")),
            ("linea_media", "Identificación de línea media", "choice", ("Centrada", "Desviada", "No identificable", "No evaluable")),
            ("lados", "Regiones identificadas", "multi", REGIONS),
            ("maxilar", "Identificación del maxilar", "choice", EVALUABILITY),
            ("mandibula", "Identificación de la mandíbula", "choice", EVALUABILITY),
            ("distorsion", "Distorsión o superposición relevante", "choice", ("No evidente", "Leve", "Moderada", "Marcada", "No evaluable")),
            ("nota_orientacion", "Comentario opcional", "line", ()),
            ("verificacion_orientacion", "Verificación antes de interpretar", "multi", ("Marcador R/L confirmado", "Derecha e izquierda desde perspectiva del paciente", "Línea media ubicada", "Orientación de imagen confiable", "Orientación dudosa; evitar asignación lateral")),
            ("evaluabilidad_region", "Mapa de evaluabilidad por región", "multi", ("Maxilar posterior derecho · evaluable", "Maxilar anterior · evaluable", "Maxilar posterior izquierdo · evaluable", "Mandíbula posterior izquierda · evaluable", "Mandíbula anterior · evaluable", "Mandíbula posterior derecha · evaluable", "Maxilar posterior derecho · limitado", "Maxilar anterior · limitado", "Maxilar posterior izquierdo · limitado", "Mandíbula posterior izquierda · limitado", "Mandíbula anterior · limitado", "Mandíbula posterior derecha · limitado", "Maxilar posterior derecho · no evaluable", "Maxilar anterior · no evaluable", "Maxilar posterior izquierdo · no evaluable", "Mandíbula posterior izquierda · no evaluable", "Mandíbula anterior · no evaluable", "Mandíbula posterior derecha · no evaluable")),
            ("recorrido_guiado", "Recorrido sistemático inicial", "multi", ("1 · Confirmar calidad técnica y cobertura", "2 · Confirmar orientación y línea media", "3 · Revisar maxilar de derecha a izquierda", "4 · Revisar mandíbula de izquierda a derecha", "5 · Marcar regiones limitadas y pendientes")),
        ],
    },
    {
        "title": "03 · Anatomía maxilar",
        "help": "Identifica primero las estructuras anatómicas normales. Registra variantes o cambios aparentes sin etiquetarlos automáticamente como enfermedad.",
        "fields": [
            ("cavidad_nasal", "Cavidad nasal", "choice", NORMAL_VARIANT),
            ("tabique_nasal", "Tabique nasal", "choice", NORMAL_VARIANT),
            ("piso_nasal", "Piso de cavidad nasal", "choice", NORMAL_VARIANT),
            ("espina_nasal", "Espina nasal anterior", "choice", EVALUABILITY),
            ("y_invertida", "Y invertida de Ennis", "choice", EVALUABILITY),
            ("paladar_duro", "Paladar duro", "choice", NORMAL_VARIANT),
            ("seno_derecho", "Seno maxilar derecho", "choice", ("Neumatización habitual aparente", "Engrosamiento mucoso sospechado", "Opacidad", "Radiolucidez", "Piso irregular", "No evaluable")),
            ("seno_izquierdo", "Seno maxilar izquierdo", "choice", ("Neumatización habitual aparente", "Engrosamiento mucoso sospechado", "Opacidad", "Radiolucidez", "Piso irregular", "No evaluable")),
            ("proceso_cigomatico", "Proceso cigomático", "choice", EVALUABILITY),
            ("tuberosidad", "Tuberosidad maxilar", "choice", NORMAL_VARIANT),
        ],
    },
    {
        "title": "04 · Anatomía mandibular",
        "help": "Sigue el contorno mandibular y localiza cuerpo, sínfisis, ángulos, ramas, cóndilos, forámenes y conducto mandibular.",
        "fields": [
            ("cuerpo", "Cuerpo mandibular", "choice", EVALUABILITY),
            ("borde_inferior", "Borde inferior mandibular", "choice", ("Continuo", "Irregular", "Interrumpido", "No evaluable")),
            ("sinfisis", "Sínfisis y región mentoniana", "choice", NORMAL_VARIANT),
            ("angulo", "Ángulos mandibulares", "choice", ("Simétricos", "Asimétricos", "Irregulares", "No evaluables")),
            ("ramas", "Ramas mandibulares", "choice", ("Simétricas", "Asimétricas", "Contorno irregular", "No evaluables")),
            ("condilos", "Cóndilos visibles", "choice", ("Ambos identificables", "Solo derecho", "Solo izquierdo", "Ninguno evaluable")),
            ("coronoides", "Apófisis coronoides", "choice", EVALUABILITY),
            ("foramen_mentoniano", "Forámenes mentonianos", "choice", ("Ambos identificables", "Solo derecho", "Solo izquierdo", "No identificables")),
            ("conducto", "Conducto mandibular", "choice", ("Trayecto identificable bilateralmente", "Identificable parcialmente", "No identificable", "Alteración aparente")),
        ],
    },
    {
        "title": "05 · Anatomía dentaria",
        "help": "Revisa coronas, cámaras pulpares, raíces, ápices, espacio periodontal, lámina dura y furcaciones. Recuerda que la panorámica tiene límites para detalles finos.",
        "fields": [
            ("coronas", "Coronas", "choice", ("Contornos habituales", "Alteraciones aparentes", "No evaluables")),
            ("esmalte_dentina", "Esmalte y dentina", "choice", ("Diferenciación aparente conservada", "Alteración de densidad", "No evaluable")),
            ("camara_pulpar", "Cámaras pulpares", "choice", ("Morfología habitual aparente", "Calcificación/reducción aparente", "Ampliación aparente", "No evaluable")),
            ("conductos", "Conductos radiculares", "choice", ("Trayecto identificable", "Anatomía compleja", "No identificables en varios dientes", "No evaluable")),
            ("raices", "Raíces", "choice", ("Morfología habitual aparente", "Variantes morfológicas", "Alteraciones aparentes", "No evaluables")),
            ("apices", "Ápices", "choice", ("Cerrados", "En desarrollo", "Morfología irregular", "No evaluables")),
            ("lpd", "Espacio periodontal", "choice", ("Uniforme aparente", "Ensanchado", "Estrechado", "Irregular", "No evaluable")),
            ("lamina", "Lámina dura", "choice", ("Continua aparente", "Interrumpida", "Engrosada", "No identificable", "No evaluable")),
            ("furcacion", "Regiones de furcación", "choice", ("Sin cambios aparentes", "Cambio sospechoso", "No evaluables")),
            ("restauraciones", "Restauraciones y materiales", "choice", ("No identificados", "Presentes", "Presentes con posible defecto", "No evaluables")),
            ("limite_resolucion", "Limitación para valorar detalles finos", "choice", ("No relevante", "Presente; requiere intraoral", "No evaluable")),
        ],
    },
    {
        "title": "06 · Inventario y anomalías dentales",
        "help": "Revisa diente por diente con nomenclatura FDI. Distingue ausencia aparente, falta de erupción, retención, ectopia y posible anomalía del desarrollo.",
        "fields": [
            ("erupcionados", "Dientes erupcionados (FDI)", "teeth", FDI_TEETH),
            ("desarrollo", "Dientes en desarrollo / no erupcionados", "teeth", FDI_TEETH),
            ("retencion", "Dientes retenidos o posiblemente incluidos", "teeth", FDI_TEETH),
            ("ausentes", "Dientes no identificados en imagen (no confirma agenesia)", "teeth", FDI_TEETH),
            ("supernumerarios", "Regiones/dientes supernumerarios sospechados", "multi", ("Mesiodens", "Sector anterior maxilar", "Sector anterior mandibular", "Premolar superior", "Premolar inferior", "Región molar", "Otra región")),
            ("ectopicos", "Erupción ectópica / posición atípica", "teeth", FDI_TEETH),
            ("anatomia_atipica", "Anomalías morfológicas sospechadas", "multi", ("Microdoncia", "Macrodoncia", "Dilaceración", "Taurodontismo", "Fusión", "Geminación", "Raíz adicional", "Raíces fusionadas", "Otra")),
            ("conteo", "Estado del inventario", "choice", ("Revisado", "Revisado con limitaciones", "Pendiente")),
            ("nota_inventario", "Comentario opcional", "line", ()),
        ],
    },
    {
        "title": "07 · Soporte óseo alveolar",
        "help": "Observa crestas, nivel óseo, patrón y distribución. La panorámica no sustituye el sondaje periodontal.",
        "fields": [
            ("nivel_cresta", "Nivel de cresta alveolar", "choice", ("Conservado aparente", "Disminución leve", "Disminución moderada", "Disminución marcada", "No evaluable")),
            ("patron_perdida", "Patrón de pérdida ósea aparente", "choice", ("Sin pérdida evidente", "Horizontal", "Vertical/angular", "Mixto", "No concluyente")),
            ("distribucion", "Distribución", "choice", ("Localizada", "Regional", "Generalizada", "No evaluable")),
            ("trabeculado", "Patrón trabecular", "choice", ("Habitual aparente", "Aumentado", "Disminuido", "Heterogéneo", "No evaluable")),
            ("cortical_alveolar", "Cortical alveolar", "choice", ("Conservada", "Irregular", "No identificable", "No evaluable")),
            ("furcaciones", "Furcaciones", "choice", ("Sin alteración aparente", "Cambios sospechosos", "No evaluables")),
            ("correlacion_periodontal", "Necesidad de evaluación periodontal clínica", "choice", ("Sí", "No evidente", "Según hallazgo / sondaje")),
        ],
    },
    {
        "title": "08 · Terceros molares",
        "help": "Registra 18, 28, 38 y 48 por separado: presencia, erupción, orientación, desarrollo radicular y relaciones anatómicas.",
        "fields": [
            ("18_estado", "18 · Estado", "choice", ("Ausente", "Erupcionado", "Parcialmente erupcionado", "No erupcionado", "Retenido/incluido sospechado", "No evaluable")),
            ("18_posicion", "18 · Orientación", "choice", ("Vertical", "Mesioangular", "Distoangular", "Horizontal", "Invertido", "Transversal", "No aplica / no evaluable")),
            ("28_estado", "28 · Estado", "choice", ("Ausente", "Erupcionado", "Parcialmente erupcionado", "No erupcionado", "Retenido/incluido sospechado", "No evaluable")),
            ("28_posicion", "28 · Orientación", "choice", ("Vertical", "Mesioangular", "Distoangular", "Horizontal", "Invertido", "Transversal", "No aplica / no evaluable")),
            ("38_estado", "38 · Estado", "choice", ("Ausente", "Erupcionado", "Parcialmente erupcionado", "No erupcionado", "Retenido/incluido sospechado", "No evaluable")),
            ("38_posicion", "38 · Orientación", "choice", ("Vertical", "Mesioangular", "Distoangular", "Horizontal", "Invertido", "Transversal", "No aplica / no evaluable")),
            ("48_estado", "48 · Estado", "choice", ("Ausente", "Erupcionado", "Parcialmente erupcionado", "No erupcionado", "Retenido/incluido sospechado", "No evaluable")),
            ("48_posicion", "48 · Orientación", "choice", ("Vertical", "Mesioangular", "Distoangular", "Horizontal", "Invertido", "Transversal", "No aplica / no evaluable")),
            ("relacion_segundo", "Relación con segundos molares", "choice", ("Sin contacto aparente", "Contacto aparente", "Superposición", "Posible afectación distal", "No evaluable")),
            ("canal_signos", "Signos radiográficos de relación con conducto mandibular (38/48)", "multi", ("Oscurecimiento radicular", "Interrupción de corticales del conducto", "Desviación del conducto", "Estrechamiento del conducto", "Superposición sin signos adicionales", "Sin signos identificables", "No evaluable")),
            ("seno_relacion", "Relación de terceros molares superiores con seno maxilar", "choice", ("Sin proximidad aparente", "Proximidad aparente", "Superposición", "No evaluable")),
            ("desarrollo_radicular", "Desarrollo radicular", "choice", ("Incompleto", "Completo", "No determinable")),
        ],
    },
    {
        "title": "09 · Anatomía adyacente",
        "help": "Vuelve a revisar senos, cavidad nasal, estructuras cigomáticas, forámenes, conducto mandibular y espacios anatómicos.",
        "fields": [
            ("senos", "Senos maxilares", "choice", ("Sin alteración aparente", "Engrosamiento mucoso sospechado", "Opacidad", "Asimetría", "No evaluables")),
            ("cavidad_nasal", "Cavidad nasal y tabique", "choice", NORMAL_VARIANT),
            ("cigomatico", "Estructuras cigomáticas", "choice", EVALUABILITY),
            ("tuberosidad_coronoides", "Tuberosidad maxilar / coronoides", "choice", ("Superposición habitual aparente", "Superposición que limita valoración", "Alteración sospechada", "No evaluable")),
            ("foramen_mentoniano", "Forámenes mentonianos", "choice", ("Identificables", "Superpuestos a ápices", "Asimetría", "No evaluables")),
            ("canal_mandibular", "Conducto mandibular", "choice", ("Trayecto habitual aparente", "Trayecto alterado sospechado", "No identificable")),
            ("espacios", "Espacios radiolúcidos anatómicos", "multi", ("Fosa submandibular", "Foramen mentoniano", "Conducto mandibular", "Espacio nasofaríngeo", "Espacios aéreos", "Otro", "Ninguno identificado")),
            ("fantasmas", "Superposiciones / imágenes fantasma", "choice", ("No evidentes", "Presentes", "Limitan interpretación", "No evaluables")),
        ],
    },
    {
        "title": "10 · Integración y reporte",
        "help": "Comprueba que todas las regiones se revisaron y resume los hallazgos sin convertir una observación radiográfica en diagnóstico definitivo.",
        "fields": [
            ("revision_regiones", "Regiones revisadas", "multi", REGIONS),
            ("clasificacion_global", "Clasificación global de hallazgos", "multi", ("Anatomía / estructura normal aparente", "Variación anatómica", "Hallazgo radiográfico", "Hallazgo sospechoso para correlación", "No concluyente", "No evaluable")),
            ("sintesis", "Resultado general", "choice", ("Sin hallazgos relevantes aparentes", "Con hallazgos que requieren correlación", "Con hallazgos que requieren estudio complementario", "Análisis limitado por calidad")),
            ("completitud", "Revisión sistemática", "choice", ("Completa", "Completa con limitaciones", "Incompleta")),
            ("observaciones_integracion", "Comentario opcional", "line", ()),
        ],
    },
    {
        "title": "11 · Hallazgos radiolúcidos / radiopacos",
        "help": "Describe cada hallazgo individualmente: tipo, localización, forma, límites, tamaño aparente, relación anatómica y certeza.",
        "fields": [
            ("tipos", "Tipos identificados", "multi", ("Radiolúcido", "Radiopaco", "Mixto", "Calcificación / estructura superpuesta", "Ninguno identificado")),
            ("regiones", "Regiones con hallazgos", "multi", REGIONS),
            ("formas", "Formas observadas", "multi", ("Redondeada", "Ovalada", "Irregular", "Unilocular", "Multilocular", "Lineal", "Difusa", "No determinable")),
            ("limites", "Límites observados", "multi", ("Definidos", "Corticalizados", "Difusos", "Irregulares", "No determinables")),
            ("relaciones", "Relaciones anatómicas a revisar", "multi", ("Ápice", "Corona", "Raíz", "Conducto mandibular", "Seno maxilar", "Cavidad nasal", "Cortical", "Dientes vecinos")),
            ("certeza", "Nivel de certeza", "choice", CONFIDENCE),
            ("hallazgos", "Registros individuales", "repeater", (
                ("tipo", "Tipo", ("Radiolúcido", "Radiopaco", "Mixto", "Calcificación / superposición")),
                ("region", "Localización", REGIONS),
                ("diente", "Diente FDI (si aplica)", ("No aplica",) + FDI_TEETH),
                ("forma", "Forma", ("Redondeada", "Ovalada", "Irregular", "Unilocular", "Multilocular", "Lineal", "Difusa", "No determinable")),
                ("limite", "Límites", ("Definidos", "Corticalizados", "Difusos", "Irregulares", "No determinables")),
                ("tamano", "Tamaño aparente", ("Pequeño", "Mediano", "Grande", "No medido / no evaluable")),
                ("relacion", "Relación anatómica", ("Apical", "Pericoronal", "Perirradicular", "Interradicular", "Conducto mandibular", "Seno maxilar", "Cortical", "Otra / no determinable")),
                ("certeza", "Certeza", CONFIDENCE),
            )),
        ],
    },
    {
        "title": "12 · Región periapical",
        "help": "Relaciona el ápice con el espacio periodontal y la lámina dura. Registra cada diente afectado y evita diferenciar quiste y granuloma solo por la panorámica.",
        "fields": [
            ("revision_apical", "Revisión periapical global", "choice", ("Sin cambios relevantes aparentes", "Con alteraciones", "Limitada / no evaluable")),
            ("patrones", "Patrones encontrados", "multi", ("Ensanchamiento del LPD", "Interrupción de lámina dura", "Radiolucidez periapical", "Radiopacidad periapical", "Alteración apical", "Ninguno identificado")),
            ("contexto", "Contexto dentario a considerar", "multi", ("Caries profunda", "Restauración extensa", "Traumatismo", "Tratamiento endodóntico previo", "Cambio de color / síntoma referido", "Sin antecedente conocido", "No disponible")),
            ("hallazgos", "Registros por diente", "repeater", (
                ("diente", "Diente FDI", FDI_TEETH),
                ("patron", "Patrón", ("LPD ensanchado", "Lámina dura interrumpida", "Radiolucidez apical", "Radiopacidad apical", "Cambio mixto", "Alteración morfológica apical")),
                ("tamano", "Extensión aparente", ("Pequeña", "Moderada", "Amplia", "No medible")),
                ("relacion", "Relación con ápice", ("Centrada en ápice", "Lateral al ápice", "Afecta varias raíces", "No determinada")),
                ("diferencial", "Posibilidades para correlacionar", ("Inflamatorio apical", "Condensación ósea", "Esclerosis idiopática", "Variación anatómica / superposición", "Otro / no determinable")),
                ("certeza", "Certeza", CONFIDENCE),
            )),
        ],
    },
    {
        "title": "13 · Reabsorciones radiculares",
        "help": "Busca cambios de longitud y contorno. Diferencia patrones internos, externos, apicales y cervicales; la superficie vestibular o lingual puede no determinarse.",
        "fields": [
            ("revision", "Resultado de revisión", "choice", ("Sin reabsorción aparente", "Sospecha de reabsorción", "No evaluable")),
            ("patron", "Patrón general", "multi", ("Interna", "Externa", "Apical", "Cervical externa", "No clasificable")),
            ("factores", "Antecedentes a considerar", "multi", ("Ortodoncia", "Traumatismo", "Inflamación / infección", "Diente retenido adyacente", "Sin antecedente conocido", "No disponible")),
            ("hallazgos", "Registros por diente", "repeater", (
                ("diente", "Diente FDI", FDI_TEETH),
                ("tipo", "Tipo sospechado", ("Interna", "Externa", "Apical", "Cervical externa", "No determinable")),
                ("tercio", "Localización", ("Cervical", "Medio", "Apical", "Varios tercios", "No determinable")),
                ("superficie", "Superficie", ("Vestibular", "Lingual / palatina", "Mesial", "Distal", "No determinable en panorámica")),
                ("morfologia", "Morfología", ("Ovalada / redondeada", "Irregular", "Acortamiento", "Ápice romo", "Defecto superficial", "Otra")),
                ("severidad", "Extensión aparente", ("Leve", "Moderada", "Avanzada", "No graduable")),
                ("certeza", "Certeza", CONFIDENCE),
            )),
        ],
    },
    {
        "title": "14 · Morfología radicular",
        "help": "Describe curvaturas, número, fusión, divergencia, longitud y variantes del desarrollo. No confundas una variante anatómica con una alteración adquirida.",
        "fields": [
            ("variantes", "Variantes morfológicas", "multi", ("Dilaceración", "Taurodontismo sospechado", "Raíces fusionadas", "Raíces divergentes", "Raíces convergentes", "Raíz adicional sospechada", "Número radicular atípico", "Raíces cortas aparentes", "Raíces largas aparentes", "Geminación / fusión dentaria sospechada", "Concrescencia no confirmable", "Ninguna identificada")),
            ("curvatura", "Curvatura radicular", "choice", ("Recta", "Leve", "Moderada", "Marcada / abrupta", "No evaluable")),
            ("numero_raices", "Número aparente de raíces", "choice", ("Habitual", "Aumentado", "Disminuido", "No determinable")),
            ("longitud", "Longitud radicular aparente", "choice", ("Habitual", "Corta", "Larga", "Asimétrica", "No evaluable")),
            ("camara", "Cámara pulpar / furcación", "choice", ("Morfología habitual aparente", "Cámara alargada / amplia", "Furcación apicalizada", "No evaluable")),
            ("comparacion", "Comparación con homólogos", "choice", ("Similar", "Diferente", "No hay homólogo", "No confiable por distorsión")),
        ],
    },
    {
        "title": "15 · Periodonto y relación diente-hueso",
        "help": "Evalúa conjuntamente espacio periodontal, lámina dura, cresta y furcaciones. Registra el patrón y su distribución.",
        "fields": [
            ("espacio", "Espacio del ligamento periodontal", "choice", ("Uniforme aparente", "Ensanchado apical", "Ensanchado lateral", "Ensanchado generalizado", "Irregular", "No evaluable")),
            ("lamina_dura", "Lámina dura", "choice", ("Continua", "Engrosada", "Interrumpida", "Irregular", "No identificable", "No evaluable")),
            ("cresta", "Relación UAC–cresta alveolar", "choice", ("Conservada aparente", "Aumentada", "Irregular", "No evaluable")),
            ("furcacion", "Furcaciones molares", "choice", ("Sin cambio aparente", "Radiolucidez sospechada", "No evaluables")),
            ("distribucion", "Distribución de cambios", "choice", ("Sin cambios", "Localizada", "Regional", "Generalizada", "Asimétrica")),
            ("correlacion", "Correlación clínica requerida", "choice", ("Sondaje periodontal", "Pruebas pulpares / periapicales", "Valoración oclusal", "No sugerida por imagen", "Según criterio docente")),
        ],
    },
    {
        "title": "16 · Corticales y arquitectura ósea",
        "help": "Sigue las corticales visibles y revisa continuidad, grosor, contorno, expansión, simetría y patrón trabecular.",
        "fields": [
            ("regiones", "Regiones evaluadas", "multi", ("Borde inferior mandibular derecho", "Borde inferior mandibular izquierdo", "Cuerpo mandibular", "Sínfisis", "Ángulo derecho", "Ángulo izquierdo", "Rama derecha", "Rama izquierda", "Piso del seno maxilar", "Paredes sinusales", "Piso nasal", "Paladar")),
            ("continuidad", "Continuidad cortical", "choice", ("Conservada", "Irregular", "Interrumpida", "No evaluable")),
            ("grosor", "Grosor cortical aparente", "choice", ("Habitual", "Adelgazado", "Engrosado", "Asimétrico", "No evaluable")),
            ("expansion", "Expansión ósea", "choice", ("No aparente", "Leve", "Moderada", "Marcada", "No determinable")),
            ("contorno", "Contorno óseo", "choice", ("Regular", "Irregular", "Alterado / desplazado", "No evaluable")),
            ("trabeculado", "Arquitectura trabecular", "choice", ("Habitual aparente", "Densidad aumentada", "Densidad disminuida", "Mixta / heterogénea", "No evaluable")),
            ("simetria", "Simetría bilateral", "choice", ("Simétrica", "Asimetría leve", "Asimetría moderada", "Asimetría marcada", "No confiable por posicionamiento")),
            ("alertas", "Cambios que requieren correlación", "multi", ("Adelgazamiento marcado", "Interrupción cortical", "Expansión", "Desplazamiento", "Erosión / destrucción sospechada", "Cambio trabecular focal", "Ninguno identificado")),
        ],
    },
    {
        "title": "17 · Articulaciones temporomandibulares",
        "help": "Compara ambos cóndilos y sus contornos en la imagen disponible. La panorámica ofrece una evaluación limitada de la ATM; registra diferencias aparentes y evita concluir patología sin correlación clínica o estudios indicados.",
        "fields": [
            ("atm_derecha", "ATM derecha", "choice", ("Contorno habitual aparente", "Aplanamiento aparente", "Irregularidad cortical", "Erosión sospechada", "Esclerosis sospechada", "Osteofito sospechado", "No evaluable")),
            ("atm_izquierda", "ATM izquierda", "choice", ("Contorno habitual aparente", "Aplanamiento aparente", "Irregularidad cortical", "Erosión sospechada", "Esclerosis sospechada", "Osteofito sospechado", "No evaluable")),
            ("condilos_simetria", "Comparación bilateral", "choice", ("Simétricos en forma y tamaño aparente", "Asimetría leve", "Asimetría marcada", "No confiable por posicionamiento")),
            ("espacio_articular", "Espacio articular aparente", "choice", ("Comparable bilateralmente", "Diferencia aparente", "No evaluable")),
            ("correlacion_atm", "Correlación clínica sugerida", "multi", ("Dolor referido", "Ruidos articulares", "Limitación de apertura", "Desviación al abrir", "Antecedentes de trauma", "Sin datos clínicos", "No aplica")),
            ("nota_atm", "Comentario opcional", "line", ()),
        ],
    },
    {
        "title": "18 · Vías aéreas y espacios anatómicos",
        "help": "Observa de manera descriptiva los espacios aéreos visibles y sus límites. La panorámica no permite cuantificar ni diagnosticar obstrucción; registra únicamente aspectos que ameriten correlación.",
        "fields": [
            ("nasofaringe", "Espacio nasofaríngeo", "choice", ("Sin estrechamiento aparente", "Estrechamiento aparente", "Asimetría", "No evaluable")),
            ("orofaringe", "Espacio orofaríngeo", "choice", ("Sin estrechamiento aparente", "Estrechamiento aparente", "Asimetría", "No evaluable")),
            ("paladar_blando", "Paladar blando / región posterior", "choice", ("Contorno identificable", "Contorno parcialmente visible", "No evaluable")),
            ("hioides", "Hueso hioides", "choice", ("Identificable", "Posición / superposición asimétrica aparente", "No identificable")),
            ("espacios_aereos", "Espacios aéreos superpuestos", "multi", ("Nasofaringe", "Orofaringe", "Espacio palatogloso", "Espacio palatofaríngeo", "Otros", "No evaluables")),
            ("limitacion_via", "Limitación interpretativa", "choice", ("No permite evaluación funcional", "Superposición / posicionamiento limita", "No evaluable")),
            ("correlacion_via", "¿Requiere correlación clínica?", "choice", ("Sí", "No evidente", "Según síntomas y exploración")),
            ("nota_via", "Comentario opcional", "line", ()),
        ],
    },
    {
        "title": "19 · Revisión final por regiones y hallazgos incidentales",
        "help": "Haz un último barrido de toda la imagen. Registra hallazgos incidentales o regiones no cubiertas por fases previas; describe localización, aspecto y necesidad de correlación, sin asignar diagnóstico definitivo.",
        "fields": [
            ("region_final", "Región de interés", "multi", ("Maxilar", "Mandíbula", "ATM derecha", "ATM izquierda", "Cavidad nasal", "Seno maxilar derecho", "Seno maxilar izquierdo", "Tejidos blandos", "Cervicales", "Otra región")),
            ("incidental", "Hallazgos incidentales / adicionales", "multi", ("Calcificación de tejidos blandos sospechada", "Cuerpo extraño / material radiopaco", "Asimetría no descrita previamente", "Alteración de contorno óseo", "Opacidad / radiolucidez focal", "No se identifican adicionales", "No evaluable")),
            ("descripcion_incidental", "Descripción por registro", "repeater", (
                ("tipo", "Tipo", ("Radiolúcido", "Radiopaco", "Mixto", "Calcificación sospechada", "Alteración de contorno", "Otro")),
                ("region", "Localización", ("Maxilar", "Mandíbula", "ATM derecha", "ATM izquierda", "Cavidad nasal", "Seno maxilar", "Tejidos blandos", "Cervicales", "Otra / no determinada")),
                ("forma", "Forma / apariencia", ("Redondeada", "Ovalada", "Lineal", "Irregular", "Difusa", "No determinable")),
                ("certeza", "Certeza", CONFIDENCE),
                ("correlacion", "Seguimiento", ("Correlación clínica", "Estudio complementario según criterio profesional", "Seguimiento / comparación", "Sin acción sugerida por imagen", "No determinable")),
            )),
            ("revision_completa", "Barrido final", "choice", ("Realizado", "Realizado con limitaciones", "Pendiente")),
            ("nota_final", "Comentario opcional", "line", ()),
        ],
    },

]


class PanoramicAnalysisDialog(QDialog):
    """Formulario panorámico por fases, con opciones y registro repetible de hallazgos."""

    def __init__(self, existing=None, parent=None):
        super().__init__(parent)
        self.existing = existing or {}
        self.saved_values = self.existing.get("values", {}) or {}
        self.setWindowTitle("Análisis sistemático de radiografía panorámica")
        # Adapt to the available screen area; forms remain scrollable on smaller displays.
        screen = QGuiApplication.primaryScreen()
        available = screen.availableGeometry() if screen else None
        target_width = min(1120, available.width() - 48) if available else 1120
        target_height = min(820, available.height() - 48) if available else 820
        self.setMinimumSize(640, 460)
        self.resize(max(640, target_width), max(460, target_height))
        if available:
            self.setMaximumSize(max(640, available.width() - 16), max(460, available.height() - 16))

        self.status = QComboBox()
        self.status.addItems(STATUS_OPTIONS)
        self.status.setCurrentText(self.existing.get("status", "Pendiente"))

        self.tabs = QTabWidget()
        self.tabs.setUsesScrollButtons(True)
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(False)
        self.controls = {}
        self.repeaters = {}

        intro = QLabel(
            "Completa el análisis seleccionando opciones. Usa «No evaluable» cuando la imagen "
            "no permita valorar una estructura. Los comentarios son opcionales y solo se necesitan "
            "cuando las opciones no describen el hallazgo."
        )
        intro.setWordWrap(True)

        top = QFormLayout()
        top.addRow("Estado de la actividad", self.status)

        saved_phases = self.saved_values.get("Fases", {}) if isinstance(self.saved_values, dict) else {}
        for phase_index, phase in enumerate(PANORAMIC_PHASES, start=1):
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(10, 10, 10, 10)
            page_layout.setSpacing(9)
            guidance = QLabel(phase.get("help", ""))
            guidance.setWordWrap(True)
            page_layout.addWidget(guidance)
            form = QFormLayout()
            form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
            phase_key = f"{phase_index:02d}"
            saved_section = saved_phases.get(phase_key, {}) if isinstance(saved_phases, dict) else {}
            for key, label, kind, options in phase["fields"]:
                if kind == "repeater":
                    group = QGroupBox(label)
                    group_layout = QVBoxLayout(group)
                    container = QWidget()
                    container_layout = QVBoxLayout(container)
                    container_layout.setContentsMargins(0, 0, 0, 0)
                    group_layout.addWidget(container)
                    add_button = QPushButton("＋ Agregar registro")
                    add_button.clicked.connect(
                        lambda checked=False, pk=phase_key, fk=key: self._add_repeater_row(pk, fk)
                    )
                    group_layout.addWidget(add_button)
                    form.addRow(group)
                    self.controls[(phase_key, key)] = {
                        "kind": kind, "container": container_layout, "group": group,
                        "definitions": options,
                    }
                    self.repeaters[(phase_key, key)] = []
                    for saved_row in saved_section.get(key, []) if isinstance(saved_section, dict) else []:
                        self._add_repeater_row(phase_key, key, saved_row)
                    continue

                widget = self._make_control(kind, options)
                self._load_control(widget, kind, saved_section.get(key) if isinstance(saved_section, dict) else None)
                self.controls[(phase_key, key)] = {"kind": kind, "widget": widget}
                if kind == "multi" or kind == "teeth":
                    field_label = QLabel(label)
                    field_box = QGroupBox()
                    field_layout = QVBoxLayout(field_box)
                    field_layout.addWidget(widget)
                    form.addRow(field_label, field_box)
                else:
                    form.addRow(label, widget)

            page_layout.addLayout(form)
            page_layout.addStretch(1)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(page)
            self.tabs.addTab(scroll, phase["title"])

        # Preserve older free-text records rather than silently discarding them.
        self.legacy_values = {}
        if isinstance(self.saved_values, dict) and "Fases" not in self.saved_values:
            self.legacy_values = {
                key: value for key, value in self.saved_values.items()
                if value not in (None, "", [], {})
            }

        self.observations = QTextEdit(self.existing.get("observations", ""))
        self.observations.setPlaceholderText("Opcional: solo información que no esté contemplada en las selecciones.")
        self.observations.setMinimumHeight(48)
        self.observations.setMaximumHeight(96)
        self.conclusion = QTextEdit(self.existing.get("conclusion", ""))
        self.conclusion.setPlaceholderText("Conclusión breve del estudiante. Puede apoyarse en las opciones seleccionadas.")
        self.conclusion.setMinimumHeight(52)
        self.conclusion.setMaximumHeight(112)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(intro)
        layout.addLayout(top)
        layout.addWidget(self.tabs, 1)
        layout.addWidget(QLabel("Comentario adicional (opcional)"))
        layout.addWidget(self.observations)
        layout.addWidget(QLabel("Conclusión breve"))
        layout.addWidget(self.conclusion)
        layout.addWidget(buttons)

    def _make_control(self, kind, options):
        if kind == "choice":
            combo = QComboBox()
            combo.addItem("Sin seleccionar")
            combo.addItems([str(value) for value in options])
            return combo
        if kind in ("multi", "teeth"):
            widget = QListWidget()
            widget.setSelectionMode(QListWidget.SelectionMode.NoSelection)
            widget.setMaximumHeight(118 if len(options) > 12 else 100)
            for value in options:
                item = QListWidgetItem(str(value))
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                widget.addItem(item)
            return widget
        if kind == "line":
            line = QLineEdit()
            line.setPlaceholderText("Opcional")
            return line
        raise ValueError(f"Tipo de control panorámico no reconocido: {kind}")

    def _load_control(self, widget, kind, value):
        if value in (None, ""):
            return
        if kind == "choice":
            index = widget.findText(str(value))
            if index >= 0:
                widget.setCurrentIndex(index)
        elif kind in ("multi", "teeth"):
            selected = set(value if isinstance(value, (list, tuple, set)) else [value])
            for index in range(widget.count()):
                item = widget.item(index)
                if item.text() in selected:
                    item.setCheckState(Qt.CheckState.Checked)
        elif kind == "line":
            widget.setText(str(value))

    def _add_repeater_row(self, phase_key, field_key, saved=None):
        saved = saved or {}
        descriptor = self.controls[(phase_key, field_key)]
        row_widget = QGroupBox(f"Registro {len(self.repeaters[(phase_key, field_key)]) + 1}")
        row_layout = QGridLayout(row_widget)
        row_layout.setContentsMargins(8, 8, 8, 8)
        row_controls = {}
        row_labels = {}
        for index, (key, label, options) in enumerate(descriptor["definitions"]):
            field = QComboBox()
            field.addItem("Sin seleccionar")
            field.addItems([str(option) for option in options])
            index_saved = field.findText(str(saved.get(label, saved.get(key, ""))))
            if index_saved >= 0:
                field.setCurrentIndex(index_saved)
            field.setToolTip(label)
            grid_row = index // 2
            grid_col = (index % 2) * 2
            row_layout.addWidget(QLabel(label), grid_row, grid_col)
            row_layout.addWidget(field, grid_row, grid_col + 1)
            row_controls[key] = field
            row_labels[key] = label
        remove_button = QPushButton("Quitar registro")
        remove_button.setMaximumWidth(120)
        row_layout.addWidget(remove_button, (len(descriptor["definitions"]) + 1) // 2, 0, 1, 4)
        entry = {"widget": row_widget, "controls": row_controls, "labels": row_labels}
        self.repeaters[(phase_key, field_key)].append(entry)

        def remove_row():
            entries = self.repeaters[(phase_key, field_key)]
            if entry in entries:
                entries.remove(entry)
            row_widget.setParent(None)
            row_widget.deleteLater()

        remove_button.clicked.connect(remove_row)
        descriptor["container"].addWidget(row_widget)

    def values(self):
        phases = {}
        for phase_index, phase in enumerate(PANORAMIC_PHASES, start=1):
            phase_key = f"{phase_index:02d}"
            section_values = {}
            for key, label, kind, options in phase["fields"]:
                descriptor = self.controls[(phase_key, key)]
                if kind == "repeater":
                    rows = []
                    for entry in self.repeaters[(phase_key, key)]:
                        result = {
                            entry["labels"][field_key]: combo.currentText()
                            for field_key, combo in entry["controls"].items()
                            if combo.currentText() != "Sin seleccionar"
                        }
                        if result:
                            rows.append(result)
                    if rows:
                        section_values[label] = rows
                    continue

                widget = descriptor["widget"]
                if kind == "choice":
                    value = widget.currentText()
                    if value != "Sin seleccionar":
                        section_values[label] = value
                elif kind in ("multi", "teeth"):
                    selected = [
                        widget.item(i).text()
                        for i in range(widget.count())
                        if widget.item(i).checkState() == Qt.CheckState.Checked
                    ]
                    if selected:
                        section_values[label] = selected
                elif kind == "line":
                    value = widget.text().strip()
                    if value:
                        section_values[label] = value
            if section_values:
                phases[phase_key] = {
                    "Apartado": phase["title"],
                    "Respuestas": section_values,
                }

        values = {"Fases": phases, "Formato": "panoramica_seleccionable_v1"}
        if self.legacy_values:
            values["Registro previo (formato anterior)"] = self.legacy_values
        return (
            self.status.currentText(),
            values,
            self.observations.toPlainText().strip(),
            self.conclusion.toPlainText().strip(),
        )
