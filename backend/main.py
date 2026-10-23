from datetime import date, datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional
import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .database import initialize_database, get_db, query, execute, log_audit, get_audit_logs
from .excel_processor import process_timetable

import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=True)

SECRET_KEY = os.getenv("LABPULSE_SECRET_KEY")

if not SECRET_KEY:
    if os.getenv("RENDER"):
        raise RuntimeError(
            "LABPULSE_SECRET_KEY must be configured in production."
        )

    SECRET_KEY = "labpulse-ai-v7-academic-demo-secret-key-change-in-production"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

APP_NAME = "LabPulse AI"

APP_FULL_NAME = (
    "LabPulse AI â€” Academic Laboratory Resource Intelligence"
)

APP_VERSION = "6.0.0"

# These are only fallback slots.
# Real uploaded timetable slots are always preferred.
DEFAULT_SLOTS = [
    "09:30 AM - 10:30 AM",
    "10:30 AM - 11:20 AM",
    "11:20 AM - 12:10 PM",
    "12:10 PM - 01:00 PM",
    "01:00 PM - 02:00 PM",
    "02:00 PM - 02:50 PM",
    "02:50 PM - 03:40 PM",
    "03:40 PM - 04:30 PM",
]

YEARS = [
    "IST",
    "2ND",
    "3RD",
    "4TH",
]


# ============================================================
# REAL COLLEGE DEPARTMENTS
# ============================================================

REAL_DEPARTMENTS = [
    "AIM",
    "CAI",
    "CE",
    "CSD",
    "CSE",
    "CST",
    "ECE",
    "ECT",
    "EEE",
    "IT",
    "ME",
]


# ============================================================
# HOD INFORMATION
#
# Keep this section editable.
# It is NOT used as the timetable source of truth.
# ============================================================

DEPARTMENT_HODS = {

    "AIM": {
        "name": "Dr. G. Loshma",
        "email": os.getenv(
            "HOD_AIM_EMAIL",
            "",
        ),
    },

    "CAI": {
        "name": "Dr. G. Loshma",
        "email": os.getenv(
            "HOD_CAI_EMAIL",
            "",
        ),
    },

    "CE": {
        "name": "Mr. D. Naveen Kumar",
        "email": os.getenv(
            "HOD_CE_EMAIL",
            "",
        ),
    },

    "CSD": {
        "name": "Dr. D. Jaya Kumari",
        "email": os.getenv(
            "HOD_CSD_EMAIL",
            "",
        ),
    },

    "CSE": {
        "name": "Dr. D. Jaya Kumari",
        "email": os.getenv(
            "HOD_CSE_EMAIL",
            "",
        ),
    },

    "CST": {
        "name": "Dr. D. Jaya Kumari",
        "email": os.getenv(
            "HOD_CST_EMAIL",
            "",
        ),
    },

    "ECE": {
        "name": "Dr. E. Kusuma Kumari",
        "email": os.getenv(
            "HOD_ECE_EMAIL",
            "",
        ),
    },

    "ECT": {
        "name": "Dr. E. Kusuma Kumari",
        "email": os.getenv(
            "HOD_ECT_EMAIL",
            "",
        ),
    },

    "EEE": {
        "name": "D. Sudha Rani",
        "email": os.getenv(
            "HOD_EEE_EMAIL",
            "",
        ),
    },

    "IT": {
        "name": "IT HOD",
        "email": os.getenv(
            "HOD_IT_EMAIL",
            "",
        ),
    },

    "ME": {
        "name": "Dr. M. V. Ramesh",
        "email": os.getenv(
            "HOD_ME_EMAIL",
            "",
        ),
    },
}


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=APP_FULL_NAME,
    version=APP_VERSION,
)

CORS_ORIGINS = [
    "https://lab-pulse-ai-tau.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

initialize_database()


# ============================================================
# BASIC NORMALIZATION HELPERS
# ============================================================

def clean(value) -> str:

    if value is None:
        return ""

    return " ".join(
        str(value)
        .strip()
        .split()
    )


def normalize_department(value: str) -> str:

    value = clean(value).upper()

    aliases = {
        "AIML": "AIM",
        "AI & ML": "AIM",
        "ARTIFICIAL INTELLIGENCE": "AIM",

        "CAI": "CAI",
        "CSE (AI)": "CAI",

        "CIVIL": "CE",

        "COMPUTER SCIENCE": "CSE",
        "COMPUTER SCIENCE & ENGINEERING": "CSE",

        "ELECTRONICS": "ECE",

        "ELECTRICAL": "EEE",

        "MECHANICAL": "ME",
        "MECH": "ME",
    }

    return aliases.get(
        value,
        value,
    )


def normalize_year(value: str) -> str:

    value = clean(value).upper()

    aliases = {

        "I YEAR": "IST",
        "1ST YEAR": "IST",
        "1ST": "IST",
        "1": "IST",
        "FIRST YEAR": "IST",

        "II YEAR": "2ND",
        "2ND YEAR": "2ND",
        "2ND": "2ND",
        "2": "2ND",
        "SECOND YEAR": "2ND",

        "III YEAR": "3RD",
        "3RD YEAR": "3RD",
        "3RD": "3RD",
        "3": "3RD",
        "THIRD YEAR": "3RD",

        "IV YEAR": "4TH",
        "4TH YEAR": "4TH",
        "4TH": "4TH",
        "4": "4TH",
        "FOURTH YEAR": "4TH",
    }

    return aliases.get(
        value,
        value,
    )


def normalize_day(value: str) -> str:

    value = clean(value).upper()

    aliases = {
        "MON": "MONDAY",
        "TUE": "TUESDAY",
        "TUES": "TUESDAY",
        "WED": "WEDNESDAY",
        "THU": "THURSDAY",
        "THURS": "THURSDAY",
        "FRI": "FRIDAY",
        "SAT": "SATURDAY",
        "SUN": "SUNDAY",
    }

    return aliases.get(
        value,
        value,
    )


def normalize_subject(value: str) -> str:

    return clean(value).upper()


def normalize_section(value: str) -> str:

    return clean(value).upper()


# ============================================================
# LAB SUBJECT DETECTION
# ============================================================

def is_lab_subject(subject: str) -> bool:

    normalized = (
        clean(subject)
        .upper()
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
        .replace(".", "")
        .replace("&", "")
    )

    if not normalized:
        return False

    lab_keywords = [
        "LAB",
        "LB",
        "PRACTICAL",
        "WORKSHOP",
        "STUDIO",
    ]

    return any(
        keyword in normalized
        for keyword in lab_keywords
    )


# ============================================================
# TIME SLOT HELPERS
# ============================================================

def parse_clock(value: str):

    value = (
        clean(value)
        .upper()
        .replace(".", ":")
    )

    formats = [
        "%H:%M",
        "%I:%M %p",
        "%I %p",
    ]

    for fmt in formats:

        try:

            parsed = datetime.strptime(
                value,
                fmt,
            )

            return (
                parsed.hour * 60
                + parsed.minute
            )

        except ValueError:
            pass

    return None


def slot_bounds(slot: str):

    parts = [
        x.strip()
        for x in clean(slot).split("-")
    ]

    if len(parts) != 2:
        return None, None

    return (
        parse_clock(parts[0]),
        parse_clock(parts[1]),
    )


def slot_duration_minutes(slot: str):

    start, end = slot_bounds(slot)

    if start is None or end is None:
        return 0

    if end < start:
        end += 24 * 60

    return end - start


def slot_end_label(slot: str):

    _, end = slot_bounds(slot)

    if end is None:
        return slot

    hour, minute = divmod(
        end,
        60,
    )

    suffix = (
        "AM"
        if hour < 12
        else "PM"
    )

    hour12 = hour % 12 or 12

    return (
        f"{hour12:02d}:"
        f"{minute:02d} "
        f"{suffix}"
    )


def slot_overlaps(
    first_start: str,
    first_end: str,
    second_slot: str,
):

    first_start_minutes = parse_clock(
        first_start
    )

    first_end_minutes = parse_clock(
        first_end
    )

    second_start, second_end = slot_bounds(
        second_slot
    )

    if None in (
        first_start_minutes,
        first_end_minutes,
        second_start,
        second_end,
    ):
        return False

    return (
        first_start_minutes < second_end
        and first_end_minutes > second_start
    )


# ============================================================
# CURRENT TIMETABLE SLOTS
# ============================================================

def current_slots():

    rows = query(
        """
        SELECT DISTINCT time_slot
        FROM timetable
        WHERE TRIM(COALESCE(time_slot,'')) <> ''
        """
    )

    values = [
        clean(row["time_slot"])
        for row in rows
        if clean(row["time_slot"])
    ]

    if not values:
        return DEFAULT_SLOTS

    def sort_key(slot):

        start, _ = slot_bounds(slot)

        return (
            start
            if start is not None
            else 9999
        )

    return sorted(
        set(values),
        key=sort_key,
    )


# ============================================================
# TIMETABLE DATE/DAY HANDLING
#
# The real timetable is WEEKLY.
# It does not require a physical calendar date.
# ============================================================

def selected_day(selected_date: str):

    try:

        return datetime.fromisoformat(
            selected_date
        ).strftime("%A").upper()

    except ValueError:

        raise HTTPException(
            status_code=400,
            detail="Invalid date. Use YYYY-MM-DD.",
        )


def timetable_rows_for_date(
    selected_date: str,
    year: Optional[str] = None,
    department: Optional[str] = None,
    section: Optional[str] = None,
):

    day_name = selected_day(
        selected_date
    )

    sql = """
        SELECT *
        FROM timetable
        WHERE UPPER(TRIM(day))=?
    """

    parameters = [
        day_name,
    ]

    if year and year != "All Years":

        sql += """
            AND academic_year=?
        """

        parameters.append(
            normalize_year(year)
        )

    if department and department != "All Departments":

        sql += """
            AND department=?
        """

        parameters.append(
            normalize_department(
                department
            )
        )

    if section and section != "All Sections":

        sql += """
            AND section=?
        """

        parameters.append(
            normalize_section(section)
        )

    sql += """
        ORDER BY
            time_slot,
            department,
            section,
            subject
    """

    return query(
        sql,
        parameters,
    )


# ============================================================
# LOGIN
# ============================================================

class LoginIn(BaseModel):

    login_id: str
    password: str

def create_access_token(role: str, department: str, display_name: str):
    now = datetime.now(timezone.utc)

    payload = {
        "role": role,
        "department": department,
        "display_name": display_name,
        "iat": now,
        "exp": now + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        if not payload.get("role"):
            raise HTTPException(
                status_code=401,
                detail="Invalid token: role is missing.",
            )

        if not payload.get("department"):
            raise HTTPException(
                status_code=401,
                detail="Invalid token: department is missing.",
            )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Session expired. Please log in again.",
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or tampered access token.",
        )

@app.post("/api/login")
def login(payload: LoginIn):

    login_id = clean(
        payload.login_id
    ).lower()

    password = clean(
        payload.password
    ).lower()

    # --------------------------------------------------------
    # ADMIN
    # --------------------------------------------------------

    if (
        login_id == "admin"
        and password == "admin"
    ):

        return {
            "authenticated": True,
            "role": "Admin",
            "department": "All Departments",
            "department_code": "ALL",
            "display_name": "System Administrator",

            "access_token": create_access_token(
    "Admin",
    "All Departments",
    "System Administrator",
),
"token_type": "bearer",
        }

    # --------------------------------------------------------
    # STUDENT VIEWER / CR (PART 4.3)
    # --------------------------------------------------------

    if (
        login_id in ["student", "cr", "student_viewer"]
        and password in ["student", "viewer"]
    ):
        return {
            "authenticated": True,
            "role": "Student Viewer",
            "department": "AIM",
            "department_code": "AIM",
            "display_name": "Student Representative",
            "access_token": create_access_token(
                "Student Viewer",
                "AIM",
                "Student Representative",
            ),
            "token_type": "bearer",
        }

    # --------------------------------------------------------
    # REAL DEPARTMENT LOGIN
    #
    # Demo authentication is intentionally retained,
    # but department names now match the real timetable.
    # --------------------------------------------------------

    department = normalize_department(
        login_id
    )

    if department not in REAL_DEPARTMENTS:

        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid department login ID. "
                "Use admin, student, or a department code such as AIM, "
                "CAI, CSE, ECE, EEE or IT."
            ),
        )

    hod_info = DEPARTMENT_HODS.get(
        department,
        {},
    )

    if password == "hod":

        return {
            "authenticated": True,
            "role": "HOD",
            "department": department,
            "department_code": department,
            "display_name": hod_info.get(
                "name",
                f"{department} HOD",
            ),
            "access_token": create_access_token(
    "HOD",
    department,
    hod_info.get("name", f"{department} HOD"),
),
"token_type": "bearer",
        }

    if password == "faculty":

        return {
            "authenticated": True,
            "role": "Faculty",
            "department": department,
            "department_code": department,
            "display_name": f"{department} Faculty",
            "access_token": create_access_token(
    "Faculty",
    department,
    f"{department} Faculty",
),
"token_type": "bearer",
        }

    if password in ["student", "viewer"]:

        return {
            "authenticated": True,
            "role": "Student Viewer",
            "department": department,
            "department_code": department,
            "display_name": f"{department} Student Viewer",
            "access_token": create_access_token(
    "Student Viewer",
    department,
    f"{department} Student Viewer",
),
"token_type": "bearer",
        }

    raise HTTPException(
        status_code=401,
        detail=(
            "Invalid password. "
            "Demo passwords are admin, hod, faculty, or student."
        ),
    )


