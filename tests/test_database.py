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
            points[f"{tooth}_M"] = [x, 0.0]
            points[f"{tooth}_D"] = [x + 10.0, 0.0]
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



def test_schema_migration_adds_provenance_without_losing_legacy_records(tmp_path):
    import sqlite3

    path = tmp_path / "legacy.sqlite3"
    connection = sqlite3.connect(path)
    connection.executescript("""
        CREATE TABLE patients(
          id TEXT PRIMARY KEY, record_number TEXT UNIQUE NOT NULL, full_name TEXT NOT NULL,
          birth_date TEXT DEFAULT '', sex TEXT DEFAULT '', phone TEXT DEFAULT '', email TEXT DEFAULT '',
          notes TEXT DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE media(
          id TEXT PRIMARY KEY, patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
          slot_key TEXT NOT NULL, original_path TEXT NOT NULL, current_path TEXT NOT NULL,
          filename TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE analyses(
          id TEXT PRIMARY KEY, patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
          analysis_key TEXT NOT NULL, status TEXT NOT NULL, values_json TEXT NOT NULL,
          observations TEXT DEFAULT '', conclusion TEXT DEFAULT '', updated_at TEXT NOT NULL,
          UNIQUE(patient_id, analysis_key));
        CREATE TABLE reports(
          id TEXT PRIMARY KEY, patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
          student_name TEXT NOT NULL, teacher_email TEXT NOT NULL,
          selected_modules_json TEXT NOT NULL, analyses_json TEXT NOT NULL,
          pdf_path TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL);
        INSERT INTO patients VALUES(
          'legacy-id','PAD-LEGACY','Paciente anterior','','','','','','2026-01-01','2026-01-01');
        INSERT INTO analyses VALUES(
          'legacy-analysis','legacy-id','steiner','Completo','{"SNA":82}','nota','conclusion','2026-01-01');
    """)
    connection.commit()
    connection.close()

    db = Database(path)
    assert db.schema_version() == 2
    patient = db.get_patient("legacy-id")
    assert patient["full_name"] == "Paciente anterior"
    analysis = db.analysis_for_patient("legacy-id")["steiner"]
    assert analysis["values"]["SNA"] == 82
    assert analysis["algorithm_version"] == "unversioned"
    assert analysis["reference_set_id"] == "unversioned"


def test_media_hash_and_dimensions_are_recorded(tmp_path):
    from PIL import Image
    db = Database(tmp_path / "media.sqlite3")
    patient = db.create_patient("Paciente de medios")
    image_path = tmp_path / "study.png"
    Image.new("RGB", (32, 24), "white").save(image_path)

    media_id = db.add_media(
        patient["id"], "extra_frontal", image_path, image_path, image_path.name
    )
    media = next(item for item in db.media_for_patient(patient["id"]) if item["id"] == media_id)
    assert len(media["sha256"]) == 64
    assert media["byte_size"] > 0
    assert media["mime_type"] == "image/png"
    assert (media["width"], media["height"]) == (32, 24)


def test_calibration_is_scoped_to_patient_and_study(tmp_path):
    db = Database(tmp_path / "calibration.sqlite3")
    patient = db.create_patient("Paciente calibración")
    calibration = db.save_calibration(
        patient["id"], "mm", known_distance=10, pixel_distance=200,
        analysis_key="steiner", notes="Regla de referencia",
    )
    assert calibration["scale_per_pixel"] == 0.05
    assert db.calibrations_for_patient(patient["id"])[0]["id"] == calibration["id"]
