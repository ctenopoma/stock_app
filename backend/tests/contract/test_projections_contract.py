"""
API contract tests for Projection endpoint (/projections)

Tests verify:
- POST /projections creates projections with calculation results
- GET /projections lists user's projections
- GET /projections/{id} retrieves a specific projection
- Authentication is required
"""

import json
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from portfolio.models import InvestmentHolding, Projection


@pytest.fixture
def api_client():
    """Provide an API client"""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Create a test user"""
    return User.objects.create_user(
        username="testuser", password="testpass123", email="test@example.com"
    )


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Provide an authenticated API client"""
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.mark.django_db
class TestProjectionContractAPI:
    """Contract tests for /projections endpoint"""

    def test_post_projections_creates_projection_with_calculation(
        self, authenticated_client, test_user
    ):
        """POST /projections with valid data creates projection"""
        # Create a holding first
        InvestmentHolding.objects.create(
            user=test_user,
            account_type="NISA",
            asset_class="MUTUAL_FUND",
            asset_region="DOMESTIC_STOCKS",
            asset_identifier="TEST001",
            asset_name="Test Fund",
            current_amount_jpy=Decimal("1000000.00"),
        )

        response = authenticated_client.post(
            "/api/v1/projections/",
            {
                "projection_years": 5,
                "annual_return_rate": 4.0,
            },
            format="json",
        )

        assert response.status_code == 201
        data = response.json()
        assert data["projection_years"] == 5
        assert data["annual_return_rate"] == "4.00"
        assert data["starting_balance_jpy"] == "1000000.00"
        assert float(data["projected_total_value_jpy"]) > 1000000.00
        assert "year_by_year_breakdown" in data

    def test_post_projections_without_authentication_returns_401(self, api_client):
        """POST /projections without auth returns 401 or 403"""
        response = api_client.post(
            "/api/v1/projections/",
            {
                "projection_years": 5,
                "annual_return_rate": 4.0,
            },
            format="json",
        )

        # Django APPEND_SLASH may return 403, accept both 401 and 403 for unauthenticated
        assert response.status_code in [401, 403]

    def test_post_projections_missing_projection_years_returns_400(
        self, authenticated_client
    ):
        """POST /projections without projection_years returns 400"""
        response = authenticated_client.post(
            "/api/v1/projections/",
            {
                "annual_return_rate": 4.0,
            },
            format="json",
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data or "projection_years" in data

    def test_post_projections_missing_annual_return_rate_returns_400(
        self, authenticated_client
    ):
        """POST /projections without annual_return_rate returns 400"""
        response = authenticated_client.post(
            "/api/v1/projections/",
            {
                "projection_years": 5,
            },
            format="json",
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data or "annual_return_rate" in data

    def test_post_projections_with_invalid_projection_years_returns_400(
        self, authenticated_client
    ):
        """POST /projections with invalid projection_years returns 400"""
        response = authenticated_client.post(
            "/api/v1/projections/",
            {
                "projection_years": 0,
                "annual_return_rate": 4.0,
            },
            format="json",
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_post_projections_with_invalid_return_rate_returns_400(
        self, authenticated_client
    ):
        """POST /projections with invalid return_rate returns 400"""
        response = authenticated_client.post(
            "/api/v1/projections/",
            {
                "projection_years": 5,
                "annual_return_rate": 101.0,
            },
            format="json",
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_get_projections_lists_user_projections(
        self, authenticated_client, test_user
    ):
        """GET /projections returns list of user's projections"""
        # Create some projections manually
        Projection.objects.create(
            user=test_user,
            projection_years=5,
            annual_return_rate=Decimal("4.0"),
            starting_balance_jpy=Decimal("1000000.00"),
            total_accumulated_contributions_jpy=Decimal("0.00"),
            total_interest_gains_jpy=Decimal("100000.00"),
            projected_total_value_jpy=Decimal("1100000.00"),
            projected_composition_by_region='{"DOMESTIC_STOCKS": {"amount": 1100000.0, "percentage": 100.0}}',
            year_by_year_breakdown='[{"year": 1, "starting_balance": 1000000.0, "contributions": 0.0, "growth": 40000.0, "ending_balance": 1040000.0}]',
        )

        response = authenticated_client.get("/api/v1/projections/")

        assert response.status_code == 200
        data = response.json()
        # data can be a dict (paginated) or list
        results = data.get("results", data) if isinstance(data, dict) else data
        assert len(results) >= 1

    def test_get_projections_without_authentication_returns_401(self, api_client):
        """GET /projections without auth returns 401 or 403"""
        response = api_client.get(
            "/api/v1/projections/",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        # Django APPEND_SLASH may return 403, accept both 401 and 403 for unauthenticated
        assert response.status_code in [401, 403]

    def test_get_projection_detail(self, authenticated_client, test_user):
        """GET /projections/{id} retrieves specific projection"""
        projection = Projection.objects.create(
            user=test_user,
            projection_years=5,
            annual_return_rate=Decimal("4.0"),
            starting_balance_jpy=Decimal("1000000.00"),
            total_accumulated_contributions_jpy=Decimal("0.00"),
            total_interest_gains_jpy=Decimal("100000.00"),
            projected_total_value_jpy=Decimal("1100000.00"),
            projected_composition_by_region='{"DOMESTIC_STOCKS": {"amount": 1100000.0, "percentage": 100.0}}',
            year_by_year_breakdown='[{"year": 1}]',
        )

        response = authenticated_client.get(f"/api/v1/projections/{projection.id}/")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == projection.id
        assert data["projection_years"] == 5

    def test_get_projection_detail_returns_404_for_missing_projection(
        self, authenticated_client
    ):
        """GET /projections/{id} returns 404 for missing projection"""
        response = authenticated_client.get("/api/v1/projections/99999/")
        assert response.status_code == 404

    def test_get_projection_detail_of_other_user_returns_404(
        self, api_client, test_user, db
    ):
        """GET /projections/{id} returns 404 if projection belongs to other user"""
        other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )

        projection = Projection.objects.create(
            user=test_user,
            projection_years=5,
            annual_return_rate=Decimal("4.0"),
            starting_balance_jpy=Decimal("1000000.00"),
            total_accumulated_contributions_jpy=Decimal("0.00"),
            total_interest_gains_jpy=Decimal("100000.00"),
            projected_total_value_jpy=Decimal("1100000.00"),
            projected_composition_by_region='{"DOMESTIC_STOCKS": {"amount": 1100000.0, "percentage": 100.0}}',
            year_by_year_breakdown='[{"year": 1}]',
        )

        api_client.force_authenticate(user=other_user)
        response = api_client.get(f"/api/v1/projections/{projection.id}/")
        assert response.status_code == 404

    def test_get_projection_detail_without_authentication_returns_401(self, api_client):
        """GET /projections/{id} without auth returns 401 or 403"""
        response = api_client.get(
            "/api/v1/projections/1/",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        # Django APPEND_SLASH may return 403, accept both 401 and 403 for unauthenticated
        assert response.status_code in [401, 403]

    def test_post_projections_with_year_by_year_breakdown(
        self, authenticated_client, test_user
    ):
        """POST /projections returns complete year-by-year breakdown"""
        InvestmentHolding.objects.create(
            user=test_user,
            account_type="NISA",
            asset_class="MUTUAL_FUND",
            asset_region="DOMESTIC_STOCKS",
            asset_identifier="TEST001",
            asset_name="Test Fund",
            current_amount_jpy=Decimal("1000000.00"),
        )

        response = authenticated_client.post(
            "/api/v1/projections/",
            {
                "projection_years": 2,
                "annual_return_rate": 4.0,
            },
            format="json",
        )

        assert response.status_code == 201
        data = response.json()
        breakdown = json.loads(data["year_by_year_breakdown"])

        assert len(breakdown) == 2
        assert breakdown[0]["year"] == 1
        assert breakdown[1]["year"] == 2
        assert "starting_balance" in breakdown[0]
        assert "contributions" in breakdown[0]
        assert "growth_rate" in breakdown[0]
        assert "ending_balance" in breakdown[0]

    def test_post_projections_composition_by_region(
        self, authenticated_client, test_user
    ):
        """POST /projections returns correct composition by region"""
        InvestmentHolding.objects.create(
            user=test_user,
            account_type="NISA",
            asset_class="MUTUAL_FUND",
            asset_region="DOMESTIC_STOCKS",
            asset_identifier="DOM",
            asset_name="Domestic",
            current_amount_jpy=Decimal("600000.00"),
        )
        InvestmentHolding.objects.create(
            user=test_user,
            account_type="GENERAL",
            asset_class="MUTUAL_FUND",
            asset_region="INTERNATIONAL_STOCKS",
            asset_identifier="INTL",
            asset_name="International",
            current_amount_jpy=Decimal("400000.00"),
        )

        response = authenticated_client.post(
            "/api/v1/projections/",
            {
                "projection_years": 1,
                "annual_return_rate": 4.0,
            },
            format="json",
        )

        assert response.status_code == 201
        data = response.json()
        composition = json.loads(data["projected_composition_by_region"])

        assert "DOMESTIC_STOCKS" in composition
        assert "INTERNATIONAL_STOCKS" in composition
        # Check proportions maintained
        assert abs(composition["DOMESTIC_STOCKS"]["percentage"] - 60.0) < 1.0
        assert abs(composition["INTERNATIONAL_STOCKS"]["percentage"] - 40.0) < 1.0