# ============================================================
# REQUEST / ACTIVITY MODELS
# ============================================================

class FacultyUsageIn(BaseModel):

    lab_id: str

    lab_name: str = ""

    usage_date: str

    time_slot: str

    department: str

    academic_year: str

    section: str

    status: str = "BUSY"

    faculty: str = ""


class RequestIn(BaseModel):

    request_date: str

    time_slot: str

    department: str

    academic_year: str

    section: str

    students: int = Field(gt=0)

    purpose: str

    preferred_lab_type: str = ""


class LaboratoryIn(BaseModel):
    lab_id: str
    lab_name: str
    location: str = ""
    lab_type: str = "General"
    equipment: str = ""
    department: str = ""
    capacity: Optional[int] = Field(default=None, ge=0)

class ActivityIn(BaseModel):

    activity_name: str

    activity_type: str

    activity_date: str

    start_time: str

    end_time: str

    organizer: str = ""

    expected_students: int = 0

    laboratory: str = ""

    status: str = "Upcoming"

    department: str = ""


class EmailTestIn(BaseModel):

    recipient: str


# ============================================================
# LAB MATCHING
# ============================================================

def lab_matches(
    value,
    lab,
):

    if not value:
        return False

    normalized_value = (
        clean(value)
        .casefold()
    )

    possible_values = {
        clean(
            lab.get("lab_id", "")
        ).casefold(),

        clean(
            lab.get("lab_name", "")
        ).casefold(),
    }

    return normalized_value in possible_values


# ============================================================
# ACTIVITY STATUS
# ============================================================

def derived_activity_status(row):

    try:

        now = datetime.now()

        activity_date = datetime.strptime(
            row["activity_date"],
            "%Y-%m-%d",
        ).date()

        start = parse_clock(
            row["start_time"]
        )

        end = parse_clock(
            row["end_time"]
        )

        now_minutes = (
            now.hour * 60
            + now.minute
        )

        if (
            activity_date < now.date()
            or (
                activity_date == now.date()
                and end is not None
                and now_minutes >= end
            )
        ):
            return "Completed"

        if (
            activity_date == now.date()
            and start is not None
            and now_minutes >= start
            and (
                end is None
                or now_minutes < end
            )
        ):
            return "Scheduled"

        return "Upcoming"

    except Exception:

        return row.get(
            "status",
            "Upcoming",
        )


# ============================================================
# LABORATORY MASTER
#
# IMPORTANT:
# The real timetable does NOT contain physical laboratory IDs.
#
# Therefore this endpoint only returns physical labs if they
# have been explicitly configured in the laboratories table.
# We never invent physical labs from subject names.
# ============================================================

@app.post("/api/laboratories")
def register_laboratory(
    item: LaboratoryIn,
    request: Request,
):
    authorization = request.headers.get("Authorization", "")

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

    token = authorization[len("Bearer "):].strip()

    try:
        payload = verify_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token."
        )

    if payload.get("role") != "Admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required."
        )

    lab_id = item.lab_id.strip()
    lab_name = item.lab_name.strip()

    if not lab_id or not lab_name:
        raise HTTPException(
            status_code=400,
            detail="Laboratory ID and name are required."
        )

    existing = query(
        """
        SELECT id
        FROM laboratories
        WHERE LOWER(lab_id) = LOWER(?)
        """,
        (lab_id,)
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="This laboratory ID already exists."
        )

    new_id = execute(
        """
        INSERT INTO laboratories (
            lab_id,
            lab_name,
            location,
            lab_type,
            equipment,
            department,
            capacity,
            active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        """,
        (
            lab_id,
            lab_name,
            item.location.strip(),
            item.lab_type.strip() or "General",
            item.equipment.strip(),
            item.department.strip(),
            item.capacity if item.capacity is not None else 0
        )
    )

    return {
        "success": True,
        "id": new_id,
        "lab_id": lab_id,
        "lab_name": lab_name,
        "active": 0,
        "verification_status": "PENDING",
        "message": (
            "Laboratory registered as inactive. "
            "Verify the physical venue before activation."
        )
    }


class LaboratoryVerificationIn(BaseModel):
    verified: bool = True
    verified_by: str = ""
    verification_notes: str = ""
    notes: str = ""
    
    
