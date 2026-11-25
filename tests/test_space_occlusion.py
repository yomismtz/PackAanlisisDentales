from app.catalog import ANALYSES
from app.completion import analysis_completion_issue
from app.reports import REPORT_MODULES
from app.space_analysis import CAREY_TEETH, calculate_carey_arch, polyline_length
from app.export_report import _analysis_display_rows


def make_carey_points(teeth, width=10.0):
    points = {}
    for index, tooth in enumerate(teeth):
        x = index * width
        points[f"{tooth}_M"] = (x, 0.0)
        points[f"{tooth}_D"] = (x + width, 0.0)
    return points


def make_carey_values():
    arches = {}
    for arch in ("superior", "inferior"):
        arches[arch] = {
            "Puntos": make_carey_points(CAREY_TEETH[arch]),
            "Recorrido disponible": [[0.0, 0.0], [120.0, 0.0]],
        }
    return {
        "Método": "Carey · dentición permanente",
        "Unidad": "px_relativos",
        "Arcadas": arches,
    }


def baume_values():
    labels = (
        "Tipo de arcada superior", "Tipo de arcada inferior",
        "Espacio primate superior derecho", "Espacio primate superior izquierdo",
        "Espacio primate inferior derecho", "Espacio primate inferior izquierdo",
        "Plano terminal derecho", "Plano terminal izquierdo",
    )
    return {"Evaluación estructurada": {label: "No evaluable" for label in labels}}


def intermaxillary_values():
    labels = (
        "Relación molar derecha", "Relación molar izquierda",
        "Relación canina derecha", "Relación canina izquierda", "Overjet",
        "Sobremordida vertical", "Relación transversal",
        "Línea media superior", "Línea media inferior",
        "Desviación mandibular al cierre",
    )
    return {"Evaluación estructurada": {label: "No evaluable" for label in labels}}


def test_polyline_length_sums_consecutive_segments():
    assert polyline_length([(0, 0), (3, 0), (3, 4)]) == 7.0


def test_polyline_length_requires_two_distinct_points():
    assert polyline_length([(0, 0)]) is None
    assert polyline_length([(1, 1), (1, 1)]) is None


def test_carey_compares_available_perimeter_with_ten_tooth_widths():
    result = calculate_carey_arch(
        make_carey_points(CAREY_TEETH["superior"]),
        [(0, 0), (120, 0)],
        CAREY_TEETH["superior"],
    )
    assert result["available_px"] == 120.0
    assert result["required_px"] == 100.0
    assert result["discrepancy_px"] == 20.0
    assert result["classification"] == "Exceso de espacio relativo"


def test_carey_reports_deficit_without_assigning_treatment():
    result = calculate_carey_arch(
        make_carey_points(CAREY_TEETH["inferior"]),
        [(0, 0), (90, 0)],
        CAREY_TEETH["inferior"],
    )
    assert result["discrepancy_px"] == -10.0
    assert result["classification"] == "Déficit de espacio relativo"
    assert "extracción" not in result["classification"].lower()


def test_carey_returns_pending_for_missing_tooth_width_or_trace():
    assert calculate_carey_arch(
        {}, [(0, 0), (100, 0)], CAREY_TEETH["superior"]
    ) is None
    assert calculate_carey_arch(
        make_carey_points(CAREY_TEETH["superior"]),
        [(0, 0)], CAREY_TEETH["superior"]
    ) is None


def test_carey_completion_requires_both_arches_and_full_measurements():
    assert analysis_completion_issue("nance_carey", make_carey_values()) is None
    values = make_carey_values()
    values["Arcadas"]["inferior"]["Recorrido disponible"] = []
    assert "perímetro" in analysis_completion_issue("nance_carey", values).lower()


def test_baume_allows_explicit_non_evaluable_fields():
    assert analysis_completion_issue("baume", baume_values()) is None
    values = baume_values()
    values["Evaluación estructurada"]["Plano terminal derecho"] = ""
    assert "plano terminal derecho" in analysis_completion_issue("baume", values).lower()


def test_intermaxillary_requires_all_planes_and_bilateral_relations():
    assert analysis_completion_issue("intermaxillary", intermaxillary_values()) is None
    values = intermaxillary_values()
    values["Evaluación estructurada"].pop("Relación molar izquierda")
    assert "relación molar izquierda" in analysis_completion_issue("intermaxillary", values).lower()


def test_models_report_includes_carey_baume_and_intermaxillary():
    keys = set(REPORT_MODULES["models"]["analysis_keys"])
    assert {"nance_carey", "baume", "intermaxillary"} <= keys
    assert "Carey" in ANALYSES["nance_carey"]


def test_carey_pdf_summary_omits_raw_landmark_coordinates():
    record = {"values": make_carey_values()}
    rows, has_ceph_table = _analysis_display_rows("nance_carey", record)
    rendered = " ".join(str(value) for row in rows for value in row)
    assert not has_ceph_table
    assert "120.0" in rendered
    assert "15_M" not in rendered
    assert "Recorrido disponible" not in rendered


def test_baume_pdf_summary_exports_classifications_only():
    rows, _ = _analysis_display_rows("baume", {"values": baume_values()})
    rendered = " ".join(str(value) for row in rows for value in row)
    assert "Tipo de arcada superior" in rendered
    assert "No evaluable" in rendered
    assert "Evaluación estructurada" not in rendered


def test_intermaxillary_pdf_summary_exports_structured_findings():
    rows, _ = _analysis_display_rows("intermaxillary", {"values": intermaxillary_values()})
    rendered = " ".join(str(value) for row in rows for value in row)
    assert "Relación molar derecha" in rendered
    assert "Sobremordida vertical" in rendered
