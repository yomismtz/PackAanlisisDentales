from app.panoramic_form import PANORAMIC_PHASES
from app.export_report import _analysis_display_rows


def test_panoramic_protocol_has_sixteen_defined_phases():
    assert len(PANORAMIC_PHASES) == 16
    assert PANORAMIC_PHASES[0]["title"].startswith("01")
    assert PANORAMIC_PHASES[-1]["title"].startswith("16")


def test_panoramic_phase_fields_have_unique_keys_and_supported_controls():
    supported = {"choice", "multi", "teeth", "line", "repeater"}
    for phase in PANORAMIC_PHASES:
        keys = [field[0] for field in phase["fields"]]
        assert len(keys) == len(set(keys))
        for key, label, kind, options in phase["fields"]:
            assert key and label
            assert kind in supported
            assert isinstance(options, tuple)


def test_panoramic_report_flattens_selected_values_and_repeatable_findings():
    values = {
        "Fases": {
            "01": {
                "Apartado": "01 · Calidad técnica",
                "Respuestas": {
                    "Aceptación de la imagen": "Adecuada",
                    "Errores técnicos identificados": ["Rotación", "Movimiento"],
                },
            },
            "11": {
                "Apartado": "11 · Hallazgos radiolúcidos / radiopacos",
                "Respuestas": {
                    "Registros individuales": [
                        {
                            "Tipo": "Radiolúcido",
                            "Localización": "Mandíbula posterior derecha",
                            "Certeza": "Sospecha",
                        }
                    ]
                },
            },
        }
    }
    rows, is_cephalometric = _analysis_display_rows(
        "panoramic_systematic", {"values": values}
    )
    assert not is_cephalometric
    rendered = dict(rows)
    assert rendered["01 · Calidad técnica · Aceptación de la imagen"] == "Adecuada"
    assert rendered["01 · Calidad técnica · Errores técnicos identificados"] == "Rotación · Movimiento"
    assert rendered["11 · Hallazgos radiolúcidos / radiopacos · Registros individuales 1 · Tipo"] == "Radiolúcido"