@app.patch("/api/laboratories/{lab_id}/verification")
@app.patch("/api/admin/laboratories/{lab_id}/verify")
def verify_laboratory(
    lab_id: str,
    item: LaboratoryVerificationIn,
    request: Request,
):
    
    authorization = request.headers.get("Authorization", "")

    if not authorization.startswith("Bearer "):

        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please log in.",
        )

    token = authorization[len("Bearer "):].strip()
    payload = verify_access_token(token)

    verified_by = payload.get("display_name", "").strip() or item.verified_by.strip() or "Administrator"

    if payload.get("role") != "Admin":
        raise HTTPException(
            status_code=403,
            detail="Only an Admin can verify laboratories.",
        )

    laboratory = query(
        """
        SELECT id, lab_id, lab_name, active
        FROM laboratories
        WHERE id = ? OR lab_id = ?
        """,
        (lab_id, lab_id)
    )

    if not laboratory:
        raise HTTPException(
            status_code=404,
            detail="Laboratory not found."
        )

    real_id = laboratory[0]["id"]
    new_active = 1 if item.verified else 0

    execute(
        """
        UPDATE laboratories
        SET active = ?
        WHERE id = ?
        """,
        (new_active, real_id)
    )

    execute(
        """
        INSERT INTO laboratory_verification_audit (
            laboratory_id,
            verified,
            verified_by,
            verification_notes
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            real_id,
            new_active,
            verified_by,
            (item.verification_notes or item.notes or "").strip()
        )
    )

    log_audit(
        "LAB_VERIFIED",
        "LABORATORY",
        laboratory[0]["lab_id"],
        verified_by,
        f"Verified active={new_active}. Notes: {(item.verification_notes or item.notes or '').strip()}"
    )

    return {
        "success": True,
        "id": real_id,
        "lab_id": laboratory[0]["lab_id"],
        "lab_name": laboratory[0]["lab_name"],
        "active": new_active,
        "verification_status": (
            "VERIFIED" if item.verified else "PENDING"
        ),
        "verified_by": verified_by,
        "verification_notes": (item.verification_notes or item.notes or "").strip(),
        "message": (
            "Laboratory activated after verification."
            if item.verified
            else "Laboratory deactivated pending verification."
        )
    }


@app.get("/api/laboratories")
def laboratories():
    # Return only genuine physical lab venues found in the
    # venue-mapping table. Do not treat classroom or seminar
    # hall mappings as physical laboratories.
    return query(
        """
        SELECT
            lab_venue AS lab_id,
            lab_venue AS lab_name,
            60 AS capacity,
            'College Campus' AS location,
            venue_type AS lab_type,
            1 AS active
        FROM venue_mappings
        WHERE UPPER(TRIM(venue_type)) = 'LABORATORY'
          AND TRIM(lab_venue) != ''
        GROUP BY lab_venue, venue_type
        ORDER BY lab_venue
        """
    )

@app.get("/api/admin/laboratories")
def admin_laboratories(request: Request):
    authorization = request.headers.get("Authorization", "")

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

    token = authorization[len("Bearer "):].strip()

    try:
        payload = verify_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token."
        )

    if payload.get("role") != "Admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required."
        )

    return query(
        """
        SELECT
            l.*,
            (
                SELECT a.verified
                FROM laboratory_verification_audit a
                WHERE a.laboratory_id = l.id
                ORDER BY a.id DESC
                LIMIT 1
            ) AS last_verified,
            (
                SELECT a.verified_by
                FROM laboratory_verification_audit a
                WHERE a.laboratory_id = l.id
                ORDER BY a.id DESC
                LIMIT 1
            ) AS last_verified_by,
            (
                SELECT a.verification_notes
                FROM laboratory_verification_audit a
                WHERE a.laboratory_id = l.id
                ORDER BY a.id DESC
                LIMIT 1
            ) AS last_verification_notes,
            (
                SELECT a.verified_at
                FROM laboratory_verification_audit a
                WHERE a.laboratory_id = l.id
                ORDER BY a.id DESC
                LIMIT 1
            ) AS last_verified_at
        FROM laboratories l
        ORDER BY l.id
        """
    )


# ============================================================
# DEPARTMENTS
# ============================================================

@app.get("/api/departments")
def departments():

    rows = query(
        """
        SELECT DISTINCT department
        FROM timetable
        WHERE TRIM(COALESCE(department,'')) <> ''
        ORDER BY department
        """
    )

    departments_found = [
        normalize_department(
            row["department"]
        )
        for row in rows
    ]

    departments_found = list(
        dict.fromkeys(
            departments_found
        )
    )

    return [
        {
            "department_code": department,
            "department_name": department,
            "hod_name": DEPARTMENT_HODS.get(
                department,
                {},
            ).get(
                "name",
                f"{department} HOD",
            ),
            "hod_email": DEPARTMENT_HODS.get(
                department,
                {},
            ).get(
                "email",
                "",
            ),
        }
        for department in departments_found
    ]


# ============================================================
# YEARS
# ============================================================

@app.get("/api/years")
def years():

    rows = query(
        """
        SELECT DISTINCT academic_year
        FROM timetable
        WHERE TRIM(COALESCE(academic_year,'')) <> ''
        """
    )

    values = [
        normalize_year(
            row["academic_year"]
        )
        for row in rows
    ]

    order = {
        "IST": 1,
        "2ND": 2,
        "3RD": 3,
        "4TH": 4,
    }

    values = sorted(
        set(values),
        key=lambda x: order.get(
            x,
            999,
        ),
    )

    return {
        "years": values
    }


# ============================================================
# SECTIONS
# ============================================================

@app.get("/api/sections")
def sections(
    department: Optional[str] = None,
    academic_year: Optional[str] = None,
):

    sql = """
        SELECT DISTINCT section
        FROM timetable
        WHERE TRIM(COALESCE(section,'')) <> ''
    """

    parameters = []

    if (
        department
        and department != "All Departments"
    ):

        sql += """
            AND department=?
        """

        parameters.append(
            normalize_department(
                department
            )
        )

    if (
        academic_year
        and academic_year != "All Years"
    ):

        sql += """
            AND academic_year=?
        """

        parameters.append(
            normalize_year(
                academic_year
            )
        )

    sql += """
        ORDER BY section
    """

    rows = query(
        sql,
        parameters,
    )

    values = [
        normalize_section(
            row["section"]
        )
        for row in rows
    ]

    return {
        "sections": values
    }


# ============================================================
# SETTINGS
# ============================================================

@app.get("/api/settings")
def settings():

    smtp_configured = bool(
        os.getenv("SMTP_HOST")
        and os.getenv("SMTP_USER")
        and os.getenv("SMTP_PASSWORD")
    )

    return {
        "system_name": APP_FULL_NAME,
        "short_name": APP_NAME,
        "version": APP_VERSION,
        "database": "SQLite",
        "supported_uploads": [
            ".xlsx",
            ".xls",
            ".csv",
        ],
        "time_slots": current_slots(),
        "default_time_slots": DEFAULT_SLOTS,
        "years": YEARS,
        "departments": REAL_DEPARTMENTS,
        "smtp_configured": smtp_configured,
    }


# ============================================================
# TIMETABLE
# ============================================================

@app.get("/api/timetable")
def timetable(
    year: Optional[str] = None,
    department: Optional[str] = None,
    selected_date: Optional[str] = None,
    section: Optional[str] = None,
):

    if selected_date:

        rows = timetable_rows_for_date(
            selected_date=selected_date,
            year=year,
            department=department,
            section=section,
        )

    else:

        sql = """
            SELECT *
            FROM timetable
            WHERE 1=1
        """

        parameters = []

        if (
            year
            and year != "All Years"
        ):

            sql += """
                AND academic_year=?
            """

            parameters.append(
                normalize_year(year)
            )

        if (
            department
            and department != "All Departments"
        ):

            sql += """
                AND department=?
            """

            parameters.append(
                normalize_department(
                    department
                )
            )

        if (
            section
            and section != "All Sections"
        ):

            sql += """
                AND section=?
            """

            parameters.append(
                normalize_section(
                    section
                )
            )

        sql += """
            ORDER BY
                academic_year,
                department,
                section,
                day,
                time_slot,
                period
        """

        rows = query(
            sql,
            parameters,
        )

    return rows


# ============================================================
# TIMETABLE UPLOAD
# ============================================================

@app.post("/api/timetable/upload")
async def upload_timetable(
    file: UploadFile = File(...),
    academic_year: str = "",
    semester: str = "",
):

    suffix = Path(
        file.filename or ""
    ).suffix.lower()

    if suffix not in {
        ".xlsx",
        ".xls",
        ".csv",
    }:

        raise HTTPException(
            status_code=400,
            detail=(
                "Upload only "
                ".xlsx, .xls or .csv files."
            ),
        )

    content = await file.read()

    with NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as temporary:

        temporary.write(content)

        temporary_path = temporary.name

    try:

        # ----------------------------------------------------
        # PROCESS REAL COLLEGE FILE
        # ----------------------------------------------------

        rows = process_timetable(
            temporary_path
        )

        if not rows:

            raise ValueError(
                "No timetable rows were found "
                "in the uploaded file."
            )

        # ----------------------------------------------------
        # DETECT YEARS
        # ----------------------------------------------------

        detected_years = sorted(
            {
                normalize_year(
                    row.get(
                        "academic_year",
                        "",
                    )
                )
                for row in rows
                if row.get(
                    "academic_year"
                )
            }
        )

        # ----------------------------------------------------
        # DETECT DEPARTMENTS
        # ----------------------------------------------------

        detected_departments = sorted(
            {
                normalize_department(
                    row.get(
                        "department",
                        "",
                    )
                )
                for row in rows
                if row.get(
                    "department"
                )
            }
        )

        if not academic_year:

            if len(detected_years) == 1:

                academic_year = detected_years[0]

            else:

                academic_year = "Multiple Years"

        # ----------------------------------------------------
        # STORE TIMETABLE
        # ----------------------------------------------------

        with get_db() as db:

            # The uploaded timetable is the current
            # timetable master.
            db.execute(
                "DELETE FROM timetable"
            )

            imported = 0

            for row in rows:

                # ------------------------------------------------
                # NEW PROCESSOR RETURNS branch_section.
                #
                # DATABASE COLUMN IS section.
                # ------------------------------------------------

                section = row.get(
                    "section",
                    row.get(
                        "branch_section",
                        "",
                    ),
                )

                department = normalize_department(
                    row.get(
                        "department",
                        "",
                    )
                )

                academic_year_value = normalize_year(
                    row.get(
                        "academic_year",
                        "",
                    )
                )

                day = normalize_day(
                    row.get(
                        "day",
                        "",
                    )
                )

                subject = normalize_subject(
                    row.get(
                        "subject",
                        "",
                    )
                )

                faculty = clean(
                    row.get(
                        "faculty",
                        "",
                    )
                )

                students_value = row.get(
                    "students",
                    0,
                )

                try:

                    students = int(
                        float(
                            students_value or 0
                        )
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    students = 0

                duration = row.get(
                    "duration_minutes",
                    0,
                )

                try:

                    duration = int(
                        float(
                            duration or 0
                        )
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    duration = 0

                resource_type = row.get(
                    "resource_type",
                    (
                        "LAB"
                        if is_lab_subject(subject)
                        else "THEORY"
                    ),
                )

                # ------------------------------------------------
                # IMPORTANT:
                # Physical lab ID/name are NOT invented.
                # ------------------------------------------------

                db.execute(
                    """
                    INSERT INTO timetable(
                        academic_year,
                        department,
                        section,
                        day,
                        period,
                        time_slot,
                        subject,
                        faculty,
                        students,
                        resource_type,
                        duration_minutes,
                        source_file,
                        uploaded_at
                    )
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        academic_year_value,
                        department,
                        normalize_section(
                            section
                        ),
                        day,
                        clean(
                            row.get(
                                "period",
                                "",
                            )
                        ),
                        clean(
                            row.get(
                                "time_slot",
                                "",
                            )
                        ),
                        subject,
                        faculty,
                        students,
                        resource_type,
                        duration,
                        file.filename
                        or "timetable",
                        datetime.now().isoformat(
                            timespec="seconds"
                        ),
                    ),
                )

                imported += 1

            # ------------------------------------------------
            # UPLOAD HISTORY
            # ------------------------------------------------

            db.execute(
                """
                INSERT INTO timetable_uploads(
                    academic_year,
                    semester,
                    file_name,
                    rows_imported
                )
                VALUES (?,?,?,?)
                """,
                (
                    academic_year,
                    semester
                    or "Not specified",
                    file.filename
                    or "timetable",
                    imported,
                ),
            )

        return {
            "success": True,
            "rows_imported": imported,
            "file": file.filename,
            "academic_year": academic_year,
            "semester": semester
            or "Not specified",
            "years_detected": detected_years,
            "departments_detected": detected_departments,
            "message": (
                "Real college timetable "
                "processed successfully."
            ),
        }

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    finally:

        Path(
            temporary_path
        ).unlink(
            missing_ok=True
        )


