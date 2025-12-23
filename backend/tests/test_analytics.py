"""
Tests for analytics (complex queries) endpoints
"""
import pytest


class TestAnalytics:
    """Test analytics endpoints"""

    def test_popular_events_by_city(self, client):
        """Test getting popular events by city"""
        response = client.get("/api/analytics/popular-events-by-city?city=Istanbul")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_popular_events_by_city_with_percentage(self, client):
        """Test getting popular events with custom percentage"""
        response = client.get("/api/analytics/popular-events-by-city?city=Istanbul&min_sold_percentage=0.5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_popular_events_missing_city(self, client):
        """Test popular events without city parameter"""
        response = client.get("/api/analytics/popular-events-by-city")
        assert response.status_code == 422

    def test_most_popular_event_types(self, client):
        """Test getting most popular event types"""
        response = client.get("/api/analytics/most-popular-event-types")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_most_popular_event_types_by_city(self, client):
        """Test getting most popular event types filtered by city"""
        response = client.get("/api/analytics/most-popular-event-types?city=Istanbul")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_user_spending_analytics(self, client, registered_user):
        """Test getting user spending analytics"""
        response = client.get(
            "/api/analytics/user-spending-analytics",
            headers=registered_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_user_spending_analytics_unauthorized(self, client):
        """Test user spending analytics without authentication"""
        response = client.get("/api/analytics/user-spending-analytics")
        assert response.status_code == 401

    def test_venue_performance(self, client):
        """Test getting venue performance metrics"""
        response = client.get("/api/analytics/venue-performance")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_upcoming_events_with_availability(self, client):
        """Test getting upcoming events with availability"""
        response = client.get("/api/analytics/upcoming-events-with-availability")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_upcoming_events_with_limit(self, client):
        """Test getting upcoming events with custom limit"""
        response = client.get("/api/analytics/upcoming-events-with-availability?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_top_spending_users_as_admin(self, client, registered_admin):
        """Test getting top spending users as admin"""
        response = client.get(
            "/api/analytics/top-spending-users",
            headers=registered_admin["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_top_spending_users_unauthorized(self, client, registered_user):
        """Test getting top spending users as regular user (should fail)"""
        response = client.get(
            "/api/analytics/top-spending-users",
            headers=registered_user["headers"]
        )
        assert response.status_code == 403

    def test_top_spending_users_with_limit(self, client, registered_admin):
        """Test getting top spending users with custom limit"""
        response = client.get(
            "/api/analytics/top-spending-users?limit=3",
            headers=registered_admin["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 3
