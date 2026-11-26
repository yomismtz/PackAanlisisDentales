"""Completion validation for AVIS analyses."""
def _filled(value):
    if value is None: return False
    if isinstance(value,str): return bool(value.strip())
    if isinstance(value,(list,tuple,dict,set)): return bool(value)
    return True

def analysis_completion_issue(key, values):
    values = values if isinstance(values,dict) else {}
    if key == "steiner":
        from .cephalometry import REFERENCES
        results=values.get("Resultados",{}) or {}
        missing=[ref.key for ref in REFERENCES if not isinstance(results.get(ref.key),dict) or not _filled(results[ref.key].get("valor"))]
        return "Steiner: faltan resultados o calibración para "+", ".join(missing)+"." if missing else None
    if key in ("little_upper","little_lower"):
        from .little import CONTACTS
        points=values.get("Puntos",{}) or {}
        if any(code not in points for code,_ in CONTACTS) or not _filled(values.get("Indice de Little px relativos")):
            return "Little requiere los seis puntos para completar los cinco segmentos."
        return None
    if key in ("moyers","tanaka_johnston"):
        points=values.get("Puntos",{}) or {}
        inc={"42_M","42_D","41_M","41_D","31_M","31_D","32_M","32_D"}
        if inc-set((points.get("incisors") or {}).keys()): return "Marca los cuatro incisivos inferiores."
        for arch in ("upper","lower"):
            if {"ref_M","ref_D","lat_R","mol_R","lat_L","mol_L"}-set((points.get(arch) or {}).keys()):
                return "Completa los puntos de referencia de ambas arcadas."
        traces=values.get("Recorridos",{}) or {}
        if any(len((traces.get(arch,{}) or {}).get(side,[]) or [])<2 for arch in ("upper","lower") for side in ("Derecho","Izquierdo")):
            return "Traza los cuatro recorridos curvos del espacio disponible."
        results=values.get("Resultado por hemiarcada",{}) or {}
        expected=("Superior · Derecho","Superior · Izquierdo","Inferior · Derecho","Inferior · Izquierdo")
        if any(results.get(label) in (None,"","Pendiente") for label in expected): return "Falta clasificar alguna hemiarcada."
        if key=="moyers" and values.get("Sexo") not in ("Femenino","Masculino"): return "Selecciona el sexo requerido por Moyers."
        return None
    if key=="dental_age":
        stages=[value for label,value in values.items() if label.startswith("Estadio OD ")]
        if len(stages)!=7 or any(not _filled(x) for x in stages): return "Nolla requiere los siete estadios."
        if values.get("Sexo") not in ("Femenino","Masculino") or not _filled(values.get("Edad dental estimada · años")):
            return "Nolla requiere sexo y una edad estimada dentro del rango de referencia."
        return None
    if key=="cervical_maturation":
        return None if values.get("Estadio vertebral") in {"CS1","CS2","CS3","CS4","CS5","CS6","No evaluable"} else "Selecciona un estadio CS1–CS6 o registra que la imagen no es evaluable."
    if key=="levandoski":
        from .levandoski import POINTS
        points=values.get("Puntos",{}) or {}
        missing=[code for code,_ in POINTS if code not in points]
        return "Levandoski requiere todos los puntos anatómicos: "+", ".join(missing)+"." if missing else None
    if key=="panoramic_systematic":
        from .panoramic_form import PANORAMIC_PHASES
        phases=values.get("Fases",{}) or {}; missing=[]
        for i,phase in enumerate(PANORAMIC_PHASES,1):
            answers=(phases.get(f"{i:02d}",{}) or {}).get("Respuestas",{}) or {}
            pending=[]
            for _,label,kind,options in phase["fields"]:
                if kind=="choice" and not _filled(answers.get(label)):
                    pending.append(label)
                elif kind=="repeater":
                    for row_number,row in enumerate(answers.get(label,[]) or [],1):
                        if not isinstance(row,dict) or any(not _filled(row.get(definition[1])) for definition in options):
                            return f"Panorámica: completa o elimina el registro {row_number} de «{label}» en {phase['title']}."
            if pending: missing.append(phase["title"]+": "+", ".join(pending))
        return "Panorámica: faltan respuestas obligatorias en "+"; ".join(missing[:3])+("…" if len(missing)>3 else "") if missing else None
    if key == "nance_carey":
        if values.get("Método") != "Carey · dentición permanente":
            return "Carey requiere seleccionar el método de dentición permanente."
        from .space_analysis import (
            CAREY_TEETH, carey_point_order, calculate_carey_arch,
        )
        arches = values.get("Arcadas", {}) or {}
        for arch in ("superior", "inferior"):
            data = arches.get(arch, {}) or {}
            points = data.get("Puntos", {}) or {}
            trace = data.get("Recorrido disponible", []) or []
            required = set(carey_point_order(arch))
            missing = required - set(points)
            if missing:
                return f"Carey: faltan puntos mesiales/distales en la secuencia de la arcada {arch}."
            if len(trace) < 2:
                return (
                    f"Carey: agrega al menos dos puntos para iniciar el recorrido "
                    f"del perímetro de la arcada {arch}; puedes añadir tantos como "
                    "necesites para seguir su curvatura."
                )
            if calculate_carey_arch(points, trace, CAREY_TEETH[arch]) is None:
                return f"Carey: no se pudo calcular la comparación geométrica de la arcada {arch}."
        return None
    if key == "baume":
        expected = (
            "Tipo de arcada superior", "Tipo de arcada inferior",
            "Espacio primate superior derecho", "Espacio primate superior izquierdo",
            "Espacio primate inferior derecho", "Espacio primate inferior izquierdo",
            "Plano terminal derecho", "Plano terminal izquierdo",
        )
        recorded = values.get("Evaluación estructurada", {}) or {}
        missing = [label for label in expected if not _filled(recorded.get(label)) or recorded.get(label) == "Seleccionar"]
        return "Baumé: completa o registra como no evaluable: " + ", ".join(missing) + "." if missing else None
    if key == "intermaxillary":
        expected = (
            "Relación molar derecha", "Relación molar izquierda",
            "Relación canina derecha", "Relación canina izquierda", "Overjet",
            "Sobremordida vertical", "Relación transversal",
            "Línea media superior", "Línea media inferior",
            "Desviación mandibular al cierre",
        )
        recorded = values.get("Evaluación estructurada", {}) or {}
        missing = [label for label in expected if not _filled(recorded.get(label)) or recorded.get(label) == "Seleccionar"]
        return "Intermaxilar: completa o registra como no evaluable: " + ", ".join(missing) + "." if missing else None
    photo_keys={"facial_frontal","facial_profile","facial_midlines","facial_levels","facial_contour","powell","smile","facial_projections","facial_symmetry"}
    if key in photo_keys:
        from .photo_analysis import CONFIG,SMILE_FIELDS,CONTOUR_FIELDS,MIDLINE_FIELDS,LEVEL_FIELDS
        points=values.get("Puntos",{}) or {}
        missing=[code for code,_ in CONFIG[key]["points"] if code not in points]
        if missing: return "Fotografía: faltan puntos anatómicos: "+", ".join(missing[:6])+("…" if len(missing)>6 else "")+"."
        visual=values.get("Evaluación visual",{}) or {}
        fields=SMILE_FIELDS if key=="smile" else CONTOUR_FIELDS if key=="facial_contour" else MIDLINE_FIELDS if key=="facial_midlines" else LEVEL_FIELDS if key=="facial_levels" else {}
        pending=[label for label in fields if visual.get(label) in (None,"","Sin evaluar")]
        if pending: return "Fotografía: completa los criterios visuales: "+", ".join(pending[:5])+("…" if len(pending)>5 else "")+"."
        return None
    return _generic_completion_issue(key,values)

def _generic_completion_issue(key,values):
    from .analysis_forms import fields_for
    missing=[label for label,_ in fields_for(key) if not _filled(values.get(label))]
    return "Completa los campos requeridos: "+", ".join(missing[:5])+("…" if len(missing)>5 else "")+"." if missing else None

def is_analysis_complete(key,record):
    return isinstance(record,dict) and record.get("status")=="Completo" and analysis_completion_issue(key,record.get("values",{})) is None
