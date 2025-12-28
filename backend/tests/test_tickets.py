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


class TestSectionTicketTypeMappings:
    """Test section-ticket type mapping endpoints"""

    def test_create_mapping_as_organizer(self, client, registered_organizer):
        """Test creating a section-ticket type mapping as organizer"""
        # Get a section and ticket type from seed data
        venues = client.get("/api/venues").json()
        events = client.get("/api/events").json()

        if len(venues) > 0 and len(events) > 0:
            # Get sections for the first venue
            venue_id = venues[0]["venue_id"]

            # Get ticket types for the first event
            event_id = events[0]["event_id"]
            ticket_types = client.get(f"/api/tickets/types?event_id={event_id}").json()

            if len(ticket_types) > 0:
                # Try to find unmapped combination
                mapping_data = {
                    "section_id": 1,  # From seed data
                    "ticket_type_id": ticket_types[0]["ticket_type_id"]
                }

                response = client.post(
                    "/api/tickets/mappings",
                    json=mapping_data,
                    headers=registered_organizer["headers"]
                )
                # Should succeed or already exist
                assert response.status_code in [201, 400]

    def test_get_all_mappings(self, client):
        """Test getting all section-ticket type mappings"""
        response = client.get("/api/tickets/mappings")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_mappings_by_section(self, client):
        """Test filtering mappings by section"""
        response = client.get("/api/tickets/mappings?section_id=1")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_mappings_by_ticket_type(self, client):
        """Test filtering mappings by ticket type"""
        response = client.get("/api/tickets/mappings?ticket_type_id=1")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_mapping_unauthorized(self, client, registered_user):
        """Test creating mapping as attendee (should fail)"""
        mapping_data = {
            "section_id": 1,
            "ticket_type_id": 1
        }
        response = client.post(
            "/api/tickets/mappings",
            json=mapping_data,
            headers=registered_user["headers"]
        )
        assert response.status_code == 403


class TestBulkTicketGeneration:
    """Test bulk ticket generation endpoints"""

    def test_bulk_generate_for_section(self, client, registered_organizer):
        """Test bulk generating tickets for a section-ticket type pair"""
        # First create a mapping
        mapping_data = {
            "section_id": 1,
            "ticket_type_id": 1
        }
        client.post(
            "/api/tickets/mappings",
            json=mapping_data,
            headers=registered_organizer["headers"]
        )

        # Now bulk generate
        generate_data = {
            "section_id": 1,
            "ticket_type_id": 1
        }
        response = client.post(
            "/api/tickets/bulk-generate",
            json=generate_data,
            headers=registered_organizer["headers"]
        )

        assert response.status_code == 201
        data = response.json()
        assert "tickets_created" in data
        assert "section_id" in data
        assert "ticket_type_id" in data
        assert data["section_id"] == 1
        assert data["ticket_type_id"] == 1

    def test_bulk_generate_without_mapping(self, client, registered_organizer):
        """Test bulk generate without creating mapping first (should fail)"""
        generate_data = {
            "section_id": 99,  # Non-existent or unmapped
            "ticket_type_id": 99
        }
        response = client.post(
            "/api/tickets/bulk-generate",
            json=generate_data,
            headers=registered_organizer["headers"]
        )
        assert response.status_code == 404

    def test_bulk_generate_idempotent(self, client, registered_organizer):
        """Test that bulk generate is idempotent (running twice doesn't duplicate)"""
        # First create mapping
        mapping_data = {
            "section_id": 2,
            "ticket_type_id": 2
        }
        client.post(
            "/api/tickets/mappings",
            json=mapping_data,
            headers=registered_organizer["headers"]
        )

        # First generation
        generate_data = {
            "section_id": 2,
            "ticket_type_id": 2
        }
        response1 = client.post(
            "/api/tickets/bulk-generate",
            json=generate_data,
            headers=registered_organizer["headers"]
        )
        assert response1.status_code == 201
        tickets_created_first = response1.json()["tickets_created"]

        # Second generation (should create 0 new tickets)
        response2 = client.post(
            "/api/tickets/bulk-generate",
            json=generate_data,
            headers=registered_organizer["headers"]
        )
        assert response2.status_code == 201
        assert response2.json()["tickets_created"] == 0  # No duplicates

    def test_bulk_generate_unauthorized(self, client, registered_user):
        """Test bulk generate as attendee (should fail)"""
        generate_data = {
            "section_id": 1,
            "ticket_type_id": 1
        }
        response = client.post(
            "/api/tickets/bulk-generate",
            json=generate_data,
            headers=registered_user["headers"]
        )
        assert response.status_code == 403


class TestEventBulkGeneration:
    """Test event-level bulk ticket generation"""

    def test_bulk_generate_for_event(self, client, registered_organizer):
        """Test bulk generating all tickets for an event"""
        # Get an event with ticket types
        events = client.get("/api/events").json()

        if len(events) > 0:
            event_id = events[0]["event_id"]

            # Create some mappings for this event first
            ticket_types = client.get(f"/api/tickets/types?event_id={event_id}").json()

            if len(ticket_types) > 0:
                # Create a mapping
                mapping_data = {
                    "section_id": 1,
                    "ticket_type_id": ticket_types[0]["ticket_type_id"]
                }
                client.post(
                    "/api/tickets/mappings",
                    json=mapping_data,
                    headers=registered_organizer["headers"]
                )

                # Now bulk generate for the entire event
                generate_data = {
                    "event_id": event_id
                }
                response = client.post(
                    "/api/tickets/bulk-generate-event",
                    json=generate_data,
                    headers=registered_organizer["headers"]
                )

                assert response.status_code == 201
                data = response.json()
                assert "tickets_created" in data
                assert "event_id" in data
                assert "mappings_processed" in data
                assert data["event_id"] == event_id
                assert data["mappings_processed"] >= 1

    def test_bulk_generate_event_no_mappings(self, client, registered_organizer):
        """Test bulk generate for event with no mappings (should fail)"""
        # Create a new event without mappings
        events = client.get("/api/events").json()

        if len(events) > 0:
            # Use an event ID that likely has no mappings
            generate_data = {
                "event_id": 999  # Non-existent event
            }
            response = client.post(
                "/api/tickets/bulk-generate-event",
                json=generate_data,
                headers=registered_organizer["headers"]
            )
            assert response.status_code == 404

    def test_bulk_generate_event_unauthorized(self, client, registered_user):
        """Test event bulk generate as attendee (should fail)"""
        generate_data = {
            "event_id": 1
        }
        response = client.post(
            "/api/tickets/bulk-generate-event",
            json=generate_data,
            headers=registered_user["headers"]
        )
        assert response.status_code == 403
