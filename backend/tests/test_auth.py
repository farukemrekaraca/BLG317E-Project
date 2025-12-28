"""
Tests for authentication endpoints
"""
import pytest


class TestRegistration:
    """Test user registration"""

    def test_register_user_success(self, client, test_user_data):
        """Test successful user registration"""
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == test_user_data["name"]
        assert data["mail_address"] == test_user_data["mail_address"]
        assert "password" not in data
        assert "user_id" in data

    def test_register_duplicate_email(self, client, registered_user, test_user_data):
        """Test registration with duplicate email"""
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        data = {
            "name": "Test User",
            "mail_address": "invalid-email",
            "password": "password123",
            "type_id": 4
        }
        response = client.post("/api/auth/register", json=data)
        assert response.status_code == 422

    def test_register_missing_required_fields(self, client):
        """Test registration with missing required fields"""
        data = {
            "name": "Test User"
        }
        response = client.post("/api/auth/register", json=data)
        assert response.status_code == 422


class TestLogin:
    """Test user login"""

    def test_login_success(self, client, test_user_data, registered_user):
        """Test successful login"""
        # Use the actual email from the registered user
        response = client.post("/api/auth/login", json={
            "mail_address": test_user_data["mail_address"],
            "password": test_user_data["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, registered_user):
        """Test login with wrong password"""
        response = client.post("/api/auth/login", json={
            "mail_address": "testuser@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email"""
        response = client.post("/api/auth/login", json={
            "mail_address": "nonexistent@example.com",
            "password": "password123"
        })
        assert response.status_code == 401

    def test_login_invalid_email_format(self, client):
        """Test login with invalid email format"""
        response = client.post("/api/auth/login", json={
            "mail_address": "invalid-email",
            "password": "password123"
        })
        assert response.status_code == 422
