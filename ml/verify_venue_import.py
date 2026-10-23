from backend.database import query

print("=== VENUE IMPORT SUMMARY ===")

for row in query("""
    SELECT mapping_status, venue_type, COUNT(*) AS total
    FROM venue_mappings
    GROUP BY mapping_status, venue_type
    ORDER BY mapping_status, venue_type
"""):
    print(row)

print("\n=== TOTAL VENUE MAPPINGS ===")
for row in query("""
    SELECT COUNT(*) AS total
    FROM venue_mappings
"""):
    print(row)

print("\n=== DUPLICATE SESSION KEYS ===")
duplicates = query("""
    SELECT academic_year, department, section, subject,
           day, time_slot, COUNT(*) AS total
    FROM venue_mappings
    GROUP BY academic_year, department, section, subject,
             day, time_slot
    HAVING COUNT(*) > 1
""")

if duplicates:
    for row in duplicates:
        print(row)
else:
    print("No duplicate session keys found.")

print("\n=== SAMPLE IMPORTED MAPPINGS ===")
for row in query("""
    SELECT academic_year, department, section, subject,
           day, start_period, end_period, lab_venue,
           venue_type, mapping_status
    FROM venue_mappings
    ORDER BY academic_year, department, section, day,
             start_period
    LIMIT 10
"""):
    print(row)