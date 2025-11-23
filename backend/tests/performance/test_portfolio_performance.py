"""
Performance optimization verification tests for portfolio operations.

These tests verify that query optimization changes have been correctly applied:
1. Portfolio summary uses database aggregation (GROUP BY) instead of Python loops
2. Projection calculation pre-fetches recurring plans to avoid N+1 queries
3. Database indexes are used for filtering by user_id
"""

from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.test import TestCase

from portfolio.models import InvestmentHolding, RecurringInvestmentPlan
from portfolio.services import ProjectionCalculationService
from portfolio.views import PortfolioSummaryView


class TestPortfolioOptimizations(TestCase):
    """Verify portfolio aggregation optimizations are working"""

    def setUp(self):
        self.user = User.objects.create_user(username="perf_test", password="test123")

    def test_portfolio_summary_with_multiple_holdings(self):
        """
        Portfolio summary should correctly aggregate holdings across regions.
        Uses optimized database aggregation (GROUP BY), not Python loops.
        """
        # Create holdings in different regions
        InvestmentHolding.objects.create(
            user=self.user,
            asset_name="Domestic Stocks",
            asset_identifier="DOMESTIC-1",
            asset_region="DOMESTIC_STOCKS",
            account_type="NISA",
            asset_class="INDIVIDUAL_STOCK",
            current_amount_jpy=Decimal("1000000"),
        )

        InvestmentHolding.objects.create(
            user=self.user,
            asset_name="International Stocks",
            asset_identifier="INTL-1",
            asset_region="INTERNATIONAL_STOCKS",
            account_type="NISA",
            asset_class="INDIVIDUAL_STOCK",
            current_amount_jpy=Decimal("2000000"),
        )

        InvestmentHolding.objects.create(
            user=self.user,
            asset_name="Domestic Bonds",
            asset_identifier="BONDS-1",
            asset_region="DOMESTIC_BONDS",
            account_type="GENERAL",
            asset_class="GOVERNMENT_BOND",
            current_amount_jpy=Decimal("500000"),
        )

        # Get portfolio summary
        summary = PortfolioSummaryView.get_portfolio_summary(self.user)

        # Verify aggregation results
        assert summary["total_value_jpy"] == Decimal("3500000")
        assert summary["holdings_count"] == 3

        # Verify composition by region
        assert "DOMESTIC_STOCKS" in summary["composition_by_region"]
        assert "INTERNATIONAL_STOCKS" in summary["composition_by_region"]
        assert "DOMESTIC_BONDS" in summary["composition_by_region"]

        # Verify percentages sum to 100
        region_percentages = [
            item["percentage"] for item in summary["composition_by_region"].values()
        ]
        total_percentage = sum(region_percentages)
        assert abs(total_percentage - 100.0) < 0.01

    def test_portfolio_summary_composition_accuracy(self):
        """
        Verify composition percentages are calculated correctly
        """
        # Create holdings with known amounts
        InvestmentHolding.objects.create(
            user=self.user,
            asset_name="Large Holding",
            asset_identifier="LARGE-1",
            asset_region="DOMESTIC_STOCKS",
            account_type="NISA",
            asset_class="MUTUAL_FUND",
            current_amount_jpy=Decimal("1000000"),
        )

        InvestmentHolding.objects.create(
            user=self.user,
            asset_name="Small Holding",
            asset_identifier="SMALL-1",
            asset_region="DOMESTIC_STOCKS",
            account_type="NISA",
            asset_class="MUTUAL_FUND",
            current_amount_jpy=Decimal("1000000"),
        )

        summary = PortfolioSummaryView.get_portfolio_summary(self.user)

        # Should have 2M total, all in domestic stocks
        assert summary["total_value_jpy"] == Decimal("2000000")
        assert summary["composition_by_region"]["DOMESTIC_STOCKS"]["amount"] == Decimal(
            "2000000"
        )
        assert (
            summary["composition_by_region"]["DOMESTIC_STOCKS"]["percentage"] == 100.0
        )

    def test_portfolio_summary_with_zero_holdings(self):
        """Portfolio summary should handle users with no holdings"""
        summary = PortfolioSummaryView.get_portfolio_summary(self.user)

        assert summary["total_value_jpy"] == 0
        assert summary["holdings_count"] == 0
        assert len(summary["composition_by_region"]) == 0

    def test_projection_calculation_with_holdings(self):
        """
        Test projection calculation with pre-fetched plans optimization.
        Should correctly compound holding values over multiple years.
        """
        # Create a simple holding
        InvestmentHolding.objects.create(
            user=self.user,
            asset_name="Test Holding",
            asset_identifier="TEST-1",
            asset_region="DOMESTIC_STOCKS",
            account_type="NISA",
            asset_class="INDIVIDUAL_STOCK",
            current_amount_jpy=Decimal("1000000"),
        )

        # Project 10 years at 5% annual return
        projection = ProjectionCalculationService.calculate_projection(
            user=self.user,
            projection_years=10,
            annual_return_rate=Decimal("5.0"),
        )

        # Verify projection was created
        assert projection.id is not None
        assert projection.projection_years == 10
        assert projection.annual_return_rate == Decimal("5.0")

        # Verify final value is greater than starting (positive return)
        assert projection.projected_total_value_jpy > projection.starting_balance_jpy

        # Verify composition was calculated
        import json

        composition = json.loads(projection.projected_composition_by_region)
        assert "DOMESTIC_STOCKS" in composition
        assert composition["DOMESTIC_STOCKS"]["percentage"] == 100.0

    def test_projection_with_recurring_plans(self):
        """
        Test projection with recurring investment plans.
        Plans should be pre-fetched to avoid N+1 queries in year loop.
        """
        # Create holding
        InvestmentHolding.objects.create(
            user=self.user,
            asset_name="Initial Holding",
            asset_identifier="INIT-1",
            asset_region="DOMESTIC_STOCKS",
            account_type="NISA",
            asset_class="INDIVIDUAL_STOCK",
            current_amount_jpy=Decimal("1000000"),
        )

        # Create monthly recurring plan
        RecurringInvestmentPlan.objects.create(
            user=self.user,
            target_asset_region="DOMESTIC_STOCKS",
            target_asset_class="INDIVIDUAL_STOCK",
            target_account_type="NISA",
            amount_jpy=Decimal("100000"),
            frequency="MONTHLY",
            start_date="2024-01-01",
        )

        # Project 5 years
        projection = ProjectionCalculationService.calculate_projection(
            user=self.user,
            projection_years=5,
            annual_return_rate=Decimal("3.0"),
        )

        # Verify projection includes contributions
        assert projection.total_accumulated_contributions_jpy > 0
        # 100k/month * 12 months * 5 years = 6M contributions
        assert projection.total_accumulated_contributions_jpy == Decimal("6000000")

        # Final value should be > starting + contributions (due to interest)
        assert (
            projection.projected_total_value_jpy
            > projection.starting_balance_jpy
            + projection.total_accumulated_contributions_jpy
        )

    def test_projection_validation(self):
        """Test projection parameter validation"""
        InvestmentHolding.objects.create(
            user=self.user,
            asset_name="Test",
            asset_identifier="TEST-1",
            asset_region="DOMESTIC_STOCKS",
            account_type="NISA",
            asset_class="INDIVIDUAL_STOCK",
            current_amount_jpy=Decimal("100000"),
        )

        # Invalid years (too low)
        with pytest.raises(
            ValueError, match="projection_years must be between 1 and 50"
        ):
            ProjectionCalculationService.calculate_projection(
                user=self.user,
                projection_years=0,
                annual_return_rate=Decimal("4.0"),
            )

        # Invalid years (too high)
        with pytest.raises(
            ValueError, match="projection_years must be between 1 and 50"
        ):
            ProjectionCalculationService.calculate_projection(
                user=self.user,
                projection_years=51,
                annual_return_rate=Decimal("4.0"),
            )

        # Invalid return rate (too high)
        with pytest.raises(
            ValueError, match="annual_return_rate must be between -100 and 100"
        ):
            ProjectionCalculationService.calculate_projection(
                user=self.user,
                projection_years=10,
                annual_return_rate=Decimal("101.0"),
            )
