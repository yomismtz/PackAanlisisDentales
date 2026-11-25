from app.catalog import ANALYSES
from app.completion import analysis_completion_issue
from app.reports import REPORT_MODULES
from app.space_analysis import (
    CAREY_TEETH, carey_point_order, calculate_carey_arch,
    next_missing_carey_point, polyline_length,
)
from app.export_report import _analysis_display_rows
from app.occlusion_analysis import BaumeDialog, IntermaxillaryDialog
from app.ui import Workspace


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
        points = make_carey_points(CAREY_TEETH[arch])
        trace = [[0.0, 0.0], [30.0, 0.0], [60.0, 0.0], [90.0, 0.0], [120.0, 0.0]]
        result = calculate_carey_arch(points, trace, CAREY_TEETH[arch])
        arches[arch] = {
            "Puntos": points,
            "Recorrido disponible": trace,
            "Espacio disponible px": result["available_px"],
            "Espacio requerido px": result["required_px"],
            "Discrepancia px": result["discrepancy_px"],
            "Resultado": result["classification"],
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




def test_carey_landmark_sequence_is_mesial_then_distal_for_each_tooth():
    order = carey_point_order("superior")
    assert order[:6] == ("15_M", "15_D", "14_M", "14_D", "13_M", "13_D")
    assert order[-4:] == ("24_M", "24_D", "25_M", "25_D")
    assert len(order) == 20


def test_next_missing_carey_point_advances_in_the_required_order():
    points = {"15_M": (1, 1), "15_D": (2, 2), "14_M": (3, 3)}
    assert next_missing_carey_point(points, "superior") == "14_D"
    points.update({"14_D": (4, 4)})
    assert next_missing_carey_point(points, "superior") == "13_M"
    complete = {
        code: (index, index)
        for index, code in enumerate(carey_point_order("inferior"))
    }
    assert next_missing_carey_point(complete, "inferior") is None


def test_carey_perimeter_accepts_two_points_and_keeps_additional_points():
    points = make_carey_points(CAREY_TEETH["superior"])
    two_points = calculate_carey_arch(
        points, [(0, 0), (100, 0)], CAREY_TEETH["superior"]
    )
    assert two_points is not None
    assert two_points["available_px"] == 100.0

    dense_curve = [
        (0, 0), (10, 6), (20, 12), (30, 18), (40, 22),
        (50, 24), (60, 22), (70, 18), (80, 12), (90, 6), (100, 0),
    ]
    dense_result = calculate_carey_arch(
        points, dense_curve, CAREY_TEETH["superior"]
    )
    assert dense_result is not None
    assert dense_result["available_px"] == round(polyline_length(dense_curve), 2)
    assert dense_result["available_px"] > 100.0


def test_curved_perimeter_length_follows_each_consecutive_point():
    curve = [(0, 0), (20, 10), (40, 20), (60, 10), (80, 0)]
    assert polyline_length(curve) > 80.0


def test_carey_completion_accepts_two_point_minimum_without_a_fixed_maximum():
    values = make_carey_values()
    values["Arcadas"]["superior"]["Recorrido disponible"] = [[0, 0], [100, 0]]
    assert analysis_completion_issue("nance_carey", values) is None


def test_carey_compares_available_perimeter_with_ten_tooth_widths():
    result = calculate_carey_arch(
        make_carey_points(CAREY_TEETH["superior"]),
        [(0, 0), (30, 0), (60, 0), (90, 0), (120, 0)],
        CAREY_TEETH["superior"],
    )
    assert result["available_px"] == 120.0
    assert result["required_px"] == 100.0
    assert result["discrepancy_px"] == 20.0
    assert result["classification"] == "Exceso de espacio relativo"


def test_carey_reports_deficit_without_assigning_treatment():
    result = calculate_carey_arch(
        make_carey_points(CAREY_TEETH["inferior"]),
        [(0, 0), (22.5, 0), (45, 0), (67.5, 0), (90, 0)],
        CAREY_TEETH["inferior"],
    )
    assert result["discrepancy_px"] == -10.0
    assert result["classification"] == "Déficit de espacio relativo"
    assert "extracción" not in result["classification"].lower()


def test_carey_returns_pending_for_missing_tooth_width_or_trace():
    assert calculate_carey_arch(
        {}, [(0, 0), (25, 0), (50, 0), (75, 0), (100, 0)], CAREY_TEETH["superior"]
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
    values["Evaluación estructurada"]["Plano terminal derecho"] = "Seleccionar"
    assert "plano terminal derecho" in analysis_completion_issue("baume", values).lower()


def test_intermaxillary_requires_all_planes_and_bilateral_relations():
    assert analysis_completion_issue("intermaxillary", intermaxillary_values()) is None
    values = intermaxillary_values()
    values["Evaluación estructurada"].pop("Relación molar izquierda")
    assert "relación molar izquierda" in analysis_completion_issue("intermaxillary", values).lower()
    values = intermaxillary_values()
    values["Evaluación estructurada"]["Overjet"] = "Seleccionar"
    assert "overjet" in analysis_completion_issue("intermaxillary", values).lower()


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


def test_dedicated_dialogs_and_workspace_routing_import():
    assert BaumeDialog.TITLE.endswith("Baumé")
    assert IntermaxillaryDialog.TITLE.endswith("intermaxilares")
    assert callable(Workspace.open_analysis_item)


def test_baume_form_exposes_both_arches_and_bilateral_terminal_planes():
    labels = {
        label
        for _, definitions in BaumeDialog.GROUPS
        for label, _ in definitions
    }
    assert {
        "Tipo de arcada superior", "Tipo de arcada inferior",
        "Plano terminal derecho", "Plano terminal izquierdo",
    } <= labels


def test_intermaxillary_form_exposes_sagittal_vertical_and_transverse_fields():
    labels = {
        label
        for _, definitions in IntermaxillaryDialog.GROUPS
        for label, _ in definitions
    }
    assert {
        "Relación molar derecha", "Relación canina izquierda",
        "Overjet", "Sobremordida vertical", "Relación transversal",
        "Línea media superior", "Línea media inferior",
    } <= labels


def test_occlusion_dialog_saves_selected_text_and_not_placeholder():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    dialog = BaumeDialog(images={})
    initial = dialog.values()[1]["Evaluación estructurada"]
    assert all(value == "" for value in initial.values())

    dialog.fields["Tipo de arcada superior"].setCurrentIndex(1)
    saved = dialog.values()[1]["Evaluación estructurada"]
    assert saved["Tipo de arcada superior"] == "Tipo I · con espacios fisiológicos"
    assert saved["Tipo de arcada inferior"] == ""
    dialog.close()
    app.processEvents()
