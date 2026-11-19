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
