import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "training_data" / "LabPulse_AI_Master_Timetable.csv"

print("=" * 70)
print("LABPULSE AI - MASTER TIMETABLE INSPECTION")
print("=" * 70)

print(f"\nLoading file:")
print(CSV_PATH)

if not CSV_PATH.exists():
    print("\nERROR: Master CSV not found.")
    print("Expected location:")
    print(CSV_PATH)
    raise SystemExit(1)

df = pd.read_csv(CSV_PATH)

print("\n✓ CSV loaded successfully")

print("\n" + "=" * 70)
print("1. DATASET SIZE")
print("=" * 70)

print(f"Rows    : {len(df)}")
print(f"Columns : {len(df.columns)}")

print("\n" + "=" * 70)
print("2. COLUMNS")
print("=" * 70)

for i, column in enumerate(df.columns, start=1):
    print(f"{i}. {column}")

print("\n" + "=" * 70)
print("3. ACADEMIC YEARS")
print("=" * 70)

print(df["academic_year"].value_counts(dropna=False))

print("\n" + "=" * 70)
print("4. DEPARTMENTS")
print("=" * 70)

print(sorted(df["department"].dropna().unique()))

print("\n" + "=" * 70)
print("5. DAYS")
print("=" * 70)

print(sorted(df["day"].dropna().unique()))

print("\n" + "=" * 70)
print("6. PERIODS")
print("=" * 70)

print(sorted(df["period"].dropna().unique()))

print("\n" + "=" * 70)
print("7. SUBJECT COUNT")
print("=" * 70)

print(f"Unique subjects: {df['subject'].nunique()}")

print("\n" + "=" * 70)
print("8. SAMPLE DATA")
print("=" * 70)

print(df.head(10).to_string(index=False))

print("\n" + "=" * 70)
print("9. MISSING VALUES")
print("=" * 70)

print(df.isnull().sum())

print("\n" + "=" * 70)
print("10. DUPLICATE ROWS")
print("=" * 70)

print(f"Duplicate rows: {df.duplicated().sum()}")

print("\n" + "=" * 70)
print("INSPECTION COMPLETE")
print("=" * 70)