# ============================================================
# UPLOAD HISTORY
# ============================================================

@app.get("/api/timetable/upload-history")
def upload_history():

    return query(
        """
        SELECT *
        FROM timetable_uploads
        ORDER BY id DESC
        LIMIT 10
        """
    )


# ============================================================
# FACULTY USAGE â€” GET
# ============================================================

@app.get("/api/faculty-usage")
def faculty_usage(
    selected_date: Optional[str] = None,
):

    if selected_date:

        return query(
            """
            SELECT *
            FROM faculty_usage
            WHERE usage_date=?
            ORDER BY time_slot, lab_id
            """,
            (
                selected_date,
            ),
        )

    return query(
        """
        SELECT *
        FROM faculty_usage
        ORDER BY
            usage_date DESC,
            time_slot,
            lab_id
        """
    )


# ============================================================
# FACULTY USAGE â€” SAVE
# ============================================================

@app.post("/api/faculty-usage")
def save_faculty_usage(
    item: FacultyUsageIn,
):

    status = clean(
        item.status
    ).upper()

    if status not in {
        "BUSY",
        "FREE",
    }:

        raise HTTPException(
            status_code=400,
            detail=(
                "Status must be BUSY or FREE."
            ),
        )

    department = normalize_department(
        item.department
    )

    academic_year = normalize_year(
        item.academic_year
    )

    section = normalize_section(
        item.section
    )

    try:

        day = datetime.fromisoformat(
            item.usage_date
        ).strftime("%A").upper()

    except ValueError:

        raise HTTPException(
            status_code=400,
            detail=(
                "usage_date must use "
                "YYYY-MM-DD format."
            ),
        )

    with get_db() as db:

        db.execute(
            """
            INSERT INTO faculty_usage(
                lab_id,
                lab_name,
                usage_date,
                day,
                time_slot,
                department,
                academic_year,
                section,
                status,
                faculty
            )
            VALUES (?,?,?,?,?,?,?,?,?,?)

            ON CONFLICT(
                lab_id,
                usage_date,
                time_slot,
                department,
                academic_year,
                section
            )

            DO UPDATE SET
                status=excluded.status,
                faculty=excluded.faculty,
                lab_name=excluded.lab_name,
                day=excluded.day
            """,
            (
                item.lab_id,
                item.lab_name,
                item.usage_date,
                day,
                item.time_slot,
                department,
                academic_year,
                section,
                status,
                item.faculty,
            ),
        )

    return {
        "success": True,
        "message": (
            "Faculty usage status saved. "
            "The status will be used by "
            "the dynamic availability engine."
        ),
    }


# ============================================================
# FACULTY USAGE â€” DELETE
# ============================================================

@app.delete("/api/faculty-usage/{usage_id}")
def delete_usage(
    usage_id: int,
):

    with get_db() as db:

        db.execute(
            """
            DELETE FROM faculty_usage
            WHERE id=?
            """,
            (
                usage_id,
            ),
        )

    return {
        "success": True
    }


# ============================================================
# PHYSICAL LAB AVAILABILITY
#
# IMPORTANT:
# This operates only on explicitly configured physical labs.
# The timetable itself does NOT create physical labs.
# ============================================================


def normalize_time_slot(value):
    """Normalize spacing around the hyphen in a time slot."""
    return "-".join(
        part.strip()
        for part in str(value or "").split("-")
    )


def get_venue_mappings_for_slot(selected_date, time_slot):
    """Find venue mappings matching a date and clock-time slot."""
    from datetime import date, datetime

    try:
        if isinstance(selected_date, datetime):
            selected_day = selected_date.strftime("%A").upper()
        elif isinstance(selected_date, date):
            selected_day = selected_date.strftime("%A").upper()
        else:
            selected_day = datetime.strptime(
                str(selected_date).strip(),
                "%Y-%m-%d",
            ).strftime("%A").upper()
    except (ValueError, TypeError):
        return []

    slot_text = normalize_time_slot(time_slot)

    # Find the period number for each academic year separately.
    period_rows = query(
        """
        SELECT DISTINCT academic_year, period
        FROM timetable
        WHERE UPPER(day) = ?
          AND REPLACE(TRIM(time_slot), ' ', '') = REPLACE(?, ' ', '')
          AND UPPER(resource_type) = 'LAB'
        """,
        (selected_day, slot_text),
    )

    mappings = []
    seen = set()

    for period_row in period_rows:
        academic_year = str(
            period_row["academic_year"]
        ).strip().upper()

        period_text = str(
            period_row["period"]
        ).strip()

        try:
            period_number = int(
                period_text.replace("Period-", "")
            )
        except ValueError:
            continue

        rows = query(
            """
            SELECT *
            FROM venue_mappings
            WHERE UPPER(day) = ?
              AND UPPER(academic_year) = ?
              AND start_period <= ?
              AND end_period >= ?
            ORDER BY department, section, subject
            """,
            (
                selected_day,
                academic_year,
                period_number,
                period_number,
            ),
        )

        for row in rows:
            mapping = dict(row)

            # Avoid duplicate results if multiple timetable
            # records refer to the same mapping.
            key = mapping.get("id")

            if key is None:
                key = (
                    mapping.get("academic_year"),
                    mapping.get("department"),
                    mapping.get("section"),
                    mapping.get("subject"),
                    mapping.get("day"),
                    mapping.get("start_period"),
                    mapping.get("end_period"),
                )

            if key not in seen:
                seen.add(key)
                mappings.append(mapping)

    return mappings

    
