"""
Tests for event endpoints
"""
import pytest
import uuid
from datetime import date, timedelta


class TestEventTypes:
    """Test event type endpoints"""

    def test_get_event_types(self, client):
        """Test getting all event types"""
        response = client.get("/api/events/types")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_create_event_type_as_organizer(self, client, registered_organizer):
        """Test creating event type as organizer"""
        unique_id = uuid.uuid4().hex[:8]
        event_type_data = {"name": f"Test Event Type {unique_id}"}
        response = client.post(
            "/api/events/types",
            json=event_type_data,
            headers=registered_organizer["headers"]
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == event_type_data["name"]
        assert "event_type_id" in data

    def test_create_event_type_unauthorized(self, client, registered_user):
        """Test creating event type as regular user (should fail)"""
        unique_id = uuid.uuid4().hex[:8]
        event_type_data = {"name": f"Test Event Type {unique_id}"}
        response = client.post(
            "/api/events/types",
            json=event_type_data,
            headers=registered_user["headers"]
        )
        assert response.status_code == 403


class TestEvents:
    """Test event endpoints"""

    def test_get_all_events(self, client):
        """Test getting all events"""
        response = client.get("/api/events")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_event_by_id(self, client):
        """Test getting specific event"""
        # First get all events to get a valid ID
        all_events = client.get("/api/events").json()
        if len(all_events) > 0:
            event_id = all_events[0]["event_id"]
            response = client.get(f"/api/events/{event_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["event_id"] == event_id

    def test_get_nonexistent_event(self, client):
        """Test getting non-existent event"""
        response = client.get("/api/events/99999")
        assert response.status_code == 404

    def test_get_events_pagination(self, client):
        """Test event pagination"""
        response = client.get("/api/events?skip=0&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
