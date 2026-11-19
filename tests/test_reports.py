import pytest

from app.reports import (
    REPORT_MODULES,
    available_modules,
    build_report_snapshot,
    completed_keys,
)


def test_report_modules_match_the_requested_four_sections():
    assert tuple(REPORT_MODULES) == ("ceph", "pan", "models", "age")


def test_only_completed_analysis_is_available_in_a_module():
    data = {
        "panoramic_systematic": {"status": "Completo"},
        "levandoski": {"status": "En proceso"},
        "steiner": {"status": "Pendiente"},
    }
    assert completed_keys(data, "pan") == ("panoramic_systematic",)
    assert available_modules(data) == ("pan",)


def test_snapshot_includes_only_selected_completed_analysis_records():
    data = {
        "steiner": {"status": "Completo", "values": {"SNA": 82}},
        "panoramic_systematic": {"status": "Completo", "values": {"Calidad": "Adecuada"}},
        "levandoski": {"status": "En proceso", "values": {"SL": 53}},
        "dental_age": {"status": "Completo", "values": {"Nolla": 58}},
    }
    result = build_report_snapshot(data, ["ceph", "pan", "age"])
    assert set(result) == {"ceph", "pan", "age"}
    assert set(result["pan"]) == {"panoramic_systematic"}
    assert "levandoski" not in result["pan"]
    assert "models" not in result


def test_snapshot_rejects_empty_selection_or_incomplete_only_modules():
    with pytest.raises(ValueError):
        build_report_snapshot({}, [])
    with pytest.raises(ValueError):
        build_report_snapshot({"steiner": {"status": "En proceso"}}, ["ceph"])


def test_snapshot_rejects_unknown_module():
    with pytest.raises(ValueError):
        build_report_snapshot({"steiner": {"status": "Completo"}}, ["invalid"])

from pathlib import Path

from app.export_report import export_academic_report


def test_academic_report_creates_pdf_for_selected_completed_modules(tmp_path):
    output = tmp_path / "YSM_informe.pdf"
    patient = {
        "full_name": "Paciente Prueba",
        "record_number": "PAD-TEST",
        "birth_date": "2012-01-01",
        "sex": "Femenino",
    }
    snapshot = {
        "ceph": {
            "steiner": {
                "status": "Completo",
                "values": {
                    "Resultados": {
                        "SNA": {
                            "valor": 82.0,
                            "norma": "82° ± 2°",
                            "clasificación": "Dentro de norma",
                            "interpretación": "Posición maxilar dentro del intervalo.",
                        }
                    }
                },
                "observations": "Registro de prueba",
                "conclusion": "Conclusión de prueba",
            }
        }
    }
    created = export_academic_report(
        output,
        patient,
        "Estudiante Prueba",
        "docente@institucion.edu",
        ["ceph"],
        snapshot,
        [],
    )
    assert created == output
    assert output.is_file()
    assert output.read_bytes().startswith(b"%PDF")
    assert output.stat().st_size > 1000


def test_academic_report_rejects_empty_module_selection(tmp_path):
    try:
        export_academic_report(
            tmp_path / "empty.pdf", {}, "Estudiante", "docente@institucion.edu",
            [], {}, [],
        )
    except ValueError as exc:
        assert "Selecciona" in str(exc)
    else:
        raise AssertionError("An empty report selection must be rejected.")


def test_academic_report_renders_saved_cephalometric_landmarks(tmp_path):
    from PIL import Image

    image_path = tmp_path / "ceph.png"
    Image.new("RGB", (640, 480), "white").save(image_path)
    output = tmp_path / "YSM_ceph_trazado.pdf"
    snapshot = {
        "ceph": {
            "steiner": {
                "status": "Completo",
                "values": {
                    "Puntos": {
                        "S": [80, 100], "N": [250, 100], "A": [300, 170],
                        "B": [310, 230], "D": [305, 250], "Ar": [150, 180],
                        "Go": [330, 310], "Gn": [390, 330], "Me": [380, 370],
                        "Pog": [400, 355], "Co": [120, 160],
                        "U1_apex": [340, 180], "U1_tip": [360, 250],
                    },
                    "Resultados": {},
                },
            }
        }
    }
    export_academic_report(
        output,
        {"full_name": "Paciente", "record_number": "PAD-01"},
        "Estudiante",
        "docente@institucion.edu",
        ["ceph"],
        snapshot,
        [{
            "slot_key": "ceph_lateral",
            "current_path": str(image_path),
            "filename": "ceph.png",
            "created_at": "2026-01-01",
        }],
    )
    assert output.is_file()
    assert output.stat().st_size > 1000
