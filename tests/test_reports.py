import pytest

from app.reports import (
    REPORT_MODULES,
    available_modules,
    build_report_snapshot,
    completed_keys,
)


def complete_panorama_record():
    from app.panoramic_form import PANORAMIC_PHASES
    phases = {}
    for index, phase in enumerate(PANORAMIC_PHASES, start=1):
        answers = {
            label: options[0]
            for _, label, kind, options in phase["fields"]
            if kind == "choice" and options
        }
        phases[f"{index:02d}"] = {"Apartado": phase["title"], "Respuestas": answers}
    return {"status": "Completo", "values": {"Fases": phases}}


def complete_steiner_record():
    from app.cephalometry import REFERENCES
    return {
        "status": "Completo",
        "values": {
            "Resultados": {ref.key: {"valor": 1.0} for ref in REFERENCES}
        },
    }


def complete_nolla_record():
    return {
        "status": "Completo",
        "values": {
            "Sexo": "Femenino",
            "Edad dental estimada · años": 8.5,
            **{f"Estadio OD {tooth}": 5 for tooth in ("17", "16", "15", "14", "13", "12", "11")},
        },
    }


def test_report_modules_include_photos_and_four_core_sections():
    assert tuple(REPORT_MODULES) == ("ceph", "pan", "models", "age", "photos")


def test_only_validated_completed_analysis_is_available_in_a_module():
    data = {
        "panoramic_systematic": complete_panorama_record(),
        "levandoski": {"status": "Completo", "values": {"Puntos": {"Cd_R": [1, 2]}}},
        "steiner": {"status": "Pendiente"},
    }
    assert completed_keys(data, "pan") == ("panoramic_systematic",)
    assert available_modules(data) == ("pan",)


def test_status_complete_without_required_data_is_not_report_complete():
    data = {
        "panoramic_systematic": {"status": "Completo", "values": {}},
        "levandoski": {"status": "Completo", "values": {}},
    }
    assert completed_keys(data, "pan") == ()
    assert available_modules(data) == ()


def test_snapshot_includes_only_selected_validated_completed_analysis_records():
    data = {
        "steiner": complete_steiner_record(),
        "panoramic_systematic": complete_panorama_record(),
        "levandoski": {"status": "En proceso", "values": {"Puntos": {"SL": 53}}},
        "dental_age": complete_nolla_record(),
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
        build_report_snapshot({"steiner": complete_steiner_record()}, ["invalid"])


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
        output, patient, "Estudiante Prueba", "docente@institucion.edu",
        ["ceph"], snapshot, [],
    )
    assert created == output
    assert output.is_file()
    assert output.read_bytes().startswith(b"%PDF")
    assert output.stat().st_size > 1000


def test_academic_report_rejects_empty_module_selection(tmp_path):
    with pytest.raises(ValueError, match="Selecciona"):
        export_academic_report(
            tmp_path / "empty.pdf", {}, "Estudiante", "docente@institucion.edu",
            [], {}, [],
        )


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
        "Estudiante", "docente@institucion.edu", ["ceph"], snapshot,
        [{
            "slot_key": "ceph_lateral",
            "current_path": str(image_path),
            "filename": "ceph.png",
            "created_at": "2026-01-01",
        }],
    )
    assert output.is_file()
    assert output.stat().st_size > 1000


def test_all_report_palettes_have_their_matching_bird_icon():
    from app.theme import REPORT_PALETTES, report_bird_path

    assert len(REPORT_PALETTES) == 10
    from PIL import Image

    for palette_id, palette in REPORT_PALETTES.items():
        assert palette["name"]
        icon_path = report_bird_path(palette_id)
        assert icon_path.is_file()
        with Image.open(icon_path) as icon:
            assert icon.format == "PNG"
            icon.verify()
