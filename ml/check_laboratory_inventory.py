
from backend.database import query

print("\n=== PHYSICAL LABORATORY INVENTORY ===")

rows = query("SELECT * FROM laboratories")

print("Total records:", len(rows))

for row in rows:
    print(dict(row))

print("\n=== VENUE MAPPING COUNTS ===")

rows = query("""
    SELECT venue_type, mapping_status, COUNT(*) AS total
    FROM venue_mappings
    GROUP BY venue_type, mapping_status
    ORDER BY venue_type, mapping_status
""")

for row in rows:
    print(dict(row))

print("\n=== LABORATORIES TABLE SCHEMA ===")

rows = query("PRAGMA table_info(laboratories)")

for row in rows:
    print(dict(row))

print("\n=== DISTINCT LABORATORY VENUE NAMES ===")

rows = query("""
    SELECT
        TRIM(lab_venue) AS lab_venue,
        COUNT(*) AS mapping_count
    FROM venue_mappings
    WHERE UPPER(TRIM(venue_type)) = 'LABORATORY'
      AND TRIM(COALESCE(lab_venue, '')) <> ''
    GROUP BY TRIM(lab_venue)
    ORDER BY TRIM(lab_venue)
""")

for row in rows:
    print(dict(row))

print("\nUnique laboratory venue names:", len(rows))