def get_timetable_assignments_to_review(item):
    """Return matching timetable assignments, not confirmed availability."""

    mappings = get_venue_mappings_for_slot(
        item.request_date,
        item.time_slot,
    )

    requested_year = normalize_year(item.academic_year)
    requested_department = normalize_department(item.department)
    requested_section = normalize_section(item.section)

    suggestions = []

    for mapping in mappings:
        # Exclude the requesting section's own scheduled lab session.
        same_year = (
            normalize_year(mapping.get("academic_year", ""))
            == requested_year
        )
        same_department = (
            normalize_department(mapping.get("department", ""))
            == requested_department
        )
        same_section = (
            normalize_section(mapping.get("section", ""))
            == requested_section
        )

        if same_year and same_department and same_section:
            continue

        venue = str(mapping.get("lab_venue") or "").strip()

        if not venue:
            continue

        suggestions.append({
            "venue": venue,
            "venue_type": mapping.get("venue_type", ""),
            "academic_year": mapping.get("academic_year", ""),
            "department": mapping.get("department", ""),
            "section": mapping.get("section", ""),
            "subject": mapping.get("subject", ""),
            "day": mapping.get("day", ""),
            "start_period": mapping.get("start_period"),
            "end_period": mapping.get("end_period"),
            "mapping_status": mapping.get(
                "mapping_status",
                "REVIEW_REQUIRED",
            ),
            "confirmed_available": False,
            "note": (
                "Timetable assignment only. "
                "Physical venue availability has not been verified."
            ),
        })

    return suggestions



@app.get("/api/venue-mappings")
def venue_mappings(
    selected_date: str,
    time_slot: str,
    year: Optional[str] = None,
    department: Optional[str] = None,
    section: Optional[str] = None,
):
    """Return date/slot venue assignments with optional academic filters."""

    mappings = get_venue_mappings_for_slot(
        selected_date,
        time_slot,
    )

    if year and year != "All Years":
        wanted_year = normalize_year(year).strip().upper()
        mappings = [
            row for row in mappings
            if normalize_year(row.get("academic_year", "")).strip().upper() == wanted_year
        ]

    if department and department != "All Departments":
        wanted_department = normalize_department(department).strip().upper()
        mappings = [
            row for row in mappings
            if normalize_department(row.get("department", "")).strip().upper() == wanted_department
        ]

    if section and section != "All Sections":
        wanted_section = normalize_section(section).strip().upper()
        mappings = [
            row for row in mappings
            if normalize_section(row.get("section", "")).strip().upper() == wanted_section
        ]

    return {
        "date": selected_date,
        "time_slot": time_slot,
        "total": len(mappings),
        "mappings": mappings,
        "note": (
            "Venue mappings are timetable assignments, not "
            "confirmation of real-time physical-lab availability. "
            "Mappings marked REVIEW_REQUIRED need verification."
        ),
    }

def available_state(
    selected_date,
    time_slot,
    year=None,
    department=None,
    section=None,
):
    labs = query(
    """
    SELECT
        lab_venue AS lab_id,
        lab_venue AS lab_name,
        60 AS capacity,
        'College Campus' AS location,
        venue_type AS lab_type,
        1 AS active
    FROM venue_mappings
    WHERE UPPER(TRIM(venue_type)) = 'LABORATORY'
      AND TRIM(lab_venue) != ''
    GROUP BY lab_venue, venue_type
    ORDER BY lab_venue
    """
)

    if not labs:

        return []

    # --------------------------------------------------------
    # TIMETABLE
    #
    # Real timetable is weekly and does not have lab_id.
    # Therefore timetable rows are interpreted as planned
    # academic usage, not as assignment to a physical lab.
    # --------------------------------------------------------

    scheduled = timetable_rows_for_date(
    selected_date,
    year=year,
    department=department,
    section=section,
)

    scheduled = [
        row
        for row in scheduled
        if clean(
            row.get("time_slot", "")
        ) == clean(time_slot)
        and (
            clean(
                row.get(
                    "resource_type",
                    "",
                )
            ).upper()
            == "LAB"
        )
    ]

    # --------------------------------------------------------
    # FACULTY USAGE
    # --------------------------------------------------------

    busy = query(
        """
        SELECT *
        FROM faculty_usage
        WHERE usage_date=?
          AND time_slot=?
        """,
        (
            selected_date,
            time_slot,
        ),
    )

    # --------------------------------------------------------
    # ACTIVE REQUESTS
    # --------------------------------------------------------

    requests = query(
        """
        SELECT *
        FROM lab_requests
        WHERE request_date=?
          AND time_slot=?
          AND status NOT IN(
              'Rejected',
              'Completed'
          )
        ORDER BY id DESC
        """,
        (
            selected_date,
            time_slot,
        ),
    )

    # --------------------------------------------------------
    # ACTIVITIES
    # --------------------------------------------------------

    activities = query(
        """
        SELECT *
        FROM activities
        WHERE activity_date=?
        """,
        (
            selected_date,
        ),
    )

    result = []

    # ========================================================
    # CHECK EVERY PHYSICAL LAB
    # ========================================================

    for lab in labs:

        state = "Available"

        reason = (
            "No conflicting booking is recorded for this lab and time slot."
        )

        # ----------------------------------------------------
        # PRIORITY 1 â€” FACULTY BUSY
        # ----------------------------------------------------

        faculty_busy = next(
            (
                row
                for row in busy
                if clean(
                    row.get("lab_id", "")
                )
                == clean(
                    lab["lab_id"]
                )
                and clean(
                    row.get("status", "")
                ).upper()
                == "BUSY"
            ),
            None,
        )

        if faculty_busy:

            state = "Busy (Faculty)"

            faculty_name = clean(
                faculty_busy.get(
                    "faculty",
                    "",
                )
            )

            reason = (
                "Faculty confirmed usage"
                + (
                    f" by {faculty_name}"
                    if faculty_name
                    else ""
                )
            )

        else:

            # ------------------------------------------------
            # PRIORITY 2 â€” REQUEST RESERVATION
            # ------------------------------------------------

            reservation = next(
                (
                    request
                    for request in requests
                    if (
                        clean(
                            request.get(
                                "recommended_lab",
                                "",
                            )
                        ).casefold()
                        in {
                            clean(
                                lab["lab_id"]
                            ).casefold(),

                            clean(
                                lab["lab_name"]
                            ).casefold(),
                        }
                    )
                ),
                None,
            )

            if reservation:

                state = "Reserved"

                reason = (
                    "Reserved for "
                    f"{reservation.get('department','')} â€¢ "
                    f"{reservation.get('academic_year','')} â€¢ "
                    f"Section "
                    f"{reservation.get('section','')} â€¢ "
                    f"{reservation.get('students',0)} students"
                )

            else:

                # ------------------------------------------------
                # PRIORITY 3 â€” ACTIVITY
                # ------------------------------------------------

                activity = next(
                    (
                        activity
                        for activity in activities
                        if lab_matches(
                            activity.get(
                                "laboratory",
                                "",
                            ),
                            lab,
                        )
                        and activity.get(
                            "status",
                            "",
                        ) not in {
                            "Completed",
                            "Cancelled",
                        }
                        and slot_overlaps(
                            activity.get(
                                "start_time",
                                "",
                            ),
                            activity.get(
                                "end_time",
                                "",
                            ),
                            time_slot,
                        )
                    ),
                    None,
                )

                if activity:

                    state = "Workshop / Activity"

                    reason = (
                        f"{activity.get('activity_name','Activity')} â€¢ "
                        f"{activity.get('start_time','')} - "
                        f"{activity.get('end_time','')}"
                    )

                else:

                    # ------------------------------------------------
                    # PRIORITY 4 â€” PLANNED LAB ACTIVITY
                    #
                    # Since no physical lab is supplied in the
                    # real timetable, we do NOT mark every physical
                    # laboratory as scheduled.
                    # ------------------------------------------------

                    if scheduled:
                        subjects = sorted({
                            clean(row.get("subject", ""))
                            for row in scheduled
                            if clean(row.get("subject", ""))
                        })

                        # A scheduled lab session without a physical venue
                        # cannot be assigned to every lab. Keep this lab
                        # available unless a lab-specific conflict is recorded.
                        state = "Available"
                        reason = ""
                        if not subjects:
                            state = "Availability Unverified"
                            reason = "Physical laboratory availability has not been verified"

        result.append(
            {
                **dict(lab),
                "status": state,
                "reason": reason,
                "planned_lab_sessions": len(
                    scheduled
                ),
            }
        )

    return result


