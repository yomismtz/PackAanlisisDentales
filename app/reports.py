"""Academic report module selection and completion rules."""
REPORT_MODULES = {
    "ceph": {
        "title": "Análisis cefalométrico",
        "analysis_keys": ("steiner",),
        "media_slots": ("ceph_lateral",),
    },
    "pan": {
        "title": "Análisis panorámico",
        "analysis_keys": ("panoramic_systematic", "levandoski"),
        "media_slots": ("panoramic",),
    },
    "models": {
        "title": "Análisis de modelos",
        "analysis_keys": ("intermaxillary", "moyers", "tanaka_johnston", "little_upper", "little_lower"),
        "media_slots": (
            "model_upper_right", "model_upper_left", "model_upper_front", "model_upper_occlusal",
            "model_lower_right", "model_lower_left", "model_lower_front", "model_lower_occlusal",
            "model_both_right", "model_both_left", "model_both_front", "moyers_periapical",
        ),
    },
    "age": {
        "title": "Análisis de edad",
        "analysis_keys": ("dental_age", "cervical_maturation"),
        "media_slots": ("panoramic", "ceph_lateral"),
    },
    "photos": {
        "title": "Análisis fotográfico",
        "analysis_keys": ("facial_frontal", "facial_profile", "facial_midlines", "facial_levels",
                         "facial_contour", "powell", "smile", "facial_projections", "facial_symmetry"),
        "media_slots": ("extra_frontal", "extra_profile", "extra_smiling"),
    },
}


def completed_keys(analyses, module_id):
    """Return only completed analysis records belonging to a report module."""
    if module_id not in REPORT_MODULES:
        raise KeyError(f"Módulo de informe desconocido: {module_id}")
    return tuple(
        key for key in REPORT_MODULES[module_id]["analysis_keys"]
        if analyses.get(key, {}).get("status") == "Completo"
    )


def available_modules(analyses):
    """Return module IDs that contain at least one completed analysis."""
    return tuple(
        module_id for module_id in REPORT_MODULES
        if completed_keys(analyses, module_id)
    )


def build_report_snapshot(analyses, selected_modules):
    """Create a stable snapshot containing only selected, completed analyses."""
    selected = tuple(dict.fromkeys(selected_modules))
    if not selected:
        raise ValueError("Selecciona al menos un módulo para el informe.")
    unknown = [module_id for module_id in selected if module_id not in REPORT_MODULES]
    if unknown:
        raise ValueError("La selección contiene módulos no reconocidos.")
    snapshot = {}
    for module_id in selected:
        keys = completed_keys(analyses, module_id)
        if not keys:
            continue
        snapshot[module_id] = {
            key: analyses[key] for key in keys
        }
    if not snapshot:
        raise ValueError("No hay análisis completos en los módulos seleccionados.")
    return snapshot
