from app.database import Database

def test_patient_media_and_analysis_roundtrip(tmp_path):
    db=Database(tmp_path/"test.sqlite3")
    p=db.create_patient("Paciente Prueba",birth_date="2012-03-04",sex="Femenino")
    assert db.get_patient(p["id"])["full_name"]=="Paciente Prueba"
    db.add_media(p["id"],"ceph_lateral","original.dcm","original.dcm","original.dcm")
    assert db.get_media_for_slot(p["id"],"ceph_lateral")["filename"]=="original.dcm"
    db.save_analysis(p["id"],"steiner","En proceso",{"SNA":"82"},"Nota","Revisión")
    saved=db.analysis_for_patient(p["id"])["steiner"]
    assert saved["values"]["SNA"]=="82"
    assert saved["conclusion"]=="Revisión"
    assert db.counts_for_patient(p["id"])["analyses"]==1


def test_report_snapshot_and_delivery_metadata_roundtrip(tmp_path):
    db=Database(tmp_path/"test.sqlite3")
    patient=db.create_patient("Estudiante Paciente")
    saved=db.save_report(
        patient["id"],
        "Estudiante de prueba",
        "docente@universidad.edu",
        ["ceph","pan"],
        {"ceph":{"steiner":{"status":"Completo","values":{"SNA":82}}}},
        tmp_path/"informe.pdf",
    )
    assert saved["student_name"]=="Estudiante de prueba"
    assert saved["teacher_email"]=="docente@universidad.edu"
    assert saved["selected_modules"]==["ceph","pan"]
    assert saved["analyses"]["ceph"]["steiner"]["values"]["SNA"]==82
    assert saved["status"]=="PDF generado · pendiente de envío"
    assert db.reports_for_patient(patient["id"])[0]["id"]==saved["id"]


def test_carey_measurements_and_conclusion_survive_patient_roundtrip(tmp_path):
    from app.completion import analysis_completion_issue
    from app.space_analysis import CAREY_TEETH, calculate_carey_arch

    db = Database(tmp_path / "carey.sqlite3")
    patient = db.create_patient("Paciente Carey")

    arches = {}
    for arch in ("superior", "inferior"):
        points = {}
        for index, tooth in enumerate(CAREY_TEETH[arch]):
            x = index * 10.0
            points[f"{tooth}_M"] = (x, 0.0)
            points[f"{tooth}_D"] = (x + 10.0, 0.0)
        trace = [[0.0, 0.0], [22.5, 0.0], [45.0, 0.0], [67.5, 0.0], [90.0, 0.0]]
        result = calculate_carey_arch(points, trace, CAREY_TEETH[arch])
        assert result is not None
        arches[arch] = {
            "Puntos": points,
            "Recorrido disponible": trace,
            "Espacio disponible px": result["available_px"],
            "Espacio requerido px": result["required_px"],
            "Discrepancia px": result["discrepancy_px"],
            "Cobertura dentaria (%)": result["coverage_percent"],
            "Déficit relativo (%)": result["deficit_percent"],
            "Excedente relativo (%)": result["excess_percent"],
            "Resultado": result["classification"],
            "Conclusión automática": result["conclusion"],
        }

    values = {
        "Método": "Carey · dentición permanente",
        "Unidad": "px_relativos",
        "Arcadas": arches,
    }
    assert analysis_completion_issue("nance_carey", values) is None

    db.save_analysis(
        patient["id"], "nance_carey", "Completo", values,
        "Observación de prueba", "Conclusión profesional de prueba",
    )

    # Re-read as the expediente does when the analysis is opened again.
    saved = db.analysis_for_patient(patient["id"])["nance_carey"]
    restored = saved["values"]["Arcadas"]["inferior"]
    assert restored["Puntos"] == arches["inferior"]["Puntos"]
    assert restored["Recorrido disponible"] == arches["inferior"]["Recorrido disponible"]
    assert restored["Déficit relativo (%)"] == 10.0
    assert "cubre 90.0%" in restored["Conclusión automática"]
    assert saved["observations"] == "Observación de prueba"
    assert saved["conclusion"] == "Conclusión profesional de prueba"
