"""
Tests for transaction endpoints
"""
import pytest


class TestTransactions:
    """Test transaction endpoints"""

    def test_get_my_transactions(self, client, registered_user):
        """Test getting current user's transactions"""
        response = client.get(
            "/api/transactions",
            headers=registered_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_my_transactions_unauthorized(self, client):
        """Test getting transactions without authentication"""
        response = client.get("/api/transactions")
        assert response.status_code == 401

    def test_get_all_transactions_as_admin(self, client, registered_admin):
        """Test getting all transactions as admin"""
        response = client.get(
            "/api/transactions/all",
            headers=registered_admin["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_all_transactions_unauthorized(self, client, registered_user):
        """Test getting all transactions as regular user (should fail)"""
        response = client.get(
            "/api/transactions/all",
            headers=registered_user["headers"]
        )
        assert response.status_code == 403

    def test_create_transaction_success(self, client, registered_user):
        """Test creating a transaction (purchasing tickets)"""
        # Get available tickets
        tickets_response = client.get("/api/tickets?status_filter=available&limit=2")
        tickets = tickets_response.json()

        if len(tickets) > 0:
            ticket_ids = [tickets[0]["ticket_id"]]

            transaction_data = {
                "ticket_ids": ticket_ids,
                "price": 500.0,
                "payment_method": "Credit Card",
                "installment_period": 1
            }

            response = client.post(
                "/api/transactions",
                json=transaction_data,
                headers=registered_user["headers"]
            )
            assert response.status_code == 201
            data = response.json()
            assert data["price"] == transaction_data["price"]
            assert data["payment_method"] == transaction_data["payment_method"]
            assert "receipt_id" in data

    def test_create_transaction_unauthorized(self, client):
        """Test creating transaction without authentication"""
        transaction_data = {
            "ticket_ids": [1],
            "price": 500.0,
            "payment_method": "Credit Card"
        }
        response = client.post("/api/transactions", json=transaction_data)
        assert response.status_code == 401

    def test_transactions_pagination(self, client, registered_user):
        """Test transaction pagination"""
        response = client.get(
            "/api/transactions?skip=0&limit=5",
            headers=registered_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
