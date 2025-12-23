"""
Tests for user endpoints
"""
import pytest


class TestUserEndpoints:
    """Test user-related endpoints"""

    def test_get_current_user(self, client, registered_user):
        """Test getting current user info"""
        response = client.get(
            "/api/users/me",
            headers=registered_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == registered_user["user"]["user_id"]
        assert data["mail_address"] == registered_user["user"]["mail_address"]

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/users/me")
        assert response.status_code == 401

    def test_get_all_users_as_admin(self, client, registered_admin):
        """Test getting all users as admin"""
        response = client.get(
            "/api/users",
            headers=registered_admin["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_all_users_as_regular_user(self, client, registered_user):
        """Test getting all users as regular user (should fail)"""
        response = client.get(
            "/api/users",
            headers=registered_user["headers"]
        )
        assert response.status_code == 403

    def test_get_user_by_id_as_admin(self, client, registered_admin, registered_user):
        """Test getting specific user by ID as admin"""
        user_id = registered_user["user"]["user_id"]
        response = client.get(
            f"/api/users/{user_id}",
            headers=registered_admin["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id

    def test_get_my_tickets(self, client, registered_user):
        """Test getting current user's tickets"""
        response = client.get(
            "/api/users/me/tickets",
            headers=registered_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_delete_user_as_admin(self, client, registered_admin):
        """Test deleting a user as admin"""
        # First create a user to delete
        new_user = {
            "name": "User To Delete",
            "mail_address": "todelete@example.com",
            "password": "password123",
            "type_id": 4
        }
        create_response = client.post("/api/auth/register", json=new_user)
        assert create_response.status_code == 201
        user_id = create_response.json()["user_id"]

        # Delete the user
        response = client.delete(
            f"/api/users/{user_id}",
            headers=registered_admin["headers"]
        )
        assert response.status_code == 204

        # Verify user is deleted
        get_response = client.get(
            f"/api/users/{user_id}",
            headers=registered_admin["headers"]
        )
        assert get_response.status_code == 404
