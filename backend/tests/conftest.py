"""
Pytest configuration and fixtures for testing
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import Database


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
def cleanup_test_users():
    """Cleanup test users after tests"""
    yield
    # Cleanup logic can be added here if needed
    # For now, each test run starts fresh with the seeded database
