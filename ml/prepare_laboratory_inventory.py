
from backend.database import query

print("\n=== LABPULSE LAB INVENTORY PREVIEW ===")

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

print("Distinct venue names:", len(rows))
print()

combined_count = 0

for row in rows:
    name = row["lab_venue"]
    count = row["mapping_count"]

    is_combined = "+" in name

    if is_combined:
        combined_count += 1

    print(f"Venue: {name}")
    print(f"Timetable mappings: {count}")
    print(
        "Review required:",
        "YES — combined venue name"
        if is_combined
        else "YES — verify physical lab details",
    )
    print("Inventory action: NOT INSERTED")
    print("-" * 50)

print("\n=== SUMMARY ===")
print("Unique venue names:", len(rows))
print("Combined names requiring review:", combined_count)
print("Database changes: NONE")
