"""
Integration tests for portfolio summary endpoint
Tests portfolio composition calculation and aggregation
"""

from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from portfolio.models import InvestmentHolding


@pytest.mark.integration
class TestPortfolioSummaryIntegration:
    """Integration tests for portfolio summary calculations"""

    @pytest.fixture
    def user(self, db):
        """Create a test user"""
        return User.objects.create_user(username="testuser", password="testpass123")

    @pytest.fixture
    def authenticated_client(self, client, user):
        """Return authenticated client"""
        client.force_login(user)
        return client

    def test_portfolio_summary_with_single_holding(
        self, db, authenticated_client, user
    ):
        """Test portfolio summary with one holding"""
        # Create a holding
        holding = InvestmentHolding.objects.create(
            user=user,
            account_type="NISA",
            asset_class="MUTUAL_FUND",
            asset_region="DOMESTIC_STOCKS",
            asset_identifier="JP0123456789",
            asset_name="Test Fund",
            current_amount_jpy=Decimal("1000000.00"),
        )

        # Fetch portfolio summary
        response = authenticated_client.get("/api/v1/portfolio/summary/")

        assert response.status_code == 200
        data = response.json()

        # Verify total value
        assert data["total_value_jpy"] == 1000000.0
        assert data["holdings_count"] == 1

        # Verify composition by region
        assert "DOMESTIC_STOCKS" in data["composition_by_region"]
        assert data["composition_by_region"]["DOMESTIC_STOCKS"]["amount"] == 1000000.0
        assert data["composition_by_region"]["DOMESTIC_STOCKS"]["percentage"] == 100.0

        # Verify composition by account type
        assert "NISA" in data["composition_by_account_type"]
        assert data["composition_by_account_type"]["NISA"]["amount"] == 1000000.0
        assert data["composition_by_account_type"]["NISA"]["percentage"] == 100.0

    def test_portfolio_summary_with_multiple_holdings(
        self, db, authenticated_client, user
    ):
        """Test portfolio summary with multiple holdings across regions"""
        # Create holdings in different regions
        InvestmentHolding.objects.create(
            user=user,
            account_type="NISA",
            asset_class="MUTUAL_FUND",
            asset_region="DOMESTIC_STOCKS",
            asset_identifier="JP001",
            asset_name="Domestic Fund",
            current_amount_jpy=Decimal("2000000.00"),
        )

        InvestmentHolding.objects.create(
            user=user,
            account_type="GENERAL",
            asset_class="INDIVIDUAL_STOCK",
            asset_region="INTERNATIONAL_STOCKS",
            asset_identifier="AAPL",
            asset_name="Apple",
            current_amount_jpy=Decimal("3000000.00"),
        )

        InvestmentHolding.objects.create(
            user=user,
            account_type="GENERAL",
            asset_class="GOVERNMENT_BOND",
            asset_region="DOMESTIC_BONDS",
            asset_identifier="JGB001",
            asset_name="JGB 10Y",
            current_amount_jpy=Decimal("500000.00"),
        )

        # Fetch portfolio summary
        response = authenticated_client.get("/api/v1/portfolio/summary/")

        assert response.status_code == 200
        data = response.json()

        # Verify total value
        assert data["total_value_jpy"] == 5500000.0
        assert data["holdings_count"] == 3

        # Verify composition by region
        assert data["composition_by_region"]["DOMESTIC_STOCKS"]["amount"] == 2000000.0
        assert (
            abs(data["composition_by_region"]["DOMESTIC_STOCKS"]["percentage"] - 36.36)
            < 0.1
        )

        assert (
            data["composition_by_region"]["INTERNATIONAL_STOCKS"]["amount"] == 3000000.0
        )
        assert (
            abs(
                data["composition_by_region"]["INTERNATIONAL_STOCKS"]["percentage"]
                - 54.55
            )
            < 0.1
        )

        assert data["composition_by_region"]["DOMESTIC_BONDS"]["amount"] == 500000.0
        assert (
            abs(data["composition_by_region"]["DOMESTIC_BONDS"]["percentage"] - 9.09)
            < 0.1
        )

        # Verify composition by account type
        assert data["composition_by_account_type"]["NISA"]["amount"] == 2000000.0
        assert (
            abs(data["composition_by_account_type"]["NISA"]["percentage"] - 36.36) < 0.1
        )

        assert data["composition_by_account_type"]["GENERAL"]["amount"] == 3500000.0
        assert (
            abs(data["composition_by_account_type"]["GENERAL"]["percentage"] - 63.64)
            < 0.1
        )

    def test_portfolio_summary_with_zero_holdings(self, db, authenticated_client, user):
        """Test portfolio summary when user has no holdings"""
        response = authenticated_client.get("/api/v1/portfolio/summary/")

        assert response.status_code == 200
        data = response.json()

        assert data["total_value_jpy"] == 0
        assert data["holdings_count"] == 0
        assert len(data["composition_by_region"]) == 0
        assert len(data["composition_by_account_type"]) == 0

    def test_portfolio_summary_user_isolation(self, db, client):
        """Test that users only see their own portfolio summary"""
        user1 = User.objects.create_user(username="user1", password="pass123")
        user2 = User.objects.create_user(username="user2", password="pass123")

        # User1 creates a holding
        InvestmentHolding.objects.create(
            user=user1,
            account_type="NISA",
            asset_class="MUTUAL_FUND",
            asset_region="DOMESTIC_STOCKS",
            asset_identifier="JP001",
            asset_name="Fund 1",
            current_amount_jpy=Decimal("1000000.00"),
        )

        # User2 creates a different holding
        InvestmentHolding.objects.create(
            user=user2,
            account_type="GENERAL",
            asset_class="INDIVIDUAL_STOCK",
            asset_region="INTERNATIONAL_STOCKS",
            asset_identifier="AAPL",
            asset_name="Apple",
            current_amount_jpy=Decimal("2000000.00"),
        )

        # User1 fetches their portfolio
        client.force_login(user1)
        response = client.get("/api/v1/portfolio/summary/")
        assert response.status_code == 200
        data = response.json()

        assert data["total_value_jpy"] == 1000000.0
        assert data["holdings_count"] == 1
        assert "DOMESTIC_STOCKS" in data["composition_by_region"]
        assert "INTERNATIONAL_STOCKS" not in data["composition_by_region"]

        # User2 fetches their portfolio
        client.force_login(user2)
        response = client.get("/api/v1/portfolio/summary/")
        assert response.status_code == 200
        data = response.json()

        assert data["total_value_jpy"] == 2000000.0
        assert data["holdings_count"] == 1
        assert "INTERNATIONAL_STOCKS" in data["composition_by_region"]
        assert "DOMESTIC_STOCKS" not in data["composition_by_region"]

    def test_portfolio_summary_requires_authentication(self, db, client):
        """Test that portfolio summary endpoint requires authentication"""
        response = client.get("/api/v1/portfolio/summary/")

        assert response.status_code == 401

    def test_portfolio_summary_with_zero_amounts(self, db, authenticated_client, user):
        """Test portfolio summary with zero-amount holdings (valid edge case)"""
        # Create a holding with zero amount
        InvestmentHolding.objects.create(
            user=user,
            account_type="NISA",
            asset_class="MUTUAL_FUND",
            asset_region="DOMESTIC_STOCKS",
            asset_identifier="JP001",
            asset_name="Empty Fund",
            current_amount_jpy=Decimal("0.00"),
        )

        # Create another holding with amount
        InvestmentHolding.objects.create(
            user=user,
            account_type="GENERAL",
            asset_class="INDIVIDUAL_STOCK",
            asset_region="INTERNATIONAL_STOCKS",
            asset_identifier="AAPL",
            asset_name="Apple",
            current_amount_jpy=Decimal("1000000.00"),
        )

        # Fetch portfolio summary
        response = authenticated_client.get("/api/v1/portfolio/summary/")

        assert response.status_code == 200
        data = response.json()

        # Total should only count the non-zero holding
        assert data["total_value_jpy"] == 1000000.0
        assert data["holdings_count"] == 2

        # Verify that the empty holding doesn't affect percentages
        assert data["composition_by_region"]["DOMESTIC_STOCKS"]["amount"] == 0.0
        assert (
            data["composition_by_region"]["INTERNATIONAL_STOCKS"]["amount"] == 1000000.0
        )
        assert (
            data["composition_by_region"]["INTERNATIONAL_STOCKS"]["percentage"] == 100.0
        )

    def test_portfolio_summary_composition_by_asset_class(
        self, db, authenticated_client, user
    ):
        """Test portfolio composition grouped by asset class"""
        # Create holdings of different asset classes
        InvestmentHolding.objects.create(
            user=user,
            account_type="NISA",
            asset_class="MUTUAL_FUND",
            asset_region="DOMESTIC_STOCKS",
            asset_identifier="JP001",
            asset_name="Fund",
            current_amount_jpy=Decimal("2000000.00"),
        )

        InvestmentHolding.objects.create(
            user=user,
            account_type="GENERAL",
            asset_class="INDIVIDUAL_STOCK",
            asset_region="INTERNATIONAL_STOCKS",
            asset_identifier="AAPL",
            asset_name="Apple",
            current_amount_jpy=Decimal("3000000.00"),
        )

        # Fetch portfolio summary
        response = authenticated_client.get("/api/v1/portfolio/summary/")

        assert response.status_code == 200
        data = response.json()

        # Verify composition by asset class
        assert "MUTUAL_FUND" in data["composition_by_asset_class"]
        assert data["composition_by_asset_class"]["MUTUAL_FUND"]["amount"] == 2000000.0
        assert (
            abs(data["composition_by_asset_class"]["MUTUAL_FUND"]["percentage"] - 40.0)
            < 0.1
        )

        assert "INDIVIDUAL_STOCK" in data["composition_by_asset_class"]
        assert (
            data["composition_by_asset_class"]["INDIVIDUAL_STOCK"]["amount"]
            == 3000000.0
        )
        assert (
            abs(
                data["composition_by_asset_class"]["INDIVIDUAL_STOCK"]["percentage"]
                - 60.0
            )
            < 0.1
        )

    def test_portfolio_summary_large_portfolio(self, db, authenticated_client, user):
        """Test portfolio summary with many holdings (stress test)"""
        # Create 50 holdings
        regions = [
            "DOMESTIC_STOCKS",
            "INTERNATIONAL_STOCKS",
            "DOMESTIC_BONDS",
            "CRYPTOCURRENCY",
        ]
        asset_classes = ["INDIVIDUAL_STOCK", "MUTUAL_FUND", "GOVERNMENT_BOND"]
        account_types = ["NISA", "GENERAL"]

        total_expected = Decimal("0.00")
        for i in range(50):
            amount = Decimal(str(100000 * (i + 1)))
            InvestmentHolding.objects.create(
                user=user,
                account_type=account_types[i % 2],
                asset_class=asset_classes[i % 3],
                asset_region=regions[i % 4],
                asset_identifier=f"ASSET{i:03d}",
                asset_name=f"Asset {i}",
                current_amount_jpy=amount,
            )
            total_expected += amount

        # Fetch portfolio summary
        response = authenticated_client.get("/api/v1/portfolio/summary/")

        assert response.status_code == 200
        data = response.json()

        # Verify count and total
        assert data["holdings_count"] == 50
        assert data["total_value_jpy"] == float(total_expected)

        # Verify percentages sum to approximately 100%
        region_percentages = [
            item["percentage"] for item in data["composition_by_region"].values()
        ]
        assert abs(sum(region_percentages) - 100.0) < 0.01

    def test_portfolio_summary_decimal_precision(self, db, authenticated_client, user):
        """Test portfolio summary maintains decimal precision"""
        # Create holdings with decimal amounts
        InvestmentHolding.objects.create(
            user=user,
            account_type="NISA",
            asset_class="MUTUAL_FUND",
            asset_region="DOMESTIC_STOCKS",
            asset_identifier="JP001",
            asset_name="Fund",
            current_amount_jpy=Decimal("123456.78"),
        )

        InvestmentHolding.objects.create(
            user=user,
            account_type="GENERAL",
            asset_class="INDIVIDUAL_STOCK",
            asset_region="DOMESTIC_STOCKS",
            asset_identifier="JP002",
            asset_name="Stock",
            current_amount_jpy=Decimal("987654.32"),
        )

        # Fetch portfolio summary
        response = authenticated_client.get("/api/v1/portfolio/summary/")

        assert response.status_code == 200
        data = response.json()

        expected_total = 123456.78 + 987654.32
        assert abs(data["total_value_jpy"] - expected_total) < 0.01
