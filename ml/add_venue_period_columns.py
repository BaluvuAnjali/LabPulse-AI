from backend.database import get_db


def main():
    with get_db() as db:
        columns = {
            row["name"]
            for row in db.execute(
                "PRAGMA table_info(venue_mappings)"
            ).fetchall()
        }

        if "start_period" not in columns:
            db.execute("""
                ALTER TABLE venue_mappings
                ADD COLUMN start_period INTEGER
            """)

        if "end_period" not in columns:
            db.execute("""
                ALTER TABLE venue_mappings
                ADD COLUMN end_period INTEGER
            """)

    print("Venue period columns are ready.")


if __name__ == "__main__":
    main()