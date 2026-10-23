from backend.database import query

print("YEAR VALUES IN DATABASE:")
for row in query("""
    SELECT academic_year, COUNT(*) AS total
    FROM timetable
    GROUP BY academic_year
    ORDER BY academic_year
"""):
    print(row)

print("\nFIRST-YEAR LAB SUBJECTS:")
for row in query("""
    SELECT academic_year, department, section,
           day, period, subject
    FROM timetable
    WHERE academic_year LIKE '%IST%'
       OR academic_year LIKE '%1ST%'
       OR academic_year LIKE '%YEAR%'
    ORDER BY academic_year, department, section, day, period
    LIMIT 30
"""):
    print(row)

print("\nLAB ROW COUNTS BY YEAR:")
for row in query("""
    SELECT academic_year, COUNT(*) AS total
    FROM timetable
    WHERE resource_type = 'LAB'
    GROUP BY academic_year
    ORDER BY academic_year
"""):
    print(row)