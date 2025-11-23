"""
Integration tests for NISA usage projection in year-by-year breakdown
Tests verify that NISA frame usage is correctly calculated and included in projections
"""

import json

import pytest
from django.contrib.auth.models import User
from django.test import Client

from portfolio.models import InvestmentHolding, RecurringInvestmentPlan


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


@pytest.mark.django_db
class TestProjectionNISAUsage:
    """Test NISA usage calculation in projection year-by-year breakdown"""

    API_ENDPOINT = "/api/v1/projections/"

    def test_projection_includes_nisa_usage_in_year_breakdown(
        self, authenticated_client, test_user
    ):
        """
        POST /projections should include NISA usage information in year_by_year_breakdown
        when there are NISA investment plans
        """
        # Create a NISA investment plan
        RecurringInvestmentPlan.objects.create(
            user=test_user,
            target_account_type="NISA_TSUMITATE",
            target_asset_class="MUTUAL_FUND",
            target_asset_region="DOMESTIC_STOCKS",
            frequency="MONTHLY",
            amount_jpy=50000,  # 50,000 * 12 = 600,000 per year
            start_date="2025-01-01",
        )

        # Create projection request
        payload = {"projection_years": 3, "annual_return_rate": 4.0}

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 201
        data = response.json()

        # Verify year_by_year_breakdown exists and is parseable
        assert "year_by_year_breakdown" in data
        year_breakdown = json.loads(data["year_by_year_breakdown"])
        assert len(year_breakdown) == 3

        # Check first year NISA usage
        year_1 = year_breakdown[0]
        assert "nisa_usage" in year_1

        nisa_usage = year_1["nisa_usage"]

        # Check tsumitate frame
        assert "tsumitate" in nisa_usage
        assert nisa_usage["tsumitate"]["used"] == 600000  # 50,000 * 12
        assert nisa_usage["tsumitate"]["limit"] == 1200000
        assert nisa_usage["tsumitate"]["remaining"] == 600000

        # Check growth frame (not used)
        assert "growth" in nisa_usage
        assert nisa_usage["growth"]["used"] == 0
        assert nisa_usage["growth"]["limit"] == 2400000

        # Check total frame
        assert "total" in nisa_usage
        assert nisa_usage["total"]["used"] == 600000
        assert nisa_usage["total"]["limit"] == 3600000

        # Check lifetime usage
        assert "lifetime_tsumitate" in nisa_usage
        assert nisa_usage["lifetime_tsumitate"]["used"] == 600000

        assert "lifetime_growth" in nisa_usage
        assert nisa_usage["lifetime_growth"]["used"] == 0

        assert "lifetime_total" in nisa_usage
        assert nisa_usage["lifetime_total"]["used"] == 600000
        assert nisa_usage["lifetime_total"]["limit"] == 18000000

    def test_projection_nisa_usage_accumulates_over_years(
        self, authenticated_client, test_user
    ):
        """
        NISA lifetime usage should accumulate correctly over multiple years
        """
        # Create NISA plans for both frames
        RecurringInvestmentPlan.objects.create(
            user=test_user,
            target_account_type="NISA_TSUMITATE",
            target_asset_class="MUTUAL_FUND",
            target_asset_region="DOMESTIC_STOCKS",
            frequency="MONTHLY",
            amount_jpy=100000,  # 1,200,000 per year (max)
            start_date="2025-01-01",
        )

        RecurringInvestmentPlan.objects.create(
            user=test_user,
            target_account_type="NISA_GROWTH",
            target_asset_class="INDIVIDUAL_STOCK",
            target_asset_region="INTERNATIONAL_STOCKS",
            frequency="MONTHLY",
            amount_jpy=200000,  # 2,400,000 per year (max)
            start_date="2025-01-01",
        )

        # Create 5-year projection
        payload = {"projection_years": 5, "annual_return_rate": 5.0}

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 201
        data = response.json()

        year_breakdown = json.loads(data["year_by_year_breakdown"])

        # Check Year 1
        year_1 = year_breakdown[0]["nisa_usage"]
        assert year_1["tsumitate"]["used"] == 1200000
        assert year_1["growth"]["used"] == 2400000
        assert year_1["total"]["used"] == 3600000  # Full annual limit
        assert year_1["lifetime_total"]["used"] == 3600000

        # Check Year 3 - cumulative should be 3 * 3,600,000 = 10,800,000
        year_3 = year_breakdown[2]["nisa_usage"]
        assert year_3["lifetime_tsumitate"]["used"] == 1200000 * 3  # 3,600,000
        assert year_3["lifetime_growth"]["used"] == 2400000 * 3  # 7,200,000
        assert year_3["lifetime_total"]["used"] == 3600000 * 3  # 10,800,000
        assert (
            year_3["lifetime_total"]["remaining"] == 18000000 - 10800000
        )  # 7,200,000 left

        # Check Year 5 - cumulative should be 5 * 3,600,000 = 18,000,000 (max)
        year_5 = year_breakdown[4]["nisa_usage"]
        assert year_5["lifetime_total"]["used"] == 3600000 * 5  # 18,000,000
        assert year_5["lifetime_total"]["remaining"] == 0  # Fully used

    def test_projection_nisa_with_daily_frequency(
        self, authenticated_client, test_user
    ):
        """
        NISA usage should correctly calculate for DAILY frequency plans
        """
        RecurringInvestmentPlan.objects.create(
            user=test_user,
            target_account_type="NISA_TSUMITATE",
            target_asset_class="MUTUAL_FUND",
            target_asset_region="DOMESTIC_STOCKS",
            frequency="DAILY",
            amount_jpy=3000,  # 3,000 * 365 = 1,095,000 per year
            start_date="2025-01-01",
        )

        payload = {"projection_years": 1, "annual_return_rate": 3.0}

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 201
        data = response.json()

        year_breakdown = json.loads(data["year_by_year_breakdown"])
        year_1 = year_breakdown[0]["nisa_usage"]

        assert year_1["tsumitate"]["used"] == 1095000  # 3,000 * 365
        assert year_1["tsumitate"]["remaining"] == 1200000 - 1095000  # 105,000

    def test_projection_nisa_with_bonus_month_frequency(
        self, authenticated_client, test_user
    ):
        """
        NISA usage should correctly calculate for BONUS_MONTH frequency plans
        """
        RecurringInvestmentPlan.objects.create(
            user=test_user,
            target_account_type="NISA_GROWTH",
            target_asset_class="INDIVIDUAL_STOCK",
            target_asset_region="INTERNATIONAL_STOCKS",
            frequency="BONUS_MONTH",
            amount_jpy=500000,  # 500,000 * 2 = 1,000,000 per year
            bonus_months="6,12",  # June and December
            start_date="2025-01-01",
        )

        payload = {"projection_years": 1, "annual_return_rate": 4.0}

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 201
        data = response.json()

        year_breakdown = json.loads(data["year_by_year_breakdown"])
        year_1 = year_breakdown[0]["nisa_usage"]

        assert year_1["growth"]["used"] == 1000000  # 500,000 * 2
        assert year_1["growth"]["remaining"] == 2400000 - 1000000  # 1,400,000

    def test_projection_nisa_with_general_account_not_counted(
        self, authenticated_client, test_user
    ):
        """
        GENERAL account contributions should not affect NISA usage
        """
        # Create GENERAL account plan
        RecurringInvestmentPlan.objects.create(
            user=test_user,
            target_account_type="GENERAL",
            target_asset_class="MUTUAL_FUND",
            target_asset_region="DOMESTIC_STOCKS",
            frequency="MONTHLY",
            amount_jpy=500000,  # Large amount, but not NISA
            start_date="2025-01-01",
        )

        payload = {"projection_years": 1, "annual_return_rate": 4.0}

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 201
        data = response.json()

        year_breakdown = json.loads(data["year_by_year_breakdown"])
        year_1 = year_breakdown[0]["nisa_usage"]

        # All NISA frames should be unused
        assert year_1["tsumitate"]["used"] == 0
        assert year_1["growth"]["used"] == 0
        assert year_1["total"]["used"] == 0
        assert year_1["lifetime_total"]["used"] == 0

    def test_projection_nisa_with_continue_if_limit_exceeded_flag(
        self, authenticated_client, test_user
    ):
        """
        Plans with continue_if_limit_exceeded=True should cap NISA usage at limit
        """
        # Create plan that exceeds limit but allows continuation
        RecurringInvestmentPlan.objects.create(
            user=test_user,
            target_account_type="NISA_TSUMITATE",
            target_asset_class="MUTUAL_FUND",
            target_asset_region="DOMESTIC_STOCKS",
            frequency="MONTHLY",
            amount_jpy=150000,  # 1,800,000 per year (exceeds 1,200,000 limit)
            start_date="2025-01-01",
            continue_if_limit_exceeded=True,  # Continue after limit
        )

        payload = {"projection_years": 1, "annual_return_rate": 4.0}

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 201
        data = response.json()

        year_breakdown = json.loads(data["year_by_year_breakdown"])
        year_1 = year_breakdown[0]["nisa_usage"]

        # Should be capped at annual limit (1,200,000), not full amount (1,800,000)
        assert year_1["tsumitate"]["used"] == 1200000
        assert year_1["tsumitate"]["remaining"] == 0

    def test_projection_nisa_with_plan_ending_mid_projection(
        self, authenticated_client, test_user
    ):
        """
        Plans with end_date should stop contributing after that date
        """
        # Create plan that ends after 2 years
        RecurringInvestmentPlan.objects.create(
            user=test_user,
            target_account_type="NISA_TSUMITATE",
            target_asset_class="MUTUAL_FUND",
            target_asset_region="DOMESTIC_STOCKS",
            frequency="MONTHLY",
            amount_jpy=100000,  # 1,200,000 per year
            start_date="2025-01-01",
            end_date="2026-12-31",  # Ends after 2 years
        )

        payload = {"projection_years": 5, "annual_return_rate": 4.0}

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 201
        data = response.json()

        year_breakdown = json.loads(data["year_by_year_breakdown"])

        # Year 1 and 2 should have contributions
        assert year_breakdown[0]["nisa_usage"]["tsumitate"]["used"] == 1200000
        assert year_breakdown[1]["nisa_usage"]["tsumitate"]["used"] == 1200000

        # Year 3+ should have no new contributions
        assert year_breakdown[2]["nisa_usage"]["tsumitate"]["used"] == 0
        assert year_breakdown[3]["nisa_usage"]["tsumitate"]["used"] == 0

        # But lifetime usage should still show cumulative
        assert (
            year_breakdown[4]["nisa_usage"]["lifetime_tsumitate"]["used"] == 2400000
        )  # 2 years worth
