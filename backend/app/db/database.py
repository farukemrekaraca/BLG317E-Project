import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager
from app.core.config import settings


class Database:
    """Database connection manager using raw SQL queries (no ORM)"""

    @staticmethod
    def get_connection():
        """Get a database connection"""
        return psycopg.connect(
            settings.DATABASE_URL,
            row_factory=dict_row
        )

    @staticmethod
    @contextmanager
    def get_cursor():
        """Context manager for database operations"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()


def get_db():
    """Dependency for getting database cursor"""
    with Database.get_cursor() as cursor:
        yield cursor
