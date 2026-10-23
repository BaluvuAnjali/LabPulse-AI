import pandas as pd
import re
from pathlib import Path


# ============================================================
# LABPULSE AI
# STEP 2 - TIMETABLE PREPROCESSING
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "training_data" / "LabPulse_AI_Master_Timetable.csv"
OUTPUT_FILE = BASE_DIR / "training_data" / "processed_timetable.csv"


print("=" * 80)
print("LABPULSE AI - TIMETABLE PREPROCESSING")
print("=" * 80)

print(f"\nInput file:")
print(INPUT_FILE)

if not INPUT_FILE.exists():
    print("\nERROR: Master timetable CSV not found.")
    raise SystemExit(1)


# ============================================================
# 1. LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("\n✓ Master timetable loaded successfully")

print(f"Rows    : {len(df)}")
print(f"Columns : {len(df.columns)}")


# ============================================================
# 2. STANDARDIZE COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

print("\n✓ Column names standardized")


# ============================================================
# 3. CLEAN STRING COLUMNS
# ============================================================

string_columns = [
    "academic_year",
    "department",
    "branch_section",
    "day",
    "period",
    "time_slot",
    "subject",
    "faculty"
]

for column in string_columns:
    if column in df.columns:
        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

print("✓ Text fields cleaned")


# ============================================================
# 4. NORMALIZE SUBJECT NAMES
# ============================================================

df["subject_normalized"] = (
    df["subject"]
    .str.upper()
    .str.strip()
    .str.replace(r"\s+", " ", regex=True)
)

print("✓ Subject names normalized")


# ============================================================
# 5. NORMALIZE ACADEMIC YEAR
# ============================================================

df["academic_year_normalized"] = (
    df["academic_year"]
    .str.upper()
    .str.strip()
)

print("✓ Academic years normalized")


# ============================================================
# 6. NORMALIZE DAY
# ============================================================

df["day_normalized"] = (
    df["day"]
    .str.upper()
    .str.strip()
)

print("✓ Days normalized")


# ============================================================
# 7. NORMALIZE TIME SLOT
# ============================================================

df["time_slot_normalized"] = (
    df["time_slot"]
    .str.upper()
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

print("✓ Time slots normalized")


# ============================================================
# 8. PARSE TIME SLOT
# ============================================================

def parse_time(time_text):

    if not time_text:
        return None

    text = time_text.strip().upper()

    match = re.match(
        r"^\s*(\d{1,2}:\d{2}\s*[AP]M)\s*-\s*(\d{1,2}:\d{2}\s*[AP]M)\s*$",
        text
    )

    if not match:
        return None

    start_text = match.group(1)
    end_text = match.group(2)

    start_time = pd.to_datetime(
        start_text,
        format="%I:%M %p"
    )

    end_time = pd.to_datetime(
        end_text,
        format="%I:%M %p"
    )

    return start_time, end_time


def calculate_duration_minutes(time_text):

    parsed = parse_time(time_text)

    if parsed is None:
        return None

    start_time, end_time = parsed

    duration = (
        end_time - start_time
    ).total_seconds() / 60

    return int(duration)


def extract_start_time(time_text):

    parsed = parse_time(time_text)

    if parsed is None:
        return ""

    start_time, _ = parsed

    return start_time.strftime("%H:%M")


def extract_end_time(time_text):

    parsed = parse_time(time_text)

    if parsed is None:
        return ""

    _, end_time = parsed

    return end_time.strftime("%H:%M")


df["start_time"] = df["time_slot_normalized"].apply(
    extract_start_time
)

df["end_time"] = df["time_slot_normalized"].apply(
    extract_end_time
)

df["duration_minutes"] = df["time_slot_normalized"].apply(
    calculate_duration_minutes
)

df["duration_hours"] = (
    df["duration_minutes"] / 60
)

print("✓ Time slots parsed")
print("✓ Actual duration calculated")


# ============================================================
# 9. IDENTIFY LAB-RELATED SUBJECTS
# ============================================================

def is_lab_subject(subject):

    if not subject:
        return False

    text = (
        subject
        .upper()
        .strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
    )

    lab_patterns = [
        "LAB",
        "LB"
    ]

    return any(
        pattern in text
        for pattern in lab_patterns
    )


df["is_lab_subject"] = df["subject_normalized"].apply(
    is_lab_subject
)

print("✓ Lab-related subjects detected")


# ============================================================
# 10. DISPLAY LAB STATISTICS
# ============================================================

lab_rows = df[df["is_lab_subject"] == True]

print("\n" + "=" * 80)
print("LAB ANALYSIS")
print("=" * 80)

print(f"\nTotal timetable rows : {len(df)}")
print(f"Lab-related rows     : {len(lab_rows)}")
print(f"Non-lab rows         : {len(df) - len(lab_rows)}")

print("\nAcademic year-wise lab rows:")

print(
    lab_rows["academic_year_normalized"]
    .value_counts()
    .sort_index()
)


print("\nUnique lab-related subjects:")

lab_subjects = sorted(
    lab_rows["subject_normalized"]
    .unique()
)

for subject in lab_subjects:
    print(f" - {subject}")


# ============================================================
# 11. CHECK DURATION DISTRIBUTION
# ============================================================

print("\n" + "=" * 80)
print("TIME DURATION ANALYSIS")
print("=" * 80)

print(
    df["duration_minutes"]
    .value_counts()
    .sort_index()
)


# ============================================================
# 12. CHECK INVALID TIME SLOTS
# ============================================================

invalid_time_rows = df[
    df["duration_minutes"].isna()
]

print("\nInvalid/unparsed time slots:")
print(len(invalid_time_rows))

if len(invalid_time_rows) > 0:

    print(
        invalid_time_rows[
            ["day", "period", "time_slot"]
        ]
        .drop_duplicates()
        .to_string(index=False)
    )


# ============================================================
# 13. CREATE RESOURCE TYPE
# ============================================================

df["resource_type"] = "THEORY"

df.loc[
    df["is_lab_subject"] == True,
    "resource_type"
] = "LAB"

print("\n✓ Resource type assigned")


# ============================================================
# 14. CREATE UNIQUE RECORD ID
# ============================================================

df.insert(
    0,
    "record_id",
    range(1, len(df) + 1)
)

print("✓ Record IDs generated")


# ============================================================
# 15. SAVE PROCESSED DATA
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n✓ Processed timetable saved")

print(f"\nOutput file:")
print(OUTPUT_FILE)


# ============================================================
# 16. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("PREPROCESSING SUMMARY")
print("=" * 80)

print(f"Original rows       : {len(df)}")
print(f"Processed rows      : {len(df)}")
print(f"Lab-related rows    : {df['is_lab_subject'].sum()}")
print(f"Theory rows         : {(df['is_lab_subject'] == False).sum()}")
print(
    f"Invalid time rows   : {df['duration_minutes'].isna().sum()}"
)

print("\nAcademic years:")

for year in sorted(
    df["academic_year_normalized"].unique()
):

    count = (
        df["academic_year_normalized"] == year
    ).sum()

    print(f" - {year}: {count} rows")


print("\n" + "=" * 80)
print("STEP 2 COMPLETED")
print("=" * 80)