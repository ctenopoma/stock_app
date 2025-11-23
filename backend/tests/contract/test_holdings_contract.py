"""
Contract tests for Holdings endpoints
Tests verify that POST /holdings and GET /holdings match the OpenAPI specification
in specs/1-portfolio-analysis/contracts/api.openapi.json
"""

import json

import pytest
from django.contrib.auth.models import User
from django.test import Client


@pytest.fixture
def api_client():
    """Fixture providing a test client"""
    return Client()


@pytest.fixture
def test_user(db):
    """Fixture creating a test user"""
    user = User.objects.create_user(
        username="testuser", password="testpass123", email="testuser@example.com"
    )
    return user


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Fixture providing an authenticated client (logged in)"""
    api_client.login(username="testuser", password="testpass123")
    return api_client


class TestHoldingsContractPostCreate:
    """Contract tests for POST /holdings (create holding)"""

    API_ENDPOINT = "/api/v1/holdings"

    def test_post_holdings_creates_holding_with_valid_input(self, authenticated_client):
        """
        POST /holdings with valid InvestmentHoldingInput should return 201 with InvestmentHolding

        OpenAPI spec:
        - Request: InvestmentHoldingInput (required fields: account_type, asset_class, asset_region,
                                            asset_identifier, asset_name, current_amount_jpy)
        - Response 201: InvestmentHolding with id, user, timestamps
        """
        payload = {
            "account_type": "NISA",
            "asset_class": "MUTUAL_FUND",
            "asset_region": "DOMESTIC_STOCKS",
            "asset_identifier": "JP0123456789",
            "asset_name": "Example Fund",
            "current_amount_jpy": 100000.50,
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        # Verify response status and structure
        assert (
            response.status_code == 201
        ), f"Expected 201, got {response.status_code}: {response.content}"

        data = response.json()
        # Verify InvestmentHolding schema
        assert "id" in data
        assert "user" in data
        assert data["account_type"] == "NISA"
        assert data["asset_class"] == "MUTUAL_FUND"
        assert data["asset_region"] == "DOMESTIC_STOCKS"
        assert data["asset_identifier"] == "JP0123456789"
        assert data["asset_name"] == "Example Fund"
        assert data["current_amount_jpy"] == 100000.50
        assert "created_at" in data
        assert "updated_at" in data

    def test_post_holdings_with_optional_purchase_date(self, authenticated_client):
        """POST /holdings with optional purchase_date"""
        payload = {
            "account_type": "GENERAL",
            "asset_class": "INDIVIDUAL_STOCK",
            "asset_region": "INTERNATIONAL_STOCKS",
            "asset_identifier": "US0987654321",
            "asset_name": "US Stock",
            "current_amount_jpy": 50000,
            "purchase_date": "2025-01-15",
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 201
        data = response.json()
        assert data["purchase_date"] == "2025-01-15"

    def test_post_holdings_missing_required_field_returns_400(
        self, authenticated_client
    ):
        """POST /holdings missing required field should return 400"""
        payload = {
            "account_type": "NISA",
            "asset_class": "MUTUAL_FUND",
            # Missing: asset_region, asset_identifier, asset_name, current_amount_jpy
            "asset_name": "Incomplete Fund",
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 400

    def test_post_holdings_unauthenticated_returns_401(self, api_client):
        """POST /holdings without authentication should return 401"""
        payload = {
            "account_type": "NISA",
            "asset_class": "MUTUAL_FUND",
            "asset_region": "DOMESTIC_STOCKS",
            "asset_identifier": "JP0123456789",
            "asset_name": "Example Fund",
            "current_amount_jpy": 100000,
        }

        response = api_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 401

    def test_post_holdings_invalid_account_type_returns_400(self, authenticated_client):
        """POST /holdings with invalid account_type should return 400"""
        payload = {
            "account_type": "INVALID_TYPE",  # Should be NISA or GENERAL
            "asset_class": "MUTUAL_FUND",
            "asset_region": "DOMESTIC_STOCKS",
            "asset_identifier": "JP0123456789",
            "asset_name": "Example Fund",
            "current_amount_jpy": 100000,
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 400

    def test_post_holdings_negative_amount_returns_400(self, authenticated_client):
        """POST /holdings with negative current_amount_jpy should return 400"""
        payload = {
            "account_type": "NISA",
            "asset_class": "MUTUAL_FUND",
            "asset_region": "DOMESTIC_STOCKS",
            "asset_identifier": "JP0123456789",
            "asset_name": "Example Fund",
            "current_amount_jpy": -100000,  # Invalid: must be >= 0
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 400


class TestHoldingsContractGetList:
    """Contract tests for GET /holdings (list holdings)"""

    API_ENDPOINT = "/api/v1/holdings"

    def test_get_holdings_returns_paginated_list(self, authenticated_client):
        """
        GET /holdings should return paginated list matching OpenAPI spec

        OpenAPI spec response:
        {
            "count": integer,
            "next": string | null,
            "previous": string | null,
            "results": array of InvestmentHolding
        }
        """
        # Create a test holding first
        payload = {
            "account_type": "NISA",
            "asset_class": "MUTUAL_FUND",
            "asset_region": "DOMESTIC_STOCKS",
            "asset_identifier": "JP0123456789",
            "asset_name": "Example Fund",
            "current_amount_jpy": 100000,
        }
        authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        response = authenticated_client.get(self.API_ENDPOINT)

        assert response.status_code == 200
        data = response.json()

        # Verify pagination schema
        assert "count" in data
        assert "next" in data
        assert "previous" in data
        assert "results" in data
        assert isinstance(data["results"], list)
        assert data["count"] >= 1

        # Verify holding in results
        if data["results"]:
            holding = data["results"][0]
            assert "id" in holding
            assert "user" in holding
            assert "account_type" in holding
            assert "asset_class" in holding

    def test_get_holdings_with_pagination_params(self, authenticated_client):
        """GET /holdings with page and page_size parameters"""
        response = authenticated_client.get(f"{self.API_ENDPOINT}?page=1&page_size=10")

        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "results" in data

    def test_get_holdings_unauthenticated_returns_401(self, api_client):
        """GET /holdings without authentication should return 401"""
        response = api_client.get(self.API_ENDPOINT)
        assert response.status_code == 401

    def test_get_holdings_returns_user_specific_holdings(self, api_client, db):
        """GET /holdings should only return holdings for authenticated user"""
        # Create two users
        user1 = User.objects.create_user(username="user1", password="pass123")
        user2 = User.objects.create_user(username="user2", password="pass123")

        # Create holding for user1
        from portfolio.models import InvestmentHolding

        InvestmentHolding.objects.create(
            user=user1,
            account_type="NISA",
            asset_class="MUTUAL_FUND",
            asset_region="DOMESTIC_STOCKS",
            asset_identifier="JP0123456789",
            asset_name="Fund 1",
            current_amount_jpy=100000,
        )

        # Create holding for user2
        InvestmentHolding.objects.create(
            user=user2,
            account_type="NISA",
            asset_class="INDIVIDUAL_STOCK",
            asset_region="INTERNATIONAL_STOCKS",
            asset_identifier="US0987654321",
            asset_name="Stock 1",
            current_amount_jpy=50000,
        )

        # Login as user1 and fetch holdings
        api_client.login(username="user1", password="pass123")
        response = api_client.get(self.API_ENDPOINT)

        assert response.status_code == 200
        data = response.json()

        # Should only see user1's holding
        assert data["count"] == 1
        assert data["results"][0]["asset_name"] == "Fund 1"


class TestHoldingsContractGetDetail:
    """Contract tests for GET /holdings/{id} (get single holding)"""

    def test_get_holding_by_id_returns_holding(self, authenticated_client):
        """GET /holdings/{id} should return InvestmentHolding"""
        # Create a holding
        payload = {
            "account_type": "NISA",
            "asset_class": "MUTUAL_FUND",
            "asset_region": "DOMESTIC_STOCKS",
            "asset_identifier": "JP0123456789",
            "asset_name": "Example Fund",
            "current_amount_jpy": 100000,
        }
        create_response = authenticated_client.post(
            "/api/v1/holdings",
            data=json.dumps(payload),
            content_type="application/json",
        )
        holding_id = create_response.json()["id"]

        # Get the holding
        response = authenticated_client.get(f"/api/v1/holdings/{holding_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == holding_id
        assert data["asset_name"] == "Example Fund"

    def test_get_holding_nonexistent_returns_404(self, authenticated_client):
        """GET /holdings/{id} with nonexistent id should return 404"""
        response = authenticated_client.get("/api/v1/holdings/99999")
        assert response.status_code == 404

    def test_get_holding_unauthenticated_returns_401(self, api_client):
        """GET /holdings/{id} without authentication should return 401"""
        response = api_client.get("/api/v1/holdings/1")
        assert response.status_code == 401
