"""
Pytest configuration and fixtures for testing
"""
import pytest
import uuid
import psycopg
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import Database
from app.core.config import settings


@pytest.fixture(scope="session", autouse=True)
def reset_test_database():
    """
    Reset the database before running tests.
    Runs once per test session to ensure clean state with correct authorization levels.
    """
    print("\nResetting test database...")
    try:
        conn = psycopg.connect(settings.DATABASE_URL)
        cursor = conn.cursor()

        # Reset schema
        with open('sql/schema.sql', 'r') as f:
            cursor.execute(f.read())

        # Insert seed data
        with open('sql/seed_data.sql', 'r') as f:
            cursor.execute(f.read())

        conn.commit()
        cursor.close()
        conn.close()
        print("Test database reset successfully!")

    except Exception as e:
        print(f"Failed to reset test database: {e}")
        raise

    yield

    # Cleanup after all tests complete
    print("\nCleaning up test database...")
    try:
        conn = psycopg.connect(settings.DATABASE_URL)
        cursor = conn.cursor()

        # Reset to clean state after all tests
        with open('sql/schema.sql', 'r') as f:
            cursor.execute(f.read())

        with open('sql/seed_data.sql', 'r') as f:
            cursor.execute(f.read())

        conn.commit()
        cursor.close()
        conn.close()
        print("Test database cleaned up successfully!")

    except Exception as e:
        print(f"Cleanup warning: {e}")


@pytest.fixture(scope="function", autouse=True)
def cleanup_test_artifacts():
    """
    Automatically cleanup test artifacts after each test.
    Removes any data created during tests that's not in seed data.
    """
    yield

    # Cleanup after each test
    try:
        conn = psycopg.connect(settings.DATABASE_URL)
        cursor = conn.cursor()

        # Delete test-created data (anything with IDs higher than seed data)
        # Seed data IDs: users 1-4, events 1-4, venues 1-3, event_types 1-5

        # Delete test events (ID > 4, will cascade to ticket_types, tickets, mappings)
        cursor.execute("DELETE FROM events WHERE event_id > 4")

        # Delete test venues (ID > 3, will cascade to sections, seats, tickets)
        cursor.execute("DELETE FROM venues WHERE venue_id > 3")

        # Delete test users (ID > 4, but keep their user type)
        cursor.execute("DELETE FROM users WHERE user_id > 4")

        # Delete test event types (ID > 5)
        cursor.execute("DELETE FROM event_type WHERE event_type_id > 5")

        # Delete orphaned transactions (shouldn't happen with CASCADE, but just in case)
        cursor.execute("DELETE FROM transactions WHERE transaction_id > 1")

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        # Don't fail the test if cleanup fails
        print(f"Cleanup warning: {e}")


@pytest.fixture(scope="function")
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(scope="function")
def test_user_data():
    """Sample user data for testing - unique for each test"""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "name": f"Test User {unique_id}",
        "mail_address": f"testuser{unique_id}@example.com",
        "phone_number": f"555-{unique_id[:4]}",
        "password": "testpassword123",
        "type_id": 4
    }


@pytest.fixture(scope="function")
def admin_user_data():
    """Admin user data for testing - unique for each test"""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "name": f"Admin User {unique_id}",
        "mail_address": f"admin{unique_id}@test.com",
        "phone_number": f"555-{unique_id[:4]}",
        "password": "adminpass123",
        "type_id": 1
    }


@pytest.fixture(scope="function")
def organizer_user_data():
    """Organizer user data for testing - unique for each test"""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "name": f"Organizer User {unique_id}",
        "mail_address": f"organizer{unique_id}@test.com",
        "phone_number": f"555-{unique_id[:4]}",
        "password": "orgpass123",
        "type_id": 2
    }


@pytest.fixture(scope="function")
def venue_owner_user_data():
    """Venue Owner user data for testing - unique for each test"""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "name": f"Venue Owner {unique_id}",
        "mail_address": f"venueowner{unique_id}@test.com",
        "phone_number": f"555-{unique_id[:4]}",
        "password": "venuepass123",
        "type_id": 3
    }


@pytest.fixture(scope="function")
def registered_user(client, test_user_data):
    """Register a user and return user data with token"""
    # Register
    response = client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 201

    # Login
    login_response = client.post("/api/auth/login", json={
        "mail_address": test_user_data["mail_address"],
        "password": test_user_data["password"]
    })
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    user = response.json()

    return {
        "user": user,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }


@pytest.fixture(scope="function")
def registered_admin(client, admin_user_data):
    """Register an admin user and return data with token"""
    # Register
    response = client.post("/api/auth/register", json=admin_user_data)
    assert response.status_code == 201

    # Login
    login_response = client.post("/api/auth/login", json={
        "mail_address": admin_user_data["mail_address"],
        "password": admin_user_data["password"]
    })
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    user = response.json()

    return {
        "user": user,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }


@pytest.fixture(scope="function")
def registered_organizer(client, organizer_user_data):
    """Register an organizer and return data with token"""
    # Register
    response = client.post("/api/auth/register", json=organizer_user_data)
    assert response.status_code == 201

    # Login
    login_response = client.post("/api/auth/login", json={
        "mail_address": organizer_user_data["mail_address"],
        "password": organizer_user_data["password"]
    })
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    user = response.json()

    return {
        "user": user,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }


@pytest.fixture(scope="function")
def registered_venue_owner(client, venue_owner_user_data):
    """Register a venue owner and return data with token"""
    # Register
    response = client.post("/api/auth/register", json=venue_owner_user_data)
    assert response.status_code == 201

    # Login
    login_response = client.post("/api/auth/login", json={
        "mail_address": venue_owner_user_data["mail_address"],
        "password": venue_owner_user_data["password"]
    })
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    user = response.json()

    return {
        "user": user,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }


@pytest.fixture(scope="function")
def cleanup_test_users():
    """Cleanup test users after tests"""
    yield
    # Cleanup logic can be added here if needed
    # For now, each test run starts fresh with the seeded database
