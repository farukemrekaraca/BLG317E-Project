"""
Tests for venue endpoints
"""
import pytest


class TestVenues:
    """Test venue endpoints"""

    def test_get_all_venues(self, client):
        """Test getting all venues"""
        response = client.get("/api/venues")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_venues_by_city(self, client):
        """Test filtering venues by city"""
        response = client.get("/api/venues?city=Istanbul")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert all(venue["city"] == "Istanbul" for venue in data)

    def test_get_venue_by_id(self, client):
        """Test getting specific venue"""
        all_venues = client.get("/api/venues").json()
        if len(all_venues) > 0:
            venue_id = all_venues[0]["venue_id"]
            response = client.get(f"/api/venues/{venue_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["venue_id"] == venue_id

    def test_get_nonexistent_venue(self, client):
        """Test getting non-existent venue"""
        response = client.get("/api/venues/99999")
        assert response.status_code == 404

    def test_create_venue_as_organizer(self, client, registered_organizer):
        """Test creating a venue"""
        venue_data = {
            "name": "Test Venue",
            "country": "Turkey",
            "city": "Istanbul",
            "address": "Test Address 123",
            "seat_count": 1000,
            "section_count": 5
        }
        response = client.post(
            "/api/venues",
            json=venue_data,
            headers=registered_organizer["headers"]
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == venue_data["name"]
        assert data["city"] == venue_data["city"]

    def test_create_venue_unauthorized(self, client):
        """Test creating venue without authentication"""
        venue_data = {
            "name": "Test Venue",
            "country": "Turkey",
            "city": "Istanbul",
            "address": "Test Address 123",
            "seat_count": 1000,
            "section_count": 5
        }
        response = client.post("/api/venues", json=venue_data)
        assert response.status_code == 401

    def test_venues_pagination(self, client):
        """Test venue pagination"""
        response = client.get("/api/venues?skip=0&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 3
