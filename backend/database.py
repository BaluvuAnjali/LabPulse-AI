from pathlib import Path
import os
import sqlite3
from contextlib import contextmanager


# ============================================================
# DATABASE LOCATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
# On Render, set LABPULSE_DB_PATH to a file on a Persistent Disk, e.g.
# /var/data/academic_lab.db. Locally, keep the existing project database.
DATABASE_PATH = Path(
    os.getenv("LABPULSE_DB_PATH", str(BASE_DIR / "backend" / "academic_lab.db"))
).expanduser()


# ============================================================
# DATABASE SCHEMA
# ============================================================

SCHEMA = """

-- ============================================================
-- 1. PHYSICAL LABORATORIES
-- ============================================================

CREATE TABLE IF NOT EXISTS laboratories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    lab_id TEXT UNIQUE NOT NULL,

    lab_name TEXT NOT NULL,

    capacity INTEGER NOT NULL DEFAULT 0,

    location TEXT NOT NULL DEFAULT 'College Campus',

    lab_type TEXT NOT NULL DEFAULT 'General',

    equipment TEXT NOT NULL DEFAULT '',

    department TEXT NOT NULL DEFAULT 'General',

        active INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS laboratory_verification_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    laboratory_id INTEGER NOT NULL,
    verified INTEGER NOT NULL DEFAULT 0,
    verified_by TEXT NOT NULL,
    verification_notes TEXT DEFAULT '',
    verified_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (laboratory_id)
        REFERENCES laboratories(id)
);


-- ============================================================
-- 2. DEPARTMENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    department_code TEXT UNIQUE NOT NULL,

    department_name TEXT UNIQUE NOT NULL
);


-- ============================================================
-- 3. SECTIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    section_code TEXT UNIQUE NOT NULL,

    department TEXT NOT NULL,

    academic_year TEXT NOT NULL,

    section_name TEXT NOT NULL
);


-- ============================================================
-- 4. MASTER TIMETABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS timetable (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    academic_year TEXT NOT NULL,

    department TEXT NOT NULL,

    section TEXT NOT NULL,

    day TEXT NOT NULL,

    period TEXT NOT NULL,

    time_slot TEXT NOT NULL,

    subject TEXT NOT NULL,

    faculty TEXT DEFAULT '',

    students INTEGER NOT NULL DEFAULT 0,

    resource_type TEXT NOT NULL DEFAULT 'THEORY',

    duration_minutes INTEGER NOT NULL DEFAULT 0,

    source_file TEXT DEFAULT '',

    uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 5. FACULTY CONFIRMED ACTUAL USAGE
-- ============================================================

CREATE TABLE IF NOT EXISTS faculty_usage (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    lab_id TEXT NOT NULL,

    lab_name TEXT DEFAULT '',

    usage_date TEXT NOT NULL,

    day TEXT NOT NULL,

    time_slot TEXT NOT NULL,

    department TEXT NOT NULL,

    academic_year TEXT NOT NULL,

    section TEXT NOT NULL,

    status TEXT NOT NULL DEFAULT 'FREE',

    faculty TEXT DEFAULT '',

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(
        lab_id,
        usage_date,
        time_slot,
        department,
        academic_year,
        section
    )
);


-- ============================================================
-- 6. LAB REQUESTS
-- ============================================================

CREATE TABLE IF NOT EXISTS lab_requests (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    request_date TEXT NOT NULL,

    time_slot TEXT NOT NULL,

    department TEXT NOT NULL,

    academic_year TEXT NOT NULL,

    section TEXT NOT NULL,

    students INTEGER NOT NULL,

    purpose TEXT NOT NULL,

    preferred_lab_type TEXT DEFAULT '',

    status TEXT NOT NULL DEFAULT 'Pending',

    recommended_lab TEXT DEFAULT '',

    recommendation_score REAL DEFAULT 0,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 7. WORKSHOPS / ACTIVITIES / RESERVATIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS activities (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    activity_name TEXT NOT NULL,

    activity_type TEXT NOT NULL,

    activity_date TEXT NOT NULL,

    start_time TEXT NOT NULL,

    end_time TEXT NOT NULL,

    organizer TEXT DEFAULT '',

    expected_students INTEGER NOT NULL DEFAULT 0,

    laboratory TEXT DEFAULT '',

    status TEXT NOT NULL DEFAULT 'Planned',

    department TEXT NOT NULL DEFAULT '',

    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 8. TIMETABLE UPLOAD HISTORY
-- ============================================================

CREATE TABLE IF NOT EXISTS timetable_uploads (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    academic_year TEXT NOT NULL,

    semester TEXT NOT NULL,

    file_name TEXT NOT NULL,

    rows_imported INTEGER NOT NULL DEFAULT 0,

    uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 9. HISTORICAL UTILIZATION
-- ============================================================

CREATE TABLE IF NOT EXISTS utilization_records (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    lab_id TEXT NOT NULL,

    usage_date TEXT NOT NULL,

    time_slot TEXT NOT NULL,

    department TEXT NOT NULL,

    academic_year TEXT NOT NULL,

    section TEXT NOT NULL,

    utilization_status TEXT NOT NULL,

    utilization_score REAL NOT NULL DEFAULT 0,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 10. ML TRAINING DATA
-- ============================================================

CREATE TABLE IF NOT EXISTS ml_utilization_data (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    lab_id TEXT NOT NULL,

    usage_date TEXT NOT NULL,

    day_of_week INTEGER NOT NULL,

    time_slot TEXT NOT NULL,

    department TEXT NOT NULL,

    academic_year TEXT NOT NULL,

    section TEXT NOT NULL,

    students INTEGER NOT NULL DEFAULT 0,

    capacity INTEGER NOT NULL DEFAULT 0,

    planned_usage INTEGER NOT NULL DEFAULT 0,

    actual_usage INTEGER NOT NULL DEFAULT 0,

    utilization_score REAL NOT NULL DEFAULT 0,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 11. ML PREDICTIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS ml_predictions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    lab_id TEXT NOT NULL,

    prediction_date TEXT NOT NULL,

    time_slot TEXT NOT NULL,

    academic_year TEXT NOT NULL,

    predicted_utilization REAL NOT NULL DEFAULT 0,

    predicted_demand REAL NOT NULL DEFAULT 0,

    model_name TEXT NOT NULL DEFAULT 'RandomForestRegressor',

    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 12. AUDIT LOGS
-- ============================================================


CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT DEFAULT '',
    actor TEXT NOT NULL DEFAULT 'System',
    details TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 13. VENUE MAPPINGS
-- ============================================================

CREATE TABLE IF NOT EXISTS venue_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    academic_year TEXT NOT NULL,
    department TEXT NOT NULL,
    section TEXT NOT NULL DEFAULT '',
    subject TEXT NOT NULL,
    day TEXT NOT NULL DEFAULT '',
    time_slot TEXT NOT NULL DEFAULT '',
    lab_venue TEXT NOT NULL DEFAULT '',
    venue_type TEXT NOT NULL DEFAULT 'UNVERIFIED',
    mapping_status TEXT NOT NULL DEFAULT 'VERIFIED',
    source_file TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (
        academic_year,
        department,
        section,
        subject,
        day,
        time_slot
    )
);

"""



