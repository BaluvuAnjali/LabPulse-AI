import pandas as pd
from pathlib import Path


# ============================================================
# LABPULSE AI
# STEP 4 - ACADEMIC YEAR FILTERING
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "training_data"
    / "processed_timetable.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "training_data"
    / "yearwise"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


print("=" * 80)
print("LABPULSE AI - ACADEMIC YEAR FILTERING")
print("=" * 80)

print(f"\nInput file:")
print(INPUT_FILE)


# ============================================================
# 1. LOAD PROCESSED TIMETABLE
# ============================================================

if not INPUT_FILE.exists():

    print("\nERROR:")
    print("processed_timetable.csv was not found.")

    raise SystemExit(1)


df = pd.read_csv(INPUT_FILE)

print("\n✓ Processed timetable loaded")

print(f"Total records: {len(df)}")


# ============================================================
# 2. CHECK YEAR COLUMN
# ============================================================

if "academic_year_normalized" not in df.columns:

    print(
        "\nERROR: academic_year_normalized column "
        "is missing."
    )

    raise SystemExit(1)


# ============================================================
# 3. DISPLAY AVAILABLE YEARS
# ============================================================

years = sorted(
    df["academic_year_normalized"]
    .dropna()
    .unique()
)

print("\nAvailable academic years:")

for year in years:

    count = (
        df["academic_year_normalized"]
        == year
    ).sum()

    print(
        f" - {year}: {count} records"
    )


# ============================================================
# 4. CREATE YEAR-WISE DATASETS
# ============================================================

print("\n" + "=" * 80)
print("CREATING YEAR-WISE DATASETS")
print("=" * 80)


for year in years:

    year_df = df[
        df["academic_year_normalized"]
        == year
    ].copy()

    # --------------------------------------------------------
    # Create safe filename
    # --------------------------------------------------------

    safe_year = (
        year
        .lower()
        .replace(" ", "_")
    )

    output_file = (
        OUTPUT_DIR
        / f"{safe_year}_timetable.csv"
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    year_df.to_csv(
        output_file,
        index=False
    )

    print(
        f"\n✓ {year}"
    )

    print(
        f"  Total records : {len(year_df)}"
    )

    print(
        f"  Departments   : "
        f"{year_df['department'].nunique()}"
    )

    print(
        f"  Sections      : "
        f"{year_df['branch_section'].nunique()}"
    )

    print(
        f"  Subjects      : "
        f"{year_df['subject_normalized'].nunique()}"
    )

    print(
        f"  Lab records   : "
        f"{year_df['is_lab_subject'].sum()}"
    )

    print(
        f"  Output        : "
        f"{output_file.name}"
    )


# ============================================================
# 5. VERIFY YEAR ISOLATION
# ============================================================

print("\n" + "=" * 80)
print("YEAR ISOLATION VERIFICATION")
print("=" * 80)


for year in years:

    safe_year = (
        year
        .lower()
        .replace(" ", "_")
    )

    output_file = (
        OUTPUT_DIR
        / f"{safe_year}_timetable.csv"
    )

    year_df = pd.read_csv(
        output_file
    )

    unique_years = (
        year_df[
            "academic_year_normalized"
        ]
        .unique()
    )

    print(
        f"\n{year}:"
    )

    print(
        f"  Records: {len(year_df)}"
    )

    print(
        f"  Years contained: "
        f"{list(unique_years)}"
    )

    # Make sure the file contains
    # only its intended academic year.

    if (
        len(unique_years) == 1
        and unique_years[0] == year
    ):

        print(
            "  ✓ YEAR ISOLATION PASSED"
        )

    else:

        print(
            "  ✗ YEAR ISOLATION FAILED"
        )


# ============================================================
# 6. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

print(
    "\nMaster dataset:"
)

print(
    f"  {len(df)} total records"
)

print(
    "\nYear-wise datasets created:"
)

for year in years:

    safe_year = (
        year
        .lower()
        .replace(" ", "_")
    )

    print(
        f"  - "
        f"{safe_year}_timetable.csv"
    )


print("\n" + "=" * 80)
print("STEP 4 COMPLETED")
print("=" * 80)