# ============================================================
# LAB AVAILABILITY API
# ============================================================
@app.get("/api/lab-availability")
def lab_availability(
    selected_date: str = date.today().isoformat(),
    time_slot: str = "",
    year: Optional[str] = None,
    department: Optional[str] = None,
    section: Optional[str] = None,
):

    if not time_slot:

        slots = current_slots()

        time_slot = (
            slots[0]
            if slots
            else DEFAULT_SLOTS[0]
        )

    data = available_state(
    selected_date,
    time_slot,
    year=year,
    department=department,
    section=section,
)

    return {
        "date": selected_date,
        "time_slot": time_slot,
        "labs": data,
        "available_count": sum(
            row["status"] == "Available"
            for row in data
        ),
    }


# ============================================================
# RECOMMENDATION ENGINE
#
# This is NOT ML accuracy.
#
# It is transparent weighted ranking after hard filtering.
# ============================================================

def build_recommendations(item):

    labs = query("""
        SELECT *
        FROM laboratories
        WHERE active=1
        ORDER BY id
    """)

    # Augment with genuine physical venue mappings if active labs is small
    if len(labs) < 5:
        venue_rows = query("""
            SELECT DISTINCT lab_venue AS lab_id, lab_venue AS lab_name, department, venue_type AS lab_type, 60 AS capacity, 'College Campus' AS location, 1 AS active
            FROM venue_mappings
            WHERE lab_venue IS NOT NULL AND lab_venue != ''
            LIMIT 15
        """)
        existing_ids = {clean(l["lab_id"]) for l in labs}
        for vr in venue_rows:
            if clean(vr["lab_id"]) not in existing_ids:
                labs.append(vr)

    if not labs:
        return []

    busy = {
        clean(row["lab_id"])
        for row in query("""
            SELECT lab_id
            FROM faculty_usage
            WHERE usage_date=?
              AND time_slot=?
              AND status='BUSY'
        """, (item.request_date, item.time_slot))
        if clean(row["lab_id"])
    }

    reserved_rows = query("""
        SELECT recommended_lab
        FROM lab_requests
        WHERE request_date=?
          AND time_slot=?
          AND status NOT IN ('Rejected', 'Completed')
    """, (item.request_date, item.time_slot))

    reserved = {
        clean(row["recommended_lab"]).casefold()
        for row in reserved_rows
        if clean(row["recommended_lab"])
    }

    activities = query("""
        SELECT *
        FROM activities
        WHERE activity_date=?
    """, (item.request_date,))

    history = query("""
        SELECT lab_id, AVG(utilization_score) AS avg_score
        FROM utilization_records
        GROUP BY lab_id
    """)

    history_map = {
        clean(row["lab_id"]): float(row["avg_score"] or 0)
        for row in history
    }

    recommendations = []

    for lab in labs:
        lab_id = clean(lab["lab_id"])

        if lab_id in busy:
            continue

        if (
            lab_id.casefold() in reserved
            or clean(lab["lab_name"]).casefold() in reserved
        ):
            continue

        activity_conflict = any(
            (
                lab_matches(activity.get("laboratory", ""), lab)
                and activity.get("status", "") not in {
                    "Completed",
                    "Cancelled",
                }
                and slot_overlaps(
                    activity.get("start_time", ""),
                    activity.get("end_time", ""),
                    item.time_slot,
                )
            )
            for activity in activities
        )

        if activity_conflict:
            continue

        score = 50.0
        reasons = ["Passes checked availability constraints"]

        preferred_type = clean(
            getattr(item, "preferred_lab_type", "")
        ).casefold()
        actual_type = clean(lab.get("lab_type", "")).casefold()

        if preferred_type:
            if preferred_type in actual_type:
                score += 20
                reasons.append("Matches requested laboratory type")
            else:
                score -= 5
        else:
            score += 5

        utilization = history_map.get(lab_id, 0)
        score += min(20, max(0, utilization) * 0.2)

        if utilization >= 70:
            reasons.append("Strong historical utilization")

        recommendations.append({
            "lab_id": lab_id,
            "lab_name": lab["lab_name"],
            "location": lab.get("location", ""),
            "lab_type": lab.get("lab_type", ""),
            "score": round(max(0, min(100, score)), 1),
            "reason": reasons,
        })

    recommendations.sort(
        key=lambda recommendation: recommendation["score"],
        reverse=True,
    )
    return recommendations

# ============================================================
# LAB REQUESTS â€” GET
# ============================================================

@app.get("/api/requests")
def requests():

    return query(
        """
        SELECT *
        FROM lab_requests
        ORDER BY id DESC
        """
    )


# ============================================================
# LAB REQUESTS â€” CREATE
# ============================================================

@app.post("/api/requests")
def create_request(
    item: RequestIn,
):

    recommendations = build_recommendations(
        item
    )

    
    timetable_assignments_to_review = get_timetable_assignments_to_review(
        item
       )


    best_lab_id = (
        recommendations[0]["lab_id"]
        if recommendations
        else None
    )

    best_lab_name = (
        recommendations[0]["lab_name"]
        if recommendations
        else None
    )

    best_score = (
        recommendations[0]["score"]
        if recommendations
        else None
    )

    department = normalize_department(
        item.department
    )

    academic_year = normalize_year(
        item.academic_year
    )

    section = normalize_section(
        item.section
    )

    # --------------------------------------------------------
    # SAVE REQUEST
    # --------------------------------------------------------

    with get_db() as db:

        cursor = db.execute(
            """
            INSERT INTO lab_requests(
                request_date,
                time_slot,
                department,
                academic_year,
                section,
                students,
                purpose,
                preferred_lab_type,
                status,
                recommended_lab,
                recommendation_score
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                item.request_date,
                item.time_slot,
                department,
                academic_year,
                section,
                item.students,
                item.purpose,
                item.preferred_lab_type,
                "Pending",
                best_lab_id,
                best_score,
            ),
        )

        request_id = cursor.lastrowid

    # --------------------------------------------------------
    # HOD NOTIFICATION
    # --------------------------------------------------------

    notification = send_hod_email(
        department,
        (
            f"Lab Request "
            f"REQ{request_id:03d} "
            f"â€” {department}"
        ),
        (
            "New laboratory request\n\n"
            f"Request: REQ{request_id:03d}\n"
            f"Department: {department}\n"
            f"Academic Year: {academic_year}\n"
            f"Section: {section}\n"
            f"Date: {item.request_date}\n"
            f"Time: {item.time_slot}\n"
            f"Students: {item.students}\n"
            f"Purpose: {item.purpose}\n"
            f"Preferred Lab Type: "
            f"{item.preferred_lab_type or 'Not specified'}\n"
            f"Recommended Lab: "
            f"{best_lab_name or 'No suitable laboratory found'}\n\n"
            "Please review the request "
            "in LabPulse AI."
        ),
    )

    recommendation_status = (
        "RECOMMENDED"
        if recommendations
        else "VERIFICATION_PENDING"
    )

    recommendation_message = (
        "A laboratory recommendation is available. "
        "Verify its actual availability before approval."
        if recommendations
        else
        "No confirmed laboratory recommendation is available. "
        "The physical laboratory inventory and venue availability "
        "must be verified. Timetable assignments below are for "
        "review only and do not indicate free laboratories."
    )

    return {
        "success": True,
        "id": request_id,
        "recommended_lab": best_lab_name,
        "recommended_lab_id": best_lab_id,
        "recommendation_score": best_score,
        "recommendation_status": recommendation_status,
        "recommendation_message": recommendation_message,
        "recommendations": recommendations,
        "timetable_assignments_to_review": timetable_assignments_to_review,
        "notification": notification,
    }


# ============================================================
# UPDATE REQUEST STATUS
# ============================================================

@app.patch("/api/requests/{request_id}")
def update_request(
    request_id: int,
    status: str = Query(...),
):

    allowed_statuses = {
        "Pending",
        "Approved",
        "Rejected",
        "Completed",
    }

    if status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail="Invalid status.",
        )

    with get_db() as db:

        db.execute(
            """
            UPDATE lab_requests
            SET status=?
            WHERE id=?
            """,
            (
                status,
                request_id,
            ),
        )

    log_audit(
        "REQUEST_STATUS_CHANGE",
        "LAB_REQUEST",
        str(request_id),
        "Admin/HOD",
        f"Status changed to {status}",
    )

    return {
        "success": True,
        "id": request_id,
        "status": status,
        "message": (
            f"Request status updated "
            f"to {status}"
        ),
    }


# ============================================================
# ACTIVITIES â€” GET
# ============================================================

@app.get("/api/activities")
def activities():

    rows = query(
        """
        SELECT *
        FROM activities
        ORDER BY
            activity_date,
            start_time
        """
    )

    return [
        {
            **dict(row),
            "status": derived_activity_status(
                row
            ),
        }
        for row in rows
    ]


# ============================================================
# ACTIVITIES â€” CREATE
# ============================================================

@app.post("/api/activities")
def create_activity(
    item: ActivityIn,
):

    status = derived_activity_status(
        {
            "activity_date": item.activity_date,
            "start_time": item.start_time,
            "end_time": item.end_time,
            "status": item.status,
        }
    )

    with get_db() as db:

        cursor = db.execute(
            """
            INSERT INTO activities(
                activity_name,
                activity_type,
                activity_date,
                start_time,
                end_time,
                organizer,
                expected_students,
                laboratory,
                status,
                department
            )
            VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
            (
                item.activity_name,
                item.activity_type,
                item.activity_date,
                item.start_time,
                item.end_time,
                item.organizer,
                item.expected_students,
                item.laboratory,
                status,
                normalize_department(
                    item.department
                ),
            ),
        )

        activity_id = cursor.lastrowid

    if item.department:

        notification = send_hod_email(
            normalize_department(
                item.department
            ),
            (
                f"{item.activity_type}: "
                f"{item.activity_name} "
                f"â€” Lab Reservation"
            ),
            (
                f"A new "
                f"{item.activity_type.lower()} "
                f"has been planned.\n\n"
                f"Activity: {item.activity_name}\n"
                f"Department: {item.department}\n"
                f"Date: {item.activity_date}\n"
                f"Time: {item.start_time} - "
                f"{item.end_time}\n"
                f"Laboratory: {item.laboratory}\n"
                f"Expected Students: "
                f"{item.expected_students}\n"
                f"Organizer: {item.organizer}\n\n"
                "The selected laboratory is reserved "
                "by LabPulse AI for this activity time."
            ),
        )

    else:

        notification = {
            "sent": False,
            "reason": "No department selected",
        }

    return {
        "success": True,
        "id": activity_id,
        "status": status,
        "notification": notification,
    }


