"""
Tests for ticket endpoints
"""
import pytest


class TestTicketTypes:
    """Test ticket type endpoints"""

    def test_get_all_ticket_types(self, client):
        """Test getting all ticket types"""
        response = client.get("/api/tickets/types")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_ticket_types_by_event(self, client):
        """Test filtering ticket types by event"""
        # Get an event first
        events = client.get("/api/events").json()
        if len(events) > 0:
            event_id = events[0]["event_id"]
            response = client.get(f"/api/tickets/types?event_id={event_id}")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)


class TestTickets:
    """Test ticket endpoints"""

    def test_get_all_tickets(self, client):
        """Test getting all tickets"""
        response = client.get("/api/tickets")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_tickets_by_status(self, client):
        """Test filtering tickets by status"""
        response = client.get("/api/tickets?status_filter=available")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert all(ticket["status"] == "available" for ticket in data)

    def test_get_tickets_by_event(self, client):
        """Test filtering tickets by event"""
        events = client.get("/api/events").json()
        if len(events) > 0:
            event_id = events[0]["event_id"]
            response = client.get(f"/api/tickets?event_id={event_id}")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    def test_get_ticket_by_id(self, client):
        """Test getting specific ticket"""
        all_tickets = client.get("/api/tickets").json()
        if len(all_tickets) > 0:
            ticket_id = all_tickets[0]["ticket_id"]
            response = client.get(f"/api/tickets/{ticket_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["ticket_id"] == ticket_id

    def test_get_nonexistent_ticket(self, client):
        """Test getting non-existent ticket"""
        response = client.get("/api/tickets/99999")
        assert response.status_code == 404

    def test_tickets_pagination(self, client):
        """Test ticket pagination"""
        response = client.get("/api/tickets?skip=0&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
