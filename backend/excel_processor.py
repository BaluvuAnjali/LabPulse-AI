from pathlib import Path
import re
import pandas as pd


# ============================================================
# REAL LABPULSE AI TIMETABLE FORMAT
# ============================================================

REQUIRED_COLUMNS = {
    "academic_year",
    "department",
    "branch_section",
    "day",
    "period",
    "time_slot",
    "subject",
    "faculty",
    "students",
}


# ============================================================
# COLUMN ALIASES
# ============================================================

ALIASES = {
    "Academic Year": "academic_year",
    "AcademicYear": "academic_year",
    "Year": "academic_year",

    "Department": "department",
    "Dept": "department",
    "Branch": "department",

    "Branch Section": "branch_section",
    "BranchSection": "branch_section",
    "Section": "branch_section",

    "Day": "day",

    "Period": "period",

    "Time Slot": "time_slot",
    "TimeSlot": "time_slot",
    "Time": "time_slot",

    "Subject": "subject",
    "Course": "subject",
    "Course Name": "subject",

    "Faculty": "faculty",
    "Faculty Name": "faculty",
    "Teacher": "faculty",
    "Staff": "faculty",

    "Students": "students",
    "Student Count": "students",
    "Strength": "students",
}


# ============================================================
# NORMALIZE COLUMN NAME
# ============================================================

def normalize_column_name(column):
    """
    Converts different column naming styles into
    the standard LabPulse AI column names.
    """

    original = str(column).strip()

    if original in ALIASES:
        return ALIASES[original]

    normalized = (
        original
        .lower()
        .strip()
        .replace(" ", "_")
        .replace("-", "_")
    )

    alias_lower = {
        key.lower(): value
        for key, value in ALIASES.items()
    }

    if normalized in alias_lower:
        return alias_lower[normalized]

    return normalized


# ============================================================
# NORMALIZE DATAFRAME COLUMNS
# ============================================================

def normalize_columns(df):
    df = df.copy()

    df.columns = [
        normalize_column_name(column)
        for column in df.columns
    ]

    return df


# ============================================================
# NORMALIZE ACADEMIC YEAR
# ============================================================

def normalize_academic_year(value):

    value = str(value).strip()

    if not value:
        return ""

    normalized = value.lower()

    if (
        "1st" in normalized
        or "first" in normalized
        or normalized in {"i", "1"}
    ):
        return "IST"

    if (
        "2nd" in normalized
        or "second" in normalized
        or normalized in {"ii", "2"}
    ):
        return "2ND"

    if (
        "3rd" in normalized
        or "third" in normalized
        or normalized in {"iii", "3"}
    ):
        return "3RD"

    if (
        "4th" in normalized
        or "fourth" in normalized
        or normalized in {"iv", "4"}
    ):
        return "4TH"

    return value.upper()


# ============================================================
# NORMALIZE DAY
# ============================================================

def normalize_day(value):

    value = str(value).strip()

    if not value:
        return ""

    return value.upper()


# ============================================================
# NORMALIZE PERIOD
# ============================================================

def normalize_period(value):

    value = str(value).strip()

    if not value:
        return ""

    normalized = value.upper()

    match = re.search(r"(\d+)", normalized)

    if match:
        return f"Period-{match.group(1)}"

    return normalized


# ============================================================
# NORMALIZE TIME SLOT
# ============================================================

def normalize_time_slot(value):

    value = str(value).strip()

    if not value:
        return ""

    return value


# ============================================================
# NORMALIZE SUBJECT
# ============================================================

def normalize_subject(value):

    value = str(value).strip()

    if not value:
        return ""

    # Remove unnecessary repeated spaces
    value = re.sub(r"\s+", " ", value)

    return value.upper()


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(value):

    if pd.isna(value):
        return ""

    return str(value).strip()


# ============================================================
# DETECT LAB SUBJECT
# ============================================================