# ============================================================
# DELETE ACTIVITY
# ============================================================

@app.delete("/api/activities/{activity_id}")
def delete_activity(
    activity_id: int,
):

    with get_db() as db:

        db.execute(
            """
            DELETE FROM activities
            WHERE id=?
            """,
            (
                activity_id,
            ),
        )

    return {
        "success": True
    }


# ============================================================
# EMAIL
# ============================================================

def send_hod_email(
    department,
    subject,
    body,
):

    department = normalize_department(
        department
    )

    info = DEPARTMENT_HODS.get(
        department
    )

    if not info:

        return {
            "sent": False,
            "reason": (
                "No HOD mapping for department."
            ),
        }

    recipient = clean(
        info.get(
            "email",
            "",
        )
    )

    if not recipient:

        return {
            "sent": False,
            "reason": (
                "HOD email is not configured."
            ),
        }

    host = clean(
        os.getenv(
            "SMTP_HOST",
            "",
        )
    )

    user = clean(
        os.getenv(
            "SMTP_USER",
            "",
        )
    )

    password = clean(
        os.getenv(
            "SMTP_PASSWORD",
            "",
        )
    )

    if not (
        host
        and user
        and password
    ):

        return {
            "sent": False,
            "recipient": recipient,
            "reason": (
                "SMTP is not configured."
            ),
        }

    port = int(
        os.getenv(
            "SMTP_PORT",
            "587",
        )
    )

    use_tls = (
        os.getenv(
            "SMTP_TLS",
            "true",
        ).lower()
        == "true"
    )

    message = EmailMessage()

    message["From"] = user
    message["To"] = recipient
    message["Subject"] = subject

    message.set_content(
        body
    )

    with smtplib.SMTP(
        host,
        port,
        timeout=20,
    ) as server:

        if use_tls:

            server.starttls()

        server.login(
            user,
            password,
        )

        server.send_message(
            message
        )

    return {
        "sent": True,
        "recipient": recipient,
    }


# ============================================================
# EMAIL TEST
# ============================================================

@app.post("/api/email/test")
def email_test(
    item: EmailTestIn,
):

    host = clean(
        os.getenv(
            "SMTP_HOST",
            "",
        )
    )

    user = clean(
        os.getenv(
            "SMTP_USER",
            "",
        )
    )

    password = clean(
        os.getenv(
            "SMTP_PASSWORD",
            "",
        )
    )

    if not (
        host
        and user
        and password
    ):

        return {
            "sent": False,
            "recipient": item.recipient,
            "reason": (
                "SMTP is not configured."
            ),
        }

    port = int(
        os.getenv(
            "SMTP_PORT",
            "587",
        )
    )

    message = EmailMessage()

    message["From"] = user
    message["To"] = item.recipient

    message["Subject"] = (
        "LabPulse AI notification test"
    )

    message.set_content(
        "This is a test notification "
        "from LabPulse AI."
    )

    with smtplib.SMTP(
        host,
        port,
        timeout=20,
    ) as server:

        if (
            os.getenv(
                "SMTP_TLS",
                "true",
            ).lower()
            == "true"
        ):

            server.starttls()

        server.login(
            user,
            password,
        )

        server.send_message(
            message
        )

    return {
        "sent": True,
        "recipient": item.recipient,
    }


# ============================================================
# ANALYTICS
# ============================================================

@app.get("/api/analytics")
def analytics(
    selected_date: str = date.today().isoformat(),
):

    labs = query(
        """
        SELECT *
        FROM laboratories
        WHERE active=1
        ORDER BY id
        """
    )

    slots = current_slots()

    first_slot = (
        slots[0]
        if slots
        else DEFAULT_SLOTS[0]
    )

    states = available_state(
        selected_date,
        first_slot,
    )

    allocated = sum(
        row["status"]
        in {
            "Scheduled",
            "Reserved",
            "Busy (Faculty)",
            "Workshop / Activity",
        }
        for row in states
    )

    free = sum(
        row["status"] == "Available"
        for row in states
    )

    seminar = query(
        """
        SELECT COUNT(*) n
        FROM activities
        WHERE activity_date=?
          AND lower(activity_type)='seminar'
        """,
        (
            selected_date,
        ),
    )[0]["n"]

    history = query(
        """
        SELECT
            fu.lab_id,
            fu.lab_name,
            fu.usage_date,
            fu.time_slot,
            fu.department,
            fu.academic_year,
            fu.section,
            fu.status,
            fu.faculty
        FROM faculty_usage fu
        WHERE fu.usage_date=?
        ORDER BY
            fu.time_slot,
            fu.lab_id
        """,
        (
            selected_date,
        ),
    )

    by_department = query(
        """
        SELECT
            department AS name,
            COUNT(*) AS value
        FROM timetable
        GROUP BY department
        ORDER BY value DESC
        """
    )

    by_year = query(
        """
        SELECT
            academic_year AS name,
            COUNT(*) AS value
        FROM timetable
        GROUP BY academic_year
        ORDER BY academic_year
        """
    )

    by_resource = query(
        """
        SELECT
            resource_type AS name,
            COUNT(*) AS value
        FROM timetable
        GROUP BY resource_type
        ORDER BY value DESC
        """
    )

    by_lab = query(
        """
        SELECT 
            lab_venue AS lab_name,
            lab_venue AS lab_id,
            COUNT(*) AS scheduled
        FROM venue_mappings
        WHERE lab_venue IS NOT NULL AND lab_venue != ''
        GROUP BY lab_venue
        ORDER BY scheduled DESC
        LIMIT 15
        """
    )

    scheduled_slots = query(
        """
        SELECT COUNT(*) n
        FROM timetable
        """
    )[0]["n"]

    confirmed_actual_slots = query(
        """
        SELECT COUNT(*) n
        FROM faculty_usage
        WHERE status='BUSY'
        """
    )[0]["n"]

    return {
        "selected_date": selected_date,
        "total_laboratories": len(labs),
        "allocated_labs": allocated,
        "free_labs": free,
        "seminar_halls": seminar,
        "occupied_history": history,
        "by_lab": by_lab,
        "by_department": by_department,
        "by_year": by_year,
        "by_resource_type": by_resource,
        "scheduled_slots": scheduled_slots,
        "confirmed_actual_slots": confirmed_actual_slots,
    }


# ============================================================
# CONFLICT DETECTION (SECTION 6.6)
# ============================================================

