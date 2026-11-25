"""SQLite local: pacientes, medios, análisis, calibraciones e informes.

Las migraciones son aditivas para conservar expedientes creados por versiones previas.
"""
import hashlib
import json
import mimetypes
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime, timezone

SCHEMA_VERSION = 2


def now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


class Database:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
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
            CREATE INDEX IF NOT EXISTS ix_media_patient ON media(patient_id, slot_key, created_at);
            CREATE TABLE IF NOT EXISTS analyses(
              id TEXT PRIMARY KEY, patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
              analysis_key TEXT NOT NULL, status TEXT NOT NULL, values_json TEXT NOT NULL,
              observations TEXT DEFAULT '', conclusion TEXT DEFAULT '', updated_at TEXT NOT NULL,
              UNIQUE(patient_id, analysis_key));
            CREATE INDEX IF NOT EXISTS ix_analysis_patient ON analyses(patient_id);
            CREATE TABLE IF NOT EXISTS reports(
              id TEXT PRIMARY KEY,
              patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
              student_name TEXT NOT NULL, teacher_email TEXT NOT NULL,
              selected_modules_json TEXT NOT NULL, analyses_json TEXT NOT NULL,
              pdf_path TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS ix_reports_patient ON reports(patient_id, created_at);
            CREATE TABLE IF NOT EXISTS app_metadata(
              key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS calibrations(
              id TEXT PRIMARY KEY,
              patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
              media_id TEXT REFERENCES media(id) ON DELETE SET NULL,
              analysis_key TEXT NOT NULL DEFAULT '',
              unit TEXT NOT NULL,
              known_distance REAL NOT NULL CHECK(known_distance > 0),
              pixel_distance REAL NOT NULL CHECK(pixel_distance > 0),
              scale_per_pixel REAL NOT NULL CHECK(scale_per_pixel > 0),
              created_at TEXT NOT NULL,
              notes TEXT DEFAULT '');
            CREATE INDEX IF NOT EXISTS ix_calibration_patient ON calibrations(patient_id, created_at);
            """)
            self._migrate(db)
            db.execute(
                """INSERT INTO app_metadata(key,value,updated_at) VALUES('schema_version',?,?)
                   ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
                (str(SCHEMA_VERSION), now()),
            )

    def connect(self):
        connection = sqlite3.connect(self.path, timeout=20)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA busy_timeout=20000")
        return connection

    @staticmethod
    def _columns(db, table):
        return {row["name"] for row in db.execute(f"PRAGMA table_info({table})")}

    def _migrate(self, db):
        """Añade metadatos sin eliminar ni reescribir datos clínicos existentes."""
        additions = {
            "media": {
                "sha256": "TEXT NOT NULL DEFAULT ''",
                "byte_size": "INTEGER",
                "mime_type": "TEXT NOT NULL DEFAULT ''",
                "width": "INTEGER",
                "height": "INTEGER",
                "orientation": "TEXT NOT NULL DEFAULT 'unknown'",
            },
            "analyses": {
                "algorithm_version": "TEXT NOT NULL DEFAULT 'unversioned'",
                "reference_set_id": "TEXT NOT NULL DEFAULT 'unversioned'",
            },
        }
        for table, columns in additions.items():
            existing = self._columns(db, table)
            for name, declaration in columns.items():
                if name not in existing:
                    db.execute(f"ALTER TABLE {table} ADD COLUMN {name} {declaration}")

    def schema_version(self):
        with self.connect() as db:
            row = db.execute("SELECT value FROM app_metadata WHERE key='schema_version'").fetchone()
        return int(row["value"]) if row else 1

    def create_patient(self, full_name, birth_date="", sex="", phone="", email="", notes=""):
        if not full_name.strip():
            raise ValueError("El nombre es obligatorio.")
        pid = str(uuid.uuid4())
        stamp = now()
        number = f"PAD-{datetime.now():%y%m%d}-{pid[:6].upper()}"
        with self.connect() as db:
            db.execute(
                "INSERT INTO patients VALUES(?,?,?,?,?,?,?,?,?,?)",
                (pid, number, full_name.strip(), birth_date, sex, phone, email, notes, stamp, stamp),
            )
        return self.get_patient(pid)

    def get_patient(self, pid):
        with self.connect() as db:
            row = db.execute("SELECT * FROM patients WHERE id=?", (pid,)).fetchone()
        return dict(row) if row else None

    def list_patients(self, query=""):
        q = f"%{query.strip()}%"
        with self.connect() as db:
            rows = db.execute(
                "SELECT * FROM patients WHERE full_name LIKE ? OR record_number LIKE ? ORDER BY updated_at DESC",
                (q, q),
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _media_metadata(path):
        metadata = {"sha256": "", "byte_size": None, "mime_type": "", "width": None,
                    "height": None, "orientation": "unknown"}
        file_path = Path(path)
        if not file_path.is_file():
            return metadata
        digest = hashlib.sha256()
        with file_path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        metadata["sha256"] = digest.hexdigest()
        metadata["byte_size"] = file_path.stat().st_size
        metadata["mime_type"] = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        try:
            from PIL import Image
            with Image.open(file_path) as image:
                metadata["width"], metadata["height"] = image.size
                exif_orientation = image.getexif().get(274)
                metadata["orientation"] = str(exif_orientation) if exif_orientation else "normal"
        except Exception:
            # DICOM u otros formatos no compatibles con Pillow conservan hash y tamaño.
            pass
        return metadata

    def add_media(self, pid, slot, original, current, filename):
        mid = str(uuid.uuid4())
        metadata = self._media_metadata(current)
        with self.connect() as db:
            db.execute(
                """INSERT INTO media(
                   id,patient_id,slot_key,original_path,current_path,filename,created_at,
                   sha256,byte_size,mime_type,width,height,orientation)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (mid, pid, slot, str(original), str(current), filename, now(),
                 metadata["sha256"], metadata["byte_size"], metadata["mime_type"],
                 metadata["width"], metadata["height"], metadata["orientation"]),
            )
        return mid

    def media_for_patient(self, pid):
        with self.connect() as db:
            rows = db.execute("SELECT * FROM media WHERE patient_id=? ORDER BY created_at", (pid,)).fetchall()
        return [dict(row) for row in rows]

    def media_for_slot(self, pid, slot):
        with self.connect() as db:
            rows = db.execute(
                "SELECT * FROM media WHERE patient_id=? AND slot_key=? ORDER BY created_at DESC",
                (pid, slot),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_media_for_slot(self, pid, slot):
        rows = self.media_for_slot(pid, slot)
        return rows[0] if rows else None

    def update_media_path(self, mid, path):
        metadata = self._media_metadata(path)
        with self.connect() as db:
            db.execute(
                """UPDATE media SET current_path=?,sha256=?,byte_size=?,mime_type=?,
                   width=?,height=?,orientation=? WHERE id=?""",
                (str(path), metadata["sha256"], metadata["byte_size"], metadata["mime_type"],
                 metadata["width"], metadata["height"], metadata["orientation"], mid),
            )

    def delete_media(self, mid):
        with self.connect() as db:
            db.execute("DELETE FROM media WHERE id=?", (mid,))

    def save_analysis(self, pid, key, status, values, observations="", conclusion="",
                      algorithm_version="unversioned", reference_set_id="unversioned"):
        stamp = now()
        with self.connect() as db:
            db.execute(
                """INSERT INTO analyses(
                   id,patient_id,analysis_key,status,values_json,observations,conclusion,updated_at,
                   algorithm_version,reference_set_id)
                   VALUES(?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(patient_id,analysis_key) DO UPDATE SET status=excluded.status,
                   values_json=excluded.values_json,observations=excluded.observations,
                   conclusion=excluded.conclusion,updated_at=excluded.updated_at,
                   algorithm_version=excluded.algorithm_version,reference_set_id=excluded.reference_set_id""",
                (str(uuid.uuid4()), pid, key, status, json.dumps(values, ensure_ascii=False),
                 observations, conclusion, stamp, algorithm_version, reference_set_id),
            )

    def analysis_for_patient(self, pid):
        with self.connect() as db:
            rows = db.execute("SELECT * FROM analyses WHERE patient_id=?", (pid,)).fetchall()
        result = {}
        for row in rows:
            item = dict(row)
            item["values"] = json.loads(item.pop("values_json") or "{}")
            result[item["analysis_key"]] = item
        return result

    def save_calibration(self, pid, unit, known_distance, pixel_distance, media_id=None,
                         analysis_key="", notes=""):
        if known_distance <= 0 or pixel_distance <= 0:
            raise ValueError("Las distancias de calibración deben ser mayores que cero.")
        calibration_id = str(uuid.uuid4())
        scale = float(known_distance) / float(pixel_distance)
        with self.connect() as db:
            db.execute(
                """INSERT INTO calibrations(
                   id,patient_id,media_id,analysis_key,unit,known_distance,pixel_distance,
                   scale_per_pixel,created_at,notes) VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (calibration_id, pid, media_id, analysis_key, unit, known_distance,
                 pixel_distance, scale, now(), notes),
            )
        return self.get_calibration(calibration_id)

    def get_calibration(self, calibration_id):
        with self.connect() as db:
            row = db.execute("SELECT * FROM calibrations WHERE id=?", (calibration_id,)).fetchone()
        return dict(row) if row else None

    def calibrations_for_patient(self, pid):
        with self.connect() as db:
            rows = db.execute(
                "SELECT * FROM calibrations WHERE patient_id=? ORDER BY created_at DESC", (pid,)
            ).fetchall()
        return [dict(row) for row in rows]

    def save_report(self, pid, student_name, teacher_email, selected_modules,
                    analyses_snapshot, pdf_path, status="PDF generado · pendiente de envío"):
        if not student_name.strip():
            raise ValueError("El nombre del estudiante es obligatorio.")
        if not teacher_email.strip():
            raise ValueError("El correo del docente es obligatorio.")
        report_id = str(uuid.uuid4())
        with self.connect() as db:
            db.execute(
                "INSERT INTO reports VALUES(?,?,?,?,?,?,?,?,?)",
                (report_id, pid, student_name.strip(), teacher_email.strip(),
                 json.dumps(list(selected_modules), ensure_ascii=False),
                 json.dumps(analyses_snapshot, ensure_ascii=False, default=str),
                 str(pdf_path), status, now()),
            )
        return self.get_report(report_id)

    def get_report(self, report_id):
        with self.connect() as db:
            row = db.execute("SELECT * FROM reports WHERE id=?", (report_id,)).fetchone()
        if not row:
            return None
        result = dict(row)
        result["selected_modules"] = json.loads(result.pop("selected_modules_json") or "[]")
        result["analyses"] = json.loads(result.pop("analyses_json") or "{}")
        return result

    def reports_for_patient(self, pid):
        with self.connect() as db:
            rows = db.execute(
                "SELECT * FROM reports WHERE patient_id=? ORDER BY created_at DESC", (pid,)
            ).fetchall()
        results = []
        for row in rows:
            item = dict(row)
            item["selected_modules"] = json.loads(item.pop("selected_modules_json") or "[]")
            item["analyses"] = json.loads(item.pop("analyses_json") or "{}")
            results.append(item)
        return results

    def counts_for_patient(self, pid):
        with self.connect() as db:
            media_count = db.execute("SELECT count(*) FROM media WHERE patient_id=?", (pid,)).fetchone()[0]
            analysis_count = db.execute("SELECT count(*) FROM analyses WHERE patient_id=?", (pid,)).fetchone()[0]
            complete_count = db.execute(
                "SELECT count(*) FROM analyses WHERE patient_id=? AND status='Completo'", (pid,)
            ).fetchone()[0]
        return {"media": media_count, "analyses": analysis_count, "complete": complete_count}
