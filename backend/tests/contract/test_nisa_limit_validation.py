"""
Contract tests for NISA limit validation
Tests verify that NISA annual limits are enforced and continue_if_limit_exceeded flag works
"""

import json

import pytest
from django.contrib.auth.models import User
from django.test import Client

from portfolio.models import RecurringInvestmentPlan


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


class TestNISALimitValidation:
    """Test NISA annual limit validation for recurring investment plans"""

    API_ENDPOINT = "/api/v1/recurring-plans/"

    @pytest.mark.django_db
    def test_nisa_tsumitate_exceeding_annual_limit_without_continue_flag_returns_400(
        self, authenticated_client
    ):
        """
        POST /recurring-plans with NISA_TSUMITATE exceeding annual limit (120万円)
        should return 400 when continue_if_limit_exceeded is False (default)
        """
        payload = {
            "target_account_type": "NISA_TSUMITATE",
            "target_asset_class": "MUTUAL_FUND",
            "target_asset_region": "DOMESTIC_STOCKS",
            "frequency": "MONTHLY",
            "amount_jpy": 150000,  # 150,000 * 12 = 1,800,000 > 1,200,000 limit
            "start_date": "2025-01-01",
            "continue_if_limit_exceeded": False,
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 400
        data = response.json()
        # Verify error message mentions annual limit
        assert "年間上限" in str(data) or "1,200,000" in str(data)

    @pytest.mark.django_db
    def test_nisa_growth_exceeding_annual_limit_without_continue_flag_returns_400(
        self, authenticated_client
    ):
        """
        POST /recurring-plans with NISA_GROWTH exceeding annual limit (240万円)
        should return 400 when continue_if_limit_exceeded is False (default)
        """
        payload = {
            "target_account_type": "NISA_GROWTH",
            "target_asset_class": "INDIVIDUAL_STOCK",
            "target_asset_region": "DOMESTIC_STOCKS",
            "frequency": "MONTHLY",
            "amount_jpy": 250000,  # 250,000 * 12 = 3,000,000 > 2,400,000 limit
            "start_date": "2025-01-01",
            "continue_if_limit_exceeded": False,
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 400
        data = response.json()
        # Verify error message mentions annual limit
        assert "年間上限" in str(data) or "2,400,000" in str(data)

    @pytest.mark.django_db
    def test_nisa_total_exceeding_annual_limit_without_continue_flag_returns_400(
        self, authenticated_client
    ):
        """
        POST /recurring-plans with NISA exceeding total annual limit (360万円)
        should return 400 when continue_if_limit_exceeded is False (default)
        """
        payload = {
            "target_account_type": "NISA_TSUMITATE",
            "target_asset_class": "MUTUAL_FUND",
            "target_asset_region": "DOMESTIC_STOCKS",
            "frequency": "MONTHLY",
            "amount_jpy": 400000,  # 400,000 * 12 = 4,800,000 > 3,600,000 total limit
            "start_date": "2025-01-01",
            "continue_if_limit_exceeded": False,
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 400
        data = response.json()
        # Verify error message mentions annual limit
        assert "年間" in str(data) or "3,600,000" in str(data)

    @pytest.mark.django_db
    def test_nisa_tsumitate_exceeding_limit_with_continue_flag_succeeds(
        self, authenticated_client
    ):
        """
        POST /recurring-plans with NISA_TSUMITATE exceeding annual limit
        should succeed (201) when continue_if_limit_exceeded is True
        """
        payload = {
            "target_account_type": "NISA_TSUMITATE",
            "target_asset_class": "MUTUAL_FUND",
            "target_asset_region": "DOMESTIC_STOCKS",
            "frequency": "MONTHLY",
            "amount_jpy": 150000,  # 150,000 * 12 = 1,800,000 > 1,200,000 limit
            "start_date": "2025-01-01",
            "continue_if_limit_exceeded": True,  # Allow exceeding limit
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 201
        data = response.json()
        assert data["continue_if_limit_exceeded"] is True
        assert data["target_account_type"] == "NISA_TSUMITATE"

    @pytest.mark.django_db
    def test_nisa_growth_exceeding_limit_with_continue_flag_succeeds(
        self, authenticated_client
    ):
        """
        POST /recurring-plans with NISA_GROWTH exceeding annual limit
        should succeed (201) when continue_if_limit_exceeded is True
        """
        payload = {
            "target_account_type": "NISA_GROWTH",
            "target_asset_class": "INDIVIDUAL_STOCK",
            "target_asset_region": "INTERNATIONAL_STOCKS",
            "frequency": "MONTHLY",
            "amount_jpy": 250000,  # 250,000 * 12 = 3,000,000 > 2,400,000 limit
            "start_date": "2025-01-01",
            "continue_if_limit_exceeded": True,  # Allow exceeding limit
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 201
        data = response.json()
        assert data["continue_if_limit_exceeded"] is True
        assert data["target_account_type"] == "NISA_GROWTH"

    @pytest.mark.django_db
    def test_nisa_within_limit_succeeds_without_continue_flag(
        self, authenticated_client
    ):
        """
        POST /recurring-plans with NISA within annual limit
        should succeed even when continue_if_limit_exceeded is False
        """
        payload = {
            "target_account_type": "NISA_TSUMITATE",
            "target_asset_class": "MUTUAL_FUND",
            "target_asset_region": "DOMESTIC_STOCKS",
            "frequency": "MONTHLY",
            "amount_jpy": 50000,  # 50,000 * 12 = 600,000 < 1,200,000 limit
            "start_date": "2025-01-01",
            "continue_if_limit_exceeded": False,
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 201
        data = response.json()
        assert data["continue_if_limit_exceeded"] is False
        assert data["target_account_type"] == "NISA_TSUMITATE"

    @pytest.mark.django_db
    def test_nisa_daily_exceeding_limit_without_continue_flag_returns_400(
        self, authenticated_client
    ):
        """
        POST /recurring-plans with DAILY frequency exceeding annual limit
        should return 400 when continue_if_limit_exceeded is False
        """
        payload = {
            "target_account_type": "NISA_TSUMITATE",
            "target_asset_class": "MUTUAL_FUND",
            "target_asset_region": "DOMESTIC_STOCKS",
            "frequency": "DAILY",
            "amount_jpy": 5000,  # 5,000 * 365 = 1,825,000 > 1,200,000 limit
            "start_date": "2025-01-01",
            "continue_if_limit_exceeded": False,
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 400

    @pytest.mark.django_db
    def test_nisa_bonus_month_exceeding_limit_without_continue_flag_returns_400(
        self, authenticated_client
    ):
        """
        POST /recurring-plans with BONUS_MONTH frequency exceeding annual limit
        should return 400 when continue_if_limit_exceeded is False
        """
        payload = {
            "target_account_type": "NISA_TSUMITATE",
            "target_asset_class": "MUTUAL_FUND",
            "target_asset_region": "DOMESTIC_STOCKS",
            "frequency": "BONUS_MONTH",
            "amount_jpy": 700000,  # 700,000 * 2 = 1,400,000 > 1,200,000 limit
            "start_date": "2025-01-01",
            "bonus_months": "6,12",  # 2 times per year
            "continue_if_limit_exceeded": False,
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 400

    @pytest.mark.django_db
    def test_general_account_not_affected_by_nisa_limit_validation(
        self, authenticated_client
    ):
        """
        POST /recurring-plans with GENERAL account should not be affected by NISA limits
        """
        payload = {
            "target_account_type": "GENERAL",
            "target_asset_class": "MUTUAL_FUND",
            "target_asset_region": "DOMESTIC_STOCKS",
            "frequency": "MONTHLY",
            "amount_jpy": 500000,  # Far exceeds NISA limits, but should be OK for GENERAL
            "start_date": "2025-01-01",
            "continue_if_limit_exceeded": False,
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 201
        data = response.json()
        assert data["target_account_type"] == "GENERAL"