def detect_conflicts(target_date: Optional[str] = None):
    dt = target_date or date.today().isoformat()
    conflicts = []

    # 1. Unverified timetable venue assignments
   
    unverified_venues = query(
        """
        SELECT
            vm.id,
            vm.lab_venue,
            vm.department,
            vm.section,
            vm.subject,
            vm.day,
            vm.time_slot,
            vm.academic_year
        FROM venue_mappings vm
        LEFT JOIN laboratories l
            ON (l.lab_id = vm.lab_venue OR l.lab_name = vm.lab_venue)
        WHERE (l.id IS NULL OR l.active = 0)
        LIMIT 6
        """
    )

    for v in unverified_venues:
        conflicts.append({
            "id": f"CONF-VM-{v['id']}",
            "laboratory": v["lab_venue"],
            "date": dt,
            "time_interval": f"{v['day']} ({v['time_slot']})",
            "overlapping_items": f"{v['academic_year']} {v['department']}-{v['section']} ({v['subject']})",
            "conflict_reason": f"Timetable venue assignment '{v['lab_venue']}' requires physical verification",
            "severity": "REVIEW",
            "resolution": "Verify lab physical capacity and register facility in Laboratory Management",
            "created_at": dt,
        })

    # 2. Check for faculty usage BUSY conflicts with approved requests
    busy_overlaps = query(
        """
        SELECT fu.lab_id, fu.lab_name, fu.time_slot, fu.faculty, lr.id AS req_id, lr.department, lr.purpose
        FROM faculty_usage fu
        JOIN lab_requests lr ON (lr.recommended_lab = fu.lab_id OR lr.recommended_lab = fu.lab_name)
          AND lr.request_date = fu.usage_date
          AND lr.time_slot = fu.time_slot
        WHERE fu.usage_date = ? AND fu.status = 'BUSY' AND lr.status = 'Approved'
        """,
        (dt,),
    )
    for b in busy_overlaps:
        conflicts.append({
            "id": f"CONF-BUSY-{b['req_id']}",
            "laboratory": b["lab_name"] or b["lab_id"],
            "date": dt,
            "time_interval": b["time_slot"],
            "overlapping_items": f"Faculty {b['faculty']} marked BUSY vs Approved Request #{b['req_id']} ({b['department']})",
            "conflict_reason": "Approved lab reservation overlaps faculty in-person usage override",
            "severity": "HIGH",
            "resolution": "Reassign request to alternative laboratory or reschedule faculty session",
            "created_at": dt,
        })

    return conflicts


# ============================================================
# LIVE LAB UTILIZATION (SECTION 6.5)
# ============================================================

def get_live_utilization(target_date: str, target_slot: str):
    states = available_state(target_date, target_slot)
    records = []

    for s in states:
        is_occupied = s["status"] != "Available"
        cap = s.get("capacity") or 40
        occ = cap if is_occupied else 0
        util_pct = 100.0 if is_occupied else 0.0
        src = "Faculty Actual Usage" if "Faculty" in s["status"] else (
            "Timetable Schedule" if "Scheduled" in s["status"] else (
                "Academic Reservation" if "Reserved" in s["status"] else "Baseline Availability"
            )
        )
        records.append({
            "lab_id": s["lab_id"],
            "lab_name": s["lab_name"],
            "department": s.get("department", "General"),
            "location": s.get("location", "College Campus"),
            "lab_type": s.get("lab_type", "LABORATORY"),
            "capacity": cap,
            "time_slot": target_slot,
            "status": s["status"],
            "occupied": is_occupied,
            "recorded_occupancy": occ,
            "utilization_percentage": util_pct,
            "data_source": src,
            "notes": s.get("reason", "Ready for allocation"),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })

    return records


@app.get("/api/conflicts")
def get_conflicts_endpoint(selected_date: Optional[str] = None):
    dt = selected_date or date.today().isoformat()
    confs = detect_conflicts(dt)
    return {
        "date": dt,
        "conflicts": confs,
        "total_conflicts": len(confs),
    }


@app.get("/api/live-utilization")
def live_utilization_endpoint(
    selected_date: Optional[str] = None,
    time_slot: Optional[str] = None,
):
    dt = selected_date or date.today().isoformat()
    slots = current_slots()
    sl = time_slot or (slots[0] if slots else DEFAULT_SLOTS[0])
    recs = get_live_utilization(dt, sl)
    occ_count = len([r for r in recs if r["occupied"]])
    rate = round((occ_count / max(len(recs), 1)) * 100, 1)

    return {
        "date": dt,
        "time_slot": sl,
        "records": recs,
        "utilization": recs,
        "summary": {
            "total_monitored": len(recs),
            "occupied_count": occ_count,
            "overall_utilization": rate,
        },
    }


@app.get("/api/audit-logs")
def audit_logs_endpoint(limit: int = 50):
    return get_audit_logs(limit)


# ============================================================
# DASHBOARD
# ============================================================

@app.get("/api/dashboard")
def dashboard():

    selected_date = date.today().isoformat()

    slots = current_slots()
    current_slot = slots[0] if slots else DEFAULT_SLOTS[0]

    states = []

    for slot in slots:

        states.extend(
            available_state(
                selected_date,
                slot,
            )
        )

    priority = {
        "Busy (Faculty)": 5,
        "Reserved": 4,
        "Workshop / Activity": 3,
        "Scheduled": 2,
        "Available": 1,
    }

    by_lab = {}

    for state in states:

        lab_id = state["lab_id"]

        if (
            lab_id not in by_lab
            or priority.get(
                state["status"],
                0,
            )
            >
            priority.get(
                by_lab[lab_id]["status"],
                0,
            )
        ):

            by_lab[lab_id] = state

    values = list(
        by_lab.values()
    )

    hard_occupied = {
        state["lab_id"]
        for state in values
        if state["status"]
        in {
            "Busy (Faculty)",
            "Reserved",
            "Workshop / Activity",
        }
    }

    total_timetable = query(
        """
        SELECT COUNT(*) n
        FROM timetable
        """
    )[0]["n"]

    actual_busy = query(
        """
        SELECT COUNT(*) n
        FROM faculty_usage
        WHERE status='BUSY'
        """
    )[0]["n"]

    utilization_rate = round(
        (
            actual_busy
            /
            max(
                total_timetable,
                1,
            )
        )
        * 100,
        1,
    )

    pending_requests = query(
        "SELECT COUNT(*) n FROM lab_requests WHERE status='Pending'"
    )[0]["n"]

    conflicts = detect_conflicts(selected_date)
    live_util = get_live_utilization(selected_date, current_slot)
    recent_activity = get_audit_logs(10)

    return {
        # Section 6.1 KPIs
        "total_laboratories": len(values),
        "available_labs": len(values) - len(hard_occupied),
        "occupied_labs": len(hard_occupied),
        "pending_requests": pending_requests,
        "active_conflicts": len(conflicts),
        "utilization_rate": utilization_rate,

        # Section 6.5 Live Lab Utilization & Section 6.6 Upcoming Resource Conflicts
        "live_utilization": live_util,
        "upcoming_conflicts": conflicts,
        "recent_activity": recent_activity,

        # Backwards compatibility keys
        "laboratories": len(values),
        "occupied_today": len(hard_occupied),
        "available_today": len(values) - len(hard_occupied),
        "requests": query("SELECT COUNT(*) n FROM lab_requests")[0]["n"],
        "activities": query("SELECT COUNT(*) n FROM activities")[0]["n"],
        "years": query("SELECT academic_year AS name, COUNT(*) AS value FROM timetable GROUP BY academic_year ORDER BY academic_year"),
        "lab_status": values,
        "timetable_rows": total_timetable,
        "faculty_confirmed_busy": actual_busy,
    }


# ============================================================
# ML STATUS
#
# This endpoint reports whether genuine ML prediction data
# exists. It does NOT invent accuracy or predictions.
# ============================================================

@app.get("/api/ml/status")
def ml_status():

    try:

        utilization_rows = query(
            """
            SELECT COUNT(*) n
            FROM ml_utilization_data
            """
        )[0]["n"]

        prediction_rows = query(
            """
            SELECT COUNT(*) n
            FROM ml_predictions
            """
        )[0]["n"]

    except Exception:

        utilization_rows = 0
        prediction_rows = 0

    return {
        "model": "Random Forest Regressor",
        "training_data_rows": utilization_rows,
        "prediction_rows": prediction_rows,
        "trained": prediction_rows > 0,
        "metrics_available": False,
        "message": (
            "ML metrics will be shown only "
            "after genuine historical utilization "
            "data is collected and a model is trained."
        ),
    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": APP_FULL_NAME,
        "status": "running",
        "version": APP_VERSION,
        "database": "SQLite",
        "data_source": (
            "Real college timetable "
            "uploaded through Excel/CSV"
        ),
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/api/health")
def health():

    try:

        with get_db() as db:

            db.execute(
                "SELECT 1"
            )

        timetable_count = query(
            """
            SELECT COUNT(*) n
            FROM timetable
            """
        )[0]["n"]

        return {
            "status": "online",
            "database": "connected",
            "engine": "SQLite",
            "timetable_rows": timetable_count,
        }

    except Exception as error:

        return {
            "status": "offline",
            "database": "disconnected",
            "error": str(error),
        }
