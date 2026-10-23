from backend.database import get_db


def create_venue_mapping_table():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS venue_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                academic_year TEXT NOT NULL,
                department TEXT NOT NULL,
                section TEXT NOT NULL DEFAULT '',
                subject TEXT NOT NULL,
                day TEXT NOT NULL DEFAULT '',
                time_slot TEXT NOT NULL DEFAULT '',
                lab_venue TEXT NOT NULL DEFAULT '',
                venue_type TEXT NOT NULL DEFAULT 'UNVERIFIED',
                mapping_status TEXT NOT NULL DEFAULT 'VERIFIED',
                source_file TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (
                    academic_year,
                    department,
                    section,
                    subject,
                    day,
                    time_slot
                )
            )
        """)

    print("Venue mapping table is ready.")


if __name__ == "__main__":
    create_venue_mapping_table()