def is_lab_subject(subject):

    subject = normalize_subject(subject)

    if not subject:
        return False

    normalized = (
        subject
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
        .replace(".", "")
    )

    # Explicit LAB / LB patterns
    if "LAB" in normalized:
        return True

    if normalized.endswith("LB"):
        return True

    # Common laboratory naming patterns
    lab_keywords = [
        "PRACTICAL",
        "WORKSHOP",
        "STUDIO",
    ]

    for keyword in lab_keywords:
        if keyword in normalized:
            return True

    return False


# ============================================================
# RESOURCE TYPE
# ============================================================

def get_resource_type(subject):

    if is_lab_subject(subject):
        return "LAB"

    return "THEORY"


# ============================================================
# TIME PARSING
# ============================================================

def parse_time(value):

    value = str(value).strip()

    if not value:
        return None

    # Convert different dash characters
    value = (
        value
        .replace("–", "-")
        .replace("—", "-")
        .replace("−", "-")
    )

    # Example:
    # 09:30-10:30
    # 09:30 AM - 10:30 AM

    parts = re.split(r"\s*-\s*", value)

    if len(parts) != 2:
        return None

    start = parts[0].strip()
    end = parts[1].strip()

    formats = [
        "%H:%M",
        "%I:%M %p",
        "%I:%M%p",
        "%H.%M",
        "%I.%M %p",
        "%I.%M%p",
    ]

    start_time = None
    end_time = None

    for fmt in formats:

        if start_time is None:
            try:
                start_time = pd.to_datetime(
                    start,
                    format=fmt
                )
            except Exception:
                pass

        if end_time is None:
            try:
                end_time = pd.to_datetime(
                    end,
                    format=fmt
                )
            except Exception:
                pass

    if start_time is None or end_time is None:
        return None

    return start_time, end_time


# ============================================================
# CALCULATE DURATION
# ============================================================

def calculate_duration_minutes(time_slot):

    parsed = parse_time(time_slot)

    if parsed is None:
        return 0

    start_time, end_time = parsed

    duration = (
        end_time - start_time
    ).total_seconds() / 60

    # Handle accidental midnight crossing
    if duration < 0:
        duration += 24 * 60

    return int(duration)


# ============================================================
# READ SOURCE FILE
# ============================================================

def read_source_file(file_path):

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Timetable file not found: {file_path}"
        )

    suffix = path.suffix.lower()

    # --------------------------------------------------------
    # CSV
    # --------------------------------------------------------

    if suffix == ".csv":

        return {
            "Timetable": pd.read_csv(path)
        }

    # --------------------------------------------------------
    # EXCEL
    # --------------------------------------------------------

    if suffix in {".xlsx", ".xls"}:

        excel_file = pd.ExcelFile(path)

        sheets = {}

        for sheet_name in excel_file.sheet_names:

            sheets[sheet_name] = pd.read_excel(
                path,
                sheet_name=sheet_name
            )

        return sheets

    raise ValueError(
        "Unsupported timetable file type. "
        "Use CSV, XLSX or XLS."
    )


# ============================================================
# SELECT TIMETABLE SHEET
# ============================================================

def select_timetable_sheet(sheets):

    if not sheets:
        raise ValueError(
            "The uploaded timetable file contains no sheets."
        )

    # Prefer exact Timetable sheet
    for sheet_name in sheets:

        if str(sheet_name).strip().lower() == "timetable":
            return sheets[sheet_name]

    # Otherwise use first sheet
    first_sheet = next(iter(sheets.values()))

    return first_sheet


# ============================================================
# VALIDATE REQUIRED COLUMNS
# ============================================================

def validate_columns(df):

    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:

        raise ValueError(
            "Timetable sheet is missing required fields: "
            + ", ".join(sorted(missing))
        )


# ============================================================
# PROCESS TIMETABLE
# ============================================================

