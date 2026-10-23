import pandas as pd
from pathlib import Path


# ============================================================
# LABPULSE AI
# STEP 3 - LAB SESSION ANALYSIS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "training_data"
    / "processed_timetable.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "training_data"
    / "lab_sessions.csv"
)


print("=" * 80)
print("LABPULSE AI - LAB SESSION ANALYSIS")
print("=" * 80)

print(f"\nInput file:")
print(INPUT_FILE)


# ============================================================
# 1. LOAD PROCESSED TIMETABLE
# ============================================================

if not INPUT_FILE.exists():
    print("\nERROR: processed_timetable.csv not found.")
    raise SystemExit(1)

df = pd.read_csv(INPUT_FILE)

print("\n✓ Processed timetable loaded")

print(f"Total rows: {len(df)}")


# ============================================================
# 2. KEEP ONLY LAB ROWS
# ============================================================

lab_df = df[
    df["is_lab_subject"] == True
].copy()

print(f"Lab rows: {len(lab_df)}")


# ============================================================
# 3. PERIOD NUMBER
# ============================================================

lab_df["period_number"] = (
    lab_df["period"]
    .str.extract(r"(\d+)")
    .astype(int)
)


# ============================================================
# 4. ORDER DATA
# ============================================================

lab_df = lab_df.sort_values(
    by=[
        "academic_year_normalized",
        "department",
        "branch_section",
        "day_normalized",
        "subject_normalized",
        "faculty",
        "period_number"
    ]
).reset_index(drop=True)


# ============================================================
# 5. IDENTIFY CONTINUOUS LAB SESSIONS
# ============================================================

group_columns = [
    "academic_year_normalized",
    "department",
    "branch_section",
    "day_normalized",
    "subject_normalized",
    "faculty"
]


lab_df["previous_period"] = (
    lab_df
    .groupby(group_columns)["period_number"]
    .shift(1)
)


lab_df["new_session"] = (
    lab_df["previous_period"].isna()
    |
    (
        lab_df["period_number"]
        != lab_df["previous_period"] + 1
    )
)


lab_df["session_number"] = (
    lab_df["new_session"]
    .groupby(
        [
            lab_df[col]
            for col in group_columns
        ]
    )
    .cumsum()
)


# ============================================================
# 6. BUILD SESSION RECORDS
# ============================================================

sessions = []

for keys, group in lab_df.groupby(
    group_columns + ["session_number"]
):

    (
        academic_year,
        department,
        branch_section,
        day,
        subject,
        faculty,
        session_number
    ) = keys

    group = group.sort_values(
        "period_number"
    )

    first_row = group.iloc[0]
    last_row = group.iloc[-1]

    start_time = first_row["start_time"]
    end_time = last_row["end_time"]

    duration_minutes = (
        pd.to_datetime(
            end_time,
            format="%H:%M"
        )
        -
        pd.to_datetime(
            start_time,
            format="%H:%M"
        )
    ).total_seconds() / 60

    duration_minutes = int(
        duration_minutes
    )

    sessions.append({

        "academic_year": academic_year,

        "department": department,

        "branch_section": branch_section,

        "day": day,

        "subject": subject,

        "faculty": faculty,

        "start_time": start_time,

        "end_time": end_time,

        "duration_minutes": duration_minutes,

        "duration_hours": round(
            duration_minutes / 60,
            2
        ),

        "first_period": first_row[
            "period"
        ],

        "last_period": last_row[
            "period"
        ],

        "period_count": len(group),

        "students": int(
            first_row["students"]
        )

    })


session_df = pd.DataFrame(
    sessions
)


# ============================================================
# 7. CREATE SESSION ID
# ============================================================

session_df.insert(
    0,
    "lab_session_id",
    range(
        1,
        len(session_df) + 1
    )
)


# ============================================================
# 8. SAVE
# ============================================================

session_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 9. SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("LAB SESSION SUMMARY")
print("=" * 80)

print(
    f"\nLab timetable rows : {len(lab_df)}"
)

print(
    f"Actual lab sessions: {len(session_df)}"
)

print(
    f"Rows combined into sessions: "
    f"{len(lab_df) - len(session_df)}"
)


# ============================================================
# 10. SESSION DURATION DISTRIBUTION
# ============================================================

print("\n" + "=" * 80)
print("LAB SESSION DURATION DISTRIBUTION")
print("=" * 80)

print(
    session_df[
        "duration_minutes"
    ]
    .value_counts()
    .sort_index()
)


# ============================================================
# 11. YEAR-WISE SESSION COUNT
# ============================================================

print("\n" + "=" * 80)
print("YEAR-WISE LAB SESSION COUNT")
print("=" * 80)

print(
    session_df[
        "academic_year"
    ]
    .value_counts()
    .sort_index()
)


# ============================================================
# 12. SUBJECT-WISE SESSION COUNT
# ============================================================

print("\n" + "=" * 80)
print("LAB SUBJECT SESSION COUNT")
print("=" * 80)

subject_counts = (
    session_df[
        "subject"
    ]
    .value_counts()
)

print(
    subject_counts.to_string()
)


# ============================================================
# 13. SHOW SAMPLE SESSIONS
# ============================================================

print("\n" + "=" * 80)
print("SAMPLE LAB SESSIONS")
print("=" * 80)

print(
    session_df[
        [
            "lab_session_id",
            "academic_year",
            "department",
            "branch_section",
            "day",
            "subject",
            "start_time",
            "end_time",
            "duration_minutes",
            "duration_hours",
            "first_period",
            "last_period",
            "period_count",
            "students"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# 14. CHECK FOR SUSPICIOUS SINGLE-PERIOD LABS
# ============================================================

print("\n" + "=" * 80)
print("SINGLE-PERIOD LAB SESSIONS")
print("=" * 80)

single_period = session_df[
    session_df["period_count"] == 1
]

print(
    f"Single-period lab sessions: "
    f"{len(single_period)}"
)

if len(single_period) > 0:

    print(
        single_period[
            [
                "academic_year",
                "department",
                "branch_section",
                "day",
                "subject",
                "start_time",
                "end_time",
                "duration_minutes"
            ]
        ]
        .head(30)
        .to_string(index=False)
    )


# ============================================================
# 15. FINAL OUTPUT
# ============================================================

print("\n" + "=" * 80)
print("OUTPUT")
print("=" * 80)

print(
    f"\nLab session file created:"
)

print(
    OUTPUT_FILE
)

print("\n" + "=" * 80)
print("STEP 3 COMPLETED")
print("=" * 80)