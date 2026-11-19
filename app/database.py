"""SQLite local: pacientes, versiones de estudios y análisis."""
import json, sqlite3, uuid
from pathlib import Path
from datetime import datetime, timezone

def now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")

class Database:
    def __init__(self, path):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS patients(
              id TEXT PRIMARY KEY, record_number TEXT UNIQUE NOT NULL, full_name TEXT NOT NULL,
              birth_date TEXT DEFAULT '', sex TEXT DEFAULT '', phone TEXT DEFAULT '', email TEXT DEFAULT '',
              notes TEXT DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS media(
              id TEXT PRIMARY KEY, patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
              slot_key TEXT NOT NULL, original_path TEXT NOT NULL, current_path TEXT NOT NULL,
              filename TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS analyses(
              id TEXT PRIMARY KEY, patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
              analysis_key TEXT NOT NULL, status TEXT NOT NULL, values_json TEXT NOT NULL,
              observations TEXT DEFAULT '', conclusion TEXT DEFAULT '', updated_at TEXT NOT NULL,
              UNIQUE(patient_id, analysis_key));
            CREATE INDEX IF NOT EXISTS ix_media_patient ON media(patient_id, slot_key, created_at);
            CREATE INDEX IF NOT EXISTS ix_analysis_patient ON analyses(patient_id);
            """)
    def connect(self):
        c = sqlite3.connect(self.path, timeout=20); c.row_factory = sqlite3.Row
        c.execute("PRAGMA foreign_keys=ON"); c.execute("PRAGMA journal_mode=WAL")
        return c
    def create_patient(self, full_name, birth_date="", sex="", phone="", email="", notes=""):
        if not full_name.strip(): raise ValueError("El nombre es obligatorio.")
        pid = str(uuid.uuid4()); stamp = now()
        number = f"PAD-{datetime.now():%y%m%d}-{pid[:6].upper()}"
        with self.connect() as db:
            db.execute("INSERT INTO patients VALUES(?,?,?,?,?,?,?,?,?,?)",
              (pid,number,full_name.strip(),birth_date,sex,phone,email,notes,stamp,stamp))
        return self.get_patient(pid)
    def get_patient(self, pid):
        with self.connect() as db: row=db.execute("SELECT * FROM patients WHERE id=?",(pid,)).fetchone()
        return dict(row) if row else None
    def list_patients(self, query=""):
        q=f"%{query.strip()}%"
        with self.connect() as db:
            rows=db.execute("SELECT * FROM patients WHERE full_name LIKE ? OR record_number LIKE ? ORDER BY updated_at DESC",(q,q)).fetchall()
        return [dict(x) for x in rows]
    def add_media(self, pid, slot, original, current, filename):
        mid=str(uuid.uuid4())
        with self.connect() as db:
            db.execute("INSERT INTO media VALUES(?,?,?,?,?,?,?)",(mid,pid,slot,str(original),str(current),filename,now()))
        return mid
    def media_for_patient(self,pid):
        with self.connect() as db: rows=db.execute("SELECT * FROM media WHERE patient_id=? ORDER BY created_at",(pid,)).fetchall()
        return [dict(x) for x in rows]
    def media_for_slot(self,pid,slot):
        with self.connect() as db: rows=db.execute("SELECT * FROM media WHERE patient_id=? AND slot_key=? ORDER BY created_at DESC",(pid,slot)).fetchall()
        return [dict(x) for x in rows]
    def get_media_for_slot(self,pid,slot):
        rows=self.media_for_slot(pid,slot); return rows[0] if rows else None
    def update_media_path(self,mid,path):
        with self.connect() as db: db.execute("UPDATE media SET current_path=? WHERE id=?",(str(path),mid))
    def delete_media(self,mid):
        with self.connect() as db: db.execute("DELETE FROM media WHERE id=?",(mid,))
    def save_analysis(self,pid,key,status,values,observations="",conclusion=""):
        stamp=now()
        with self.connect() as db:
            db.execute("""INSERT INTO analyses VALUES(?,?,?,?,?,?,?,?)
              ON CONFLICT(patient_id,analysis_key) DO UPDATE SET status=excluded.status,
              values_json=excluded.values_json,observations=excluded.observations,
              conclusion=excluded.conclusion,updated_at=excluded.updated_at""",
              (str(uuid.uuid4()),pid,key,status,json.dumps(values,ensure_ascii=False),observations,conclusion,stamp))
    def analysis_for_patient(self,pid):
        with self.connect() as db: rows=db.execute("SELECT * FROM analyses WHERE patient_id=?",(pid,)).fetchall()
        out={}
        for x in rows:
            d=dict(x); d["values"]=json.loads(d.pop("values_json") or "{}"); out[d["analysis_key"]]=d
        return out
    def counts_for_patient(self,pid):
        with self.connect() as db:
            m=db.execute("SELECT count(*) FROM media WHERE patient_id=?",(pid,)).fetchone()[0]
            a=db.execute("SELECT count(*) FROM analyses WHERE patient_id=?",(pid,)).fetchone()[0]
            c=db.execute("SELECT count(*) FROM analyses WHERE patient_id=? AND status='Completo'",(pid,)).fetchone()[0]
        return {"media":m,"analyses":a,"complete":c}