def process_timetable(file_path: str):

    # --------------------------------------------------------
    # STEP 1 — Read file
    # --------------------------------------------------------

    sheets = read_source_file(file_path)

    # --------------------------------------------------------
    # STEP 2 — Select timetable sheet
    # --------------------------------------------------------

    df = select_timetable_sheet(sheets)

    # --------------------------------------------------------
    # STEP 3 — Normalize column names
    # --------------------------------------------------------

    df = normalize_columns(df)

    # --------------------------------------------------------
    # STEP 4 — Replace missing values
    # --------------------------------------------------------

    df = df.fillna("")

    # --------------------------------------------------------
    # STEP 5 — Validate real timetable columns
    # --------------------------------------------------------

    validate_columns(df)

    # --------------------------------------------------------
    # STEP 6 — Normalize text columns
    # --------------------------------------------------------

    text_columns = [
        "academic_year",
        "department",
        "branch_section",
        "day",
        "period",
        "time_slot",
        "subject",
        "faculty",
    ]

    for column in text_columns:

        df[column] = (
            df[column]
            .apply(normalize_text)
        )

    # --------------------------------------------------------
    # STEP 7 — Normalize academic year
    # --------------------------------------------------------

    df["academic_year"] = (
        df["academic_year"]
        .apply(normalize_academic_year)
    )

    # --------------------------------------------------------
    # STEP 8 — Normalize day
    # --------------------------------------------------------

    df["day"] = (
        df["day"]
        .apply(normalize_day)
    )

    # --------------------------------------------------------
    # STEP 9 — Normalize period
    # --------------------------------------------------------

    df["period"] = (
        df["period"]
        .apply(normalize_period)
    )

    # --------------------------------------------------------
    # STEP 10 — Normalize subject
    # --------------------------------------------------------

    df["subject"] = (
        df["subject"]
        .apply(normalize_subject)
    )

    # --------------------------------------------------------
    # STEP 11 — Convert students to integer
    # --------------------------------------------------------

    df["students"] = (
        pd.to_numeric(
            df["students"],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
    )

    # --------------------------------------------------------
    # STEP 12 — Remove completely empty rows
    # --------------------------------------------------------

    df = df[
        (df["academic_year"] != "")
        &
        (df["department"] != "")
        &
        (df["branch_section"] != "")
        &
        (df["day"] != "")
        &
        (df["period"] != "")
        &
        (df["time_slot"] != "")
        &
        (df["subject"] != "")
    ].copy()

    # --------------------------------------------------------
    # STEP 13 — Detect LAB / THEORY
    # --------------------------------------------------------

    df["resource_type"] = (
        df["subject"]
        .apply(get_resource_type)
    )

    # --------------------------------------------------------
    # STEP 14 — Calculate exact duration
    # --------------------------------------------------------

    df["duration_minutes"] = (
        df["time_slot"]
        .apply(calculate_duration_minutes)
    )

    # --------------------------------------------------------
    # STEP 15 — Add source file
    # --------------------------------------------------------

    df["source_file"] = Path(
        file_path
    ).name

    # --------------------------------------------------------
    # STEP 16 — Remove duplicate rows
    # --------------------------------------------------------

    df = df.drop_duplicates(
        subset=[
            "academic_year",
            "department",
            "branch_section",
            "day",
            "period",
            "time_slot",
            "subject",
            "faculty",
        ]
    ).copy()

    # --------------------------------------------------------
    # STEP 17 — Final column order
    # --------------------------------------------------------

    final_columns = [
        "academic_year",
        "department",
        "branch_section",
        "day",
        "period",
        "time_slot",
        "subject",
        "faculty",
        "students",
        "resource_type",
        "duration_minutes",
        "source_file",
    ]

    df = df[final_columns]

    # --------------------------------------------------------
    # STEP 18 — Validation checks
    # --------------------------------------------------------

    if len(df) == 0:

        raise ValueError(
            "No valid timetable records were found "
            "after processing."
        )

    invalid_duration = df[
        df["duration_minutes"] <= 0
    ]

    if not invalid_duration.empty:

        raise ValueError(
            "Invalid time slot detected. "
            "Could not calculate duration for "
            f"{len(invalid_duration)} timetable rows."
        )

    # --------------------------------------------------------
    # STEP 19 — Return records
    # --------------------------------------------------------

    return df.to_dict("records")