"""
Database Reset Script

WARNING: This script will DROP ALL TABLES and recreate them with fresh seed data.
All existing data will be LOST.

Usage:
    python reset_db.py              # Interactive mode (asks for confirmation)
    python reset_db.py --force      # Force reset without confirmation
"""

import sys
import psycopg
from app.core.config import settings


def reset_database(force=False):
    """Reset database by dropping all tables and recreating with seed data"""

    if not force:
        print("=" * 70)
        print("WARNING: DATABASE RESET")
        print("=" * 70)
        print("\nThis will:")
        print("  1. DROP all existing tables")
        print("  2. Recreate tables from schema.sql")
        print("  3. Insert seed data from seed_data.sql")
        print("\n⚠️  ALL EXISTING DATA WILL BE LOST! ⚠️\n")

        confirmation = input("Type 'RESET' to confirm: ")
        if confirmation != "RESET":
            print("\n❌ Reset cancelled.")
            return False

    try:
        print("\n🔄 Connecting to database...")
        conn = psycopg.connect(settings.DATABASE_URL)
        cursor = conn.cursor()

        print("📋 Dropping and recreating tables...")
        with open('sql/schema.sql', 'r') as f:
            schema_sql = f.read()
            cursor.execute(schema_sql)
        print("✅ Schema created successfully!")

        print("📊 Inserting seed data...")
        with open('sql/seed_data.sql', 'r') as f:
            seed_sql = f.read()
            cursor.execute(seed_sql)
        print("✅ Seed data inserted successfully!")

        conn.commit()
        cursor.close()
        conn.close()

        print("\n" + "=" * 70)
        print("✅ DATABASE RESET COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nNew authorization levels:")
        print("  • Admin: 3")
        print("  • Venue Owner: 2")
        print("  • Organizer: 1")
        print("  • Attendee: 0")
        print("\nYou can now run:")
        print("  • API server: uvicorn app.main:app --reload")
        print("  • Tests: pytest")
        print()

        return True

    except FileNotFoundError as e:
        print(f"\n❌ Error: SQL file not found - {e}")
        print("Make sure you're running this script from the backend directory.")
        return False

    except psycopg.Error as e:
        print(f"\n❌ Database error: {e}")
        return False

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    force = "--force" in sys.argv or "-f" in sys.argv

    success = reset_database(force=force)
    sys.exit(0 if success else 1)