# ============================================================
# DATABASE CONNECTION
# ============================================================

@contextmanager
def get_db():

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    con = sqlite3.connect(str(DATABASE_PATH))

    con.row_factory = sqlite3.Row

    try:

        yield con

        con.commit()

    except Exception:

        con.rollback()

        raise

    finally:

        con.close()


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():
    with get_db() as db:
        db.executescript(SCHEMA)
        db.execute("""
            CREATE TABLE IF NOT EXISTS venue_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                academic_year TEXT NOT NULL,
                department TEXT NOT NULL,
                section TEXT NOT NULL DEFAULT '',
                subject TEXT NOT NULL,
                day TEXT NOT NULL DEFAULT '',
                time_slot TEXT NOT NULL DEFAULT '',
                lab_venue TEXT NOT NULL DEFAULT '',
                venue_type TEXT NOT NULL DEFAULT 'UNVERIFIED',
                mapping_status TEXT NOT NULL DEFAULT 'VERIFIED',
                source_file TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (
                    academic_year,
                    department,
                    section,
                    subject,
                    day,
                    time_slot
                )
            )
        """)


# ============================================================
# SELECT / READ
# ============================================================

def query(sql, params=()):

    with get_db() as db:

        rows = db.execute(
            sql,
            params
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]


# ============================================================
# INSERT / UPDATE / DELETE
# ============================================================

def execute(sql, params=()):

    with get_db() as db:

        cursor = db.execute(
            sql,
            params
        )

        return cursor.lastrowid


# ============================================================
# AUDIT LOGGING
# ============================================================

def log_audit(action: str, entity_type: str, entity_id: str = "", actor: str = "System", details: str = ""):
    try:
        execute(
            """
            INSERT INTO audit_logs (action, entity_type, entity_id, actor, details)
            VALUES (?, ?, ?, ?, ?)
            """,
            (action, entity_type, str(entity_id), actor, details),
        )
    except Exception:
        pass


def get_audit_logs(limit: int = 50):
    try:
        return query(
            """
            SELECT * FROM audit_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
    except Exception:
        return []