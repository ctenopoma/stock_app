"""
Integration tests for Projection model and calculation service

Tests verify:
- ProjectionCalculationService correctly implements compound interest formula
- Year-by-year breakdown is accurate
- Contribution calculations for different frequencies work correctly
- Portfolio composition projection maintains proportions
"""

import json
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from portfolio.models import InvestmentHolding, RecurringInvestmentPlan
from portfolio.services import ProjectionCalculationService


@pytest.mark.django_db
class TestProjectionCalculationService:
    """Test projection calculation service"""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Create test user and sample data"""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

    def test_calculate_projection_with_no_holdings_or_plans(self):
        """Projection with zero starting balance and no plans"""
        projection = ProjectionCalculationService.calculate_projection(
            user=self.user,
            projection_years=5,
            annual_return_rate=Decimal("4.0"),
        )

        assert projection.starting_balance_jpy == Decimal("0.00")
        assert projection.total_accumulated_contributions_jpy == Decimal("0.00")
        assert projection.projected_total_value_jpy == Decimal("0.00")
        assert projection.total_interest_gains_jpy == Decimal("0.00")

    def test_calculate_projection_with_current_holdings_only(self):
        """Projection with only current holdings, no recurring plans"""
        # Create a holding worth 1,000,000 JPY
        InvestmentHolding.objects.create(
            user=self.user,
            account_type="NISA",
            asset_class="MUTUAL_FUND",
            asset_region="DOMESTIC_STOCKS",
            asset_identifier="TEST001",
            asset_name="Test Fund",
            current_amount_jpy=Decimal("1000000.00"),
        )

        projection = ProjectionCalculationService.calculate_projection(
            user=self.user,
            projection_years=1,
            annual_return_rate=Decimal("4.0"),
        )

        # FV = 1,000,000 × (1 + 0.04)^1 = 1,040,000
        expected_final_value = Decimal("1000000.00") * (1 + Decimal("0.04"))

        assert projection.starting_balance_jpy == Decimal("1000000.00")
        assert projection.total_accumulated_contributions_jpy == Decimal("0.00")
        # Check within 2 decimal places (rounding)
        assert abs(
            projection.projected_total_value_jpy - expected_final_value
        ) < Decimal("1.00")

    def test_calculate_projection_with_monthly_recurring_plan(self):
        """Projection with monthly recurring investment plan"""
        # Create a holding to have a starting balance
        InvestmentHolding.objects.create(
            user=self.user,
            account_type="NISA",
            asset_class="MUTUAL_FUND",
            asset_region="DOMESTIC_STOCKS",
            asset_identifier="TEST001",
            asset_name="Test Fund",
            current_amount_jpy=Decimal("1000000.00"),
        )

        # Create a monthly recurring plan: 50,000 JPY per month
        today = date.today()
        RecurringInvestmentPlan.objects.create(
            user=self.user,
            target_account_type="NISA",
            target_asset_class="MUTUAL_FUND",
            target_asset_region="DOMESTIC_STOCKS",
            frequency="MONTHLY",
            amount_jpy=Decimal("50000.00"),
            start_date=today,
        )

        projection = ProjectionCalculationService.calculate_projection(
            user=self.user,
            projection_years=1,
            annual_return_rate=Decimal("4.0"),
        )

        # Contributions: 50,000 × 12 = 600,000
        # FV = (1,000,000 + 600,000) × 1.04 = 1,664,000
        expected_contributions = Decimal("50000.00") * 12
        expected_final_value = (
            Decimal("1000000.00") + expected_contributions
        ) * Decimal("1.04")

        assert projection.total_accumulated_contributions_jpy == expected_contributions
        assert abs(
            projection.projected_total_value_jpy - expected_final_value
        ) < Decimal("1.00")

    def test_calculate_projection_with_daily_recurring_plan(self):
        """Projection with daily recurring investment plan"""
        InvestmentHolding.objects.create(
            user=self.user,
            account_type="GENERAL",
            asset_class="INDIVIDUAL_STOCK",
            asset_region="INTERNATIONAL_STOCKS",
            asset_identifier="AAPL",
            asset_name="Apple Inc.",
            current_amount_jpy=Decimal("500000.00"),
        )

        # Daily plan: 1,000 JPY per day
        today = date.today()
        RecurringInvestmentPlan.objects.create(
            user=self.user,
            target_account_type="GENERAL",
            target_asset_class="INDIVIDUAL_STOCK",
            target_asset_region="INTERNATIONAL_STOCKS",
            frequency="DAILY",
            amount_jpy=Decimal("1000.00"),
            start_date=today,
        )

        projection = ProjectionCalculationService.calculate_projection(
            user=self.user,
            projection_years=1,
            annual_return_rate=Decimal("5.0"),
        )

        # Contributions: 1,000 × 365 = 365,000
        expected_contributions = Decimal("1000.00") * 365
        expected_final_value = (
            Decimal("500000.00") + expected_contributions
        ) * Decimal("1.05")

        assert projection.total_accumulated_contributions_jpy == expected_contributions
        assert abs(
            projection.projected_total_value_jpy - expected_final_value
        ) < Decimal("1.00")

    def test_calculate_projection_with_bonus_month_plan(self):
        """Projection with bonus month recurring plan (e.g., June and December)"""
        InvestmentHolding.objects.create(
            user=self.user,
            account_type="NISA",
            asset_class="MUTUAL_FUND",
            asset_region="DOMESTIC_BONDS",
            asset_identifier="BOND001",
            asset_name="Bond Fund",
            current_amount_jpy=Decimal("2000000.00"),
        )

        # Bonus plan: 200,000 JPY in June (6) and December (12)
        today = date.today()
        RecurringInvestmentPlan.objects.create(
            user=self.user,
            target_account_type="NISA",
            target_asset_class="MUTUAL_FUND",
            target_asset_region="DOMESTIC_BONDS",
            frequency="BONUS_MONTH",
            amount_jpy=Decimal("200000.00"),
            start_date=today,
            bonus_months="6,12",
        )

        projection = ProjectionCalculationService.calculate_projection(
            user=self.user,
            projection_years=1,
            annual_return_rate=Decimal("3.0"),
        )

        # Contributions: 200,000 × 2 months = 400,000
        expected_contributions = Decimal("200000.00") * 2
        expected_final_value = (
            Decimal("2000000.00") + expected_contributions
        ) * Decimal("1.03")

        assert projection.total_accumulated_contributions_jpy == expected_contributions
        assert abs(
            projection.projected_total_value_jpy - expected_final_value
        ) < Decimal("1.00")

    def test_calculate_projection_multiple_years(self):
        """Projection over multiple years with compound growth"""
        InvestmentHolding.objects.create(
            user=self.user,
            account_type="NISA",
            asset_class="MUTUAL_FUND",
            asset_region="DOMESTIC_STOCKS",
            asset_identifier="NISA001",
            asset_name="NISA Fund",
            current_amount_jpy=Decimal("1000000.00"),
        )

        # No recurring plans, just compound growth
        projection = ProjectionCalculationService.calculate_projection(
            user=self.user,
            projection_years=3,
            annual_return_rate=Decimal("5.0"),
        )

        # Year 1: 1,000,000 × 1.05 = 1,050,000
        # Year 2: 1,050,000 × 1.05 = 1,102,500
        # Year 3: 1,102,500 × 1.05 = 1,157,625
        expected_final = Decimal("1000000.00") * (Decimal("1.05") ** 3)

        assert abs(projection.projected_total_value_jpy - expected_final) < Decimal(
            "1.00"
        )
        # Interest gains = final - starting (no contributions)
        assert abs(
            projection.total_interest_gains_jpy
            - (expected_final - Decimal("1000000.00"))
        ) < Decimal("1.00")

    def test_calculate_projection_year_by_year_breakdown(self):
        """Verify year-by-year breakdown structure and values"""
        InvestmentHolding.objects.create(
            user=self.user,
            account_type="NISA",
            asset_class="MUTUAL_FUND",
            asset_region="DOMESTIC_STOCKS",
            asset_identifier="TEST001",
            asset_name="Test Fund",
            current_amount_jpy=Decimal("1000000.00"),
        )

        projection = ProjectionCalculationService.calculate_projection(
            user=self.user,
            projection_years=2,
            annual_return_rate=Decimal("4.0"),
        )

        # Parse year-by-year breakdown
        breakdown = json.loads(projection.year_by_year_breakdown)

        assert len(breakdown) == 2
        assert breakdown[0]["year"] == 1
        assert breakdown[1]["year"] == 2

        # Verify first year
        assert breakdown[0]["starting_balance"] == 1000000.0
        assert breakdown[0]["contributions"] == 0.0
        assert breakdown[0]["growth_rate"] == 0.04

    def test_calculate_projection_with_negative_return_rate(self):
        """Projection handles negative returns (market downturn)"""
        InvestmentHolding.objects.create(
            user=self.user,
            account_type="GENERAL",
            asset_class="INDIVIDUAL_STOCK",
            asset_region="CRYPTOCURRENCY",
            asset_identifier="BTC",
            asset_name="Bitcoin",
            current_amount_jpy=Decimal("500000.00"),
        )

        projection = ProjectionCalculationService.calculate_projection(
            user=self.user,
            projection_years=1,
            annual_return_rate=Decimal("-10.0"),  # -10% return
        )

        # FV = 500,000 × (1 - 0.10) = 450,000
        expected_final = Decimal("500000.00") * Decimal("0.90")

        assert abs(projection.projected_total_value_jpy - expected_final) < Decimal(
            "1.00"
        )
        assert projection.total_interest_gains_jpy < 0  # Negative gains

    def test_calculate_projection_invalid_years_raises_error(self):
        """Invalid projection years should raise ValueError"""
        with pytest.raises(ValueError):
            ProjectionCalculationService.calculate_projection(
                user=self.user,
                projection_years=0,  # Too small
                annual_return_rate=Decimal("4.0"),
            )

        with pytest.raises(ValueError):
            ProjectionCalculationService.calculate_projection(
                user=self.user,
                projection_years=51,  # Too large
                annual_return_rate=Decimal("4.0"),
            )

    def test_calculate_projection_invalid_return_rate_raises_error(self):
        """Invalid return rate should raise ValueError"""
        with pytest.raises(ValueError):
            ProjectionCalculationService.calculate_projection(
                user=self.user,
                projection_years=10,
                annual_return_rate=Decimal("-101.0"),  # Too low
            )

        with pytest.raises(ValueError):
            ProjectionCalculationService.calculate_projection(
                user=self.user,
                projection_years=10,
                annual_return_rate=Decimal("101.0"),  # Too high
            )

    def test_calculate_projection_maintains_composition_proportions(self):
        """Projected composition maintains current proportions"""
        # Create holdings in different regions
        InvestmentHolding.objects.create(
            user=self.user,
            account_type="NISA",
            asset_class="MUTUAL_FUND",
            asset_region="DOMESTIC_STOCKS",
            asset_identifier="DOM",
            asset_name="Domestic",
            current_amount_jpy=Decimal("600000.00"),  # 60%
        )
        InvestmentHolding.objects.create(
            user=self.user,
            account_type="GENERAL",
            asset_class="MUTUAL_FUND",
            asset_region="INTERNATIONAL_STOCKS",
            asset_identifier="INTL",
            asset_name="International",
            current_amount_jpy=Decimal("400000.00"),  # 40%
        )

        projection = ProjectionCalculationService.calculate_projection(
            user=self.user,
            projection_years=1,
            annual_return_rate=Decimal("4.0"),
        )

        composition = json.loads(projection.projected_composition_by_region)

        # Check proportions are maintained
        domestic_pct = composition.get("DOMESTIC_STOCKS", {}).get("percentage", 0)
        international_pct = composition.get("INTERNATIONAL_STOCKS", {}).get(
            "percentage", 0
        )

        assert abs(domestic_pct - 60.0) < 1.0
        assert abs(international_pct - 40.0) < 1.0
