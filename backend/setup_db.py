"""
Script to set up the database with schema and seed data.
Run this after creating the database in PostgreSQL.
"""

import psycopg
from app.core.config import settings

def setup_database():
    """Set up database schema and seed data"""
    try:
        # Connect to database
        conn = psycopg.connect(settings.DATABASE_URL)
        cursor = conn.cursor()

        print("Setting up database schema...")

        # Read and execute schema
        with open('sql/schema.sql', 'r') as f:
            schema_sql = f.read()
            cursor.execute(schema_sql)

        print("Schema created successfully!")

        # Read and execute seed data
        with open('sql/seed_data.sql', 'r') as f:
            seed_sql = f.read()
            cursor.execute(seed_sql)

        print("Seed data inserted successfully!")

        conn.commit()
        cursor.close()
        conn.close()

        print("\nDatabase setup completed successfully!")
        print("You can now run the API server with: uvicorn app.main:app --reload")

    except Exception as e:
        print(f"Error setting up database: {e}")
        raise

if __name__ == "__main__":
    setup_database()
