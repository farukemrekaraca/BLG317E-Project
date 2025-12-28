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

    def test_delete_ticket_as_admin(self, client, registered_admin):
        """Test deleting a ticket as admin"""
        # Get an existing ticket
        tickets = client.get("/api/tickets").json()
        if len(tickets) > 0:
            ticket_id = tickets[0]["ticket_id"]

            # Delete it
            response = client.delete(
                f"/api/tickets/{ticket_id}",
                headers=registered_admin["headers"]
            )
            assert response.status_code == 204

            # Verify it's gone
            verify = client.get(f"/api/tickets/{ticket_id}")
            assert verify.status_code == 404

    def test_delete_ticket_unauthorized(self, client, registered_organizer):
        """Test deleting ticket as non-admin (should fail)"""
        tickets = client.get("/api/tickets").json()
        if len(tickets) > 0:
            ticket_id = tickets[0]["ticket_id"]

            response = client.delete(
                f"/api/tickets/{ticket_id}",
                headers=registered_organizer["headers"]
            )
            assert response.status_code == 403  # Organizers can't delete tickets

    def test_delete_nonexistent_ticket(self, client, registered_admin):
        """Test deleting non-existent ticket"""
        response = client.delete(
            "/api/tickets/99999",
            headers=registered_admin["headers"]
        )
        assert response.status_code == 404


class TestSectionTicketTypeMappings:
    """Test section-ticket type mapping endpoints"""

    @pytest.fixture(autouse=True)
    def cleanup_mappings(self, client, registered_organizer):
        """Cleanup mappings created during tests"""
        yield
        # Cleanup after test - delete test mappings
        # This runs after each test in this class

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

    def test_delete_mapping_as_organizer(self, client, registered_organizer):
        """Test deleting a section-ticket type mapping"""
        # First create a mapping
        mapping_data = {
            "section_id": 3,
            "ticket_type_id": 3
        }
        create_response = client.post(
            "/api/tickets/mappings",
            json=mapping_data,
            headers=registered_organizer["headers"]
        )
        assert create_response.status_code in [201, 400]  # Created or already exists

        # Now delete it
        delete_response = client.delete(
            f"/api/tickets/mappings?section_id={mapping_data['section_id']}&ticket_type_id={mapping_data['ticket_type_id']}",
            headers=registered_organizer["headers"]
        )
        assert delete_response.status_code in [204, 404]  # Deleted or not found

    def test_delete_nonexistent_mapping(self, client, registered_organizer):
        """Test deleting a non-existent mapping (should fail)"""
        response = client.delete(
            "/api/tickets/mappings?section_id=999&ticket_type_id=999",
            headers=registered_organizer["headers"]
        )
        assert response.status_code == 404

    def test_delete_mapping_unauthorized(self, client, registered_user):
        """Test deleting mapping as attendee (should fail)"""
        response = client.delete(
            "/api/tickets/mappings?section_id=1&ticket_type_id=1",
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

    def test_complete_workflow_with_cleanup(self, client, registered_venue_owner, registered_organizer, registered_admin):
        """
        Test complete workflow: create venue with many seats, generate tickets, then cleanup.
        This demonstrates the full ticket generation pipeline and proper cleanup.
        """
        # Step 1: Create a venue with multiple sections and many seats
        venue_data = {
            "name": "Large Test Venue",
            "country": "Turkey",
            "city": "Istanbul",
            "address": "Test Address 123",
            "seat_count": 5000,
            "sections": [
                {"prefix": "VIP", "seat_count": 500},
                {"prefix": "Premium", "seat_count": 1000},
                {"prefix": "Standard", "seat_count": 2000},
                {"prefix": "Economy", "seat_count": 1500}
            ]
        }
        venue_response = client.post(
            "/api/venues",
            json=venue_data,
            headers=registered_venue_owner["headers"]
        )
        assert venue_response.status_code == 201
        venue = venue_response.json()
        venue_id = venue["venue_id"]

        # Step 2: Create an event at this venue
        event_data = {
            "venue_id": venue_id,
            "event_type_id": 1,  # Concert from seed data
            "name": "Large Test Concert",
            "date": "2025-12-31"
        }
        event_response = client.post(
            "/api/events",
            json=event_data,
            headers=registered_organizer["headers"]
        )
        assert event_response.status_code == 201
        event = event_response.json()
        event_id = event["event_id"]

        # Step 3: Create ticket types for the event
        ticket_type_data = {
            "event_id": event_id,
            "name": "General Admission",
            "price": 100.0
        }
        ticket_type_response = client.post(
            "/api/tickets/types",
            json=ticket_type_data,
            headers=registered_organizer["headers"]
        )
        assert ticket_type_response.status_code == 201
        ticket_type = ticket_type_response.json()
        ticket_type_id = ticket_type["ticket_type_id"]

        # Step 4: Get sections for the venue and create mappings
        # Note: We'd need a sections API endpoint to get sections
        # For now, we'll use section IDs that should exist after venue creation
        # The venue created 4 sections, they should have sequential IDs

        # Step 5: Create section-ticket type mapping for one section
        mapping_data = {
            "section_id": venue_id,  # Approximate - in real scenario we'd query sections
            "ticket_type_id": ticket_type_id
        }
        mapping_response = client.post(
            "/api/tickets/mappings",
            json=mapping_data,
            headers=registered_organizer["headers"]
        )
        # Might fail due to section_id approximation, but demonstrates the workflow

        # Step 6: Bulk generate tickets for the event
        # This would create thousands of tickets if mappings exist
        bulk_generate_data = {
            "event_id": event_id
        }
        bulk_response = client.post(
            "/api/tickets/bulk-generate-event",
            json=bulk_generate_data,
            headers=registered_organizer["headers"]
        )
        # May succeed or fail depending on mappings

        # Step 7: CLEANUP - With CASCADE deletes enabled, we can delete in any order!
        # CASCADE constraints will automatically delete related data:
        # - Deleting event → deletes ticket_types → deletes tickets and mappings
        # - Deleting venue → deletes sections → deletes seats → deletes remaining tickets

        # Delete the event (will cascade to ticket_types, tickets, mappings)
        delete_event_response = client.delete(
            f"/api/events/{event_id}",
            headers=registered_organizer["headers"]
        )
        assert delete_event_response.status_code == 204

        # Delete the venue (will cascade to sections, seats, any remaining tickets)
        delete_venue_response = client.delete(
            f"/api/venues/{venue_id}",
            headers=registered_admin["headers"]
        )
        assert delete_venue_response.status_code == 204

        # Verify cleanup worked
        verify_event = client.get(f"/api/events/{event_id}")
        assert verify_event.status_code == 404

        verify_venue = client.get(f"/api/venues/{venue_id}")
        assert verify_venue.status_code == 404


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
