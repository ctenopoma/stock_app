"""
Portfolio projection calculation service

Implements compound interest calculations for future portfolio forecasting
based on current holdings, recurring investment plans, and specified annual return rates.

Performance optimizations:
- Use select_related/prefetch_related to eliminate N+1 queries
- Cache current portfolio total calculation
- Single database queries for composition calculations
"""

import json
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from django.contrib.auth.models import User
from django.db.models import Sum

from portfolio.models import InvestmentHolding, Projection, RecurringInvestmentPlan


class ProjectionCalculationService:
    """
    Service for calculating future portfolio projections using compound interest formula.

    Formula: FV = PV × (1 + r)^n + sum of contributions (each also compounded)

    Where:
    - FV = Final Value
    - PV = Present Value (current portfolio)
    - r = annual return rate (as decimal, e.g., 0.04 for 4%)
    - n = number of years
    - Contributions are made throughout the year and also accrue interest
    """

    # Cache for recurring plans (avoid repeated database queries in loops)
    _plan_cache = {}

    @staticmethod
    def calculate_projection(
        user: User,
        projection_years: int,
        annual_return_rate: Decimal,
    ) -> Projection:
        """
        Calculate future portfolio projection for a user.

        OPTIMIZATION: Cache recurring plans to avoid N queries in year loop.

        Args:
            user: The user whose portfolio to project
            projection_years: Number of years to project (1-50)
            annual_return_rate: Annual return rate as percentage (e.g., Decimal('4.0') for 4%)

        Returns:
            Projection object with calculated values

        Raises:
            ValueError: If parameters are invalid
        """
        # Validate inputs
        if not (1 <= projection_years <= 50):
            raise ValueError("projection_years must be between 1 and 50")

        if not (-100 <= annual_return_rate <= 100):
            raise ValueError("annual_return_rate must be between -100 and 100")

        # OPTIMIZATION: Pre-fetch all recurring plans once (cache for loop)
        plans = list(RecurringInvestmentPlan.objects.filter(user=user))

        # Get current portfolio state (snapshot)
        starting_balance = ProjectionCalculationService._get_current_portfolio_total(
            user
        )

        # Convert percentage to decimal (4.0 → 0.04)
        rate_decimal = annual_return_rate / Decimal(100)

        # Calculate year-by-year projection
        year_breakdown: List[Dict] = []
        current_balance = starting_balance
        total_contributions = Decimal(0)
        
        # Track cumulative NISA usage across years, seeded with current lifetime usage
        lifetime_usage = InvestmentHolding.get_nisa_lifetime_usage(user)
        cumulative_nisa = {
            "tsumitate": Decimal(lifetime_usage["tsumitate"]["amount"]),
            "growth": Decimal(lifetime_usage["growth"]["amount"]),
        }

        # Seed annual base with current-year usage for year 0
        current_year_usage = InvestmentHolding.get_nisa_usage_by_year(user)
        annual_base = {
            "tsumitate": Decimal(current_year_usage["tsumitate"]["amount"]),
            "growth": Decimal(current_year_usage["growth"]["amount"]),
        }

        for year in range(projection_years):
            # Calculate contributions for this year using cached plans
            year_contributions = (
                ProjectionCalculationService._calculate_year_contributions_cached(
                    plans, year
                )
            )
            total_contributions += year_contributions

            # Calculate NISA usage for this year (include existing usage in first year)
            nisa_usage = ProjectionCalculationService._calculate_nisa_usage_for_year(
                plans,
                year,
                cumulative_nisa,
                base_annual=annual_base if year == 0 else None,
            )

            # Add contributions to current balance
            balance_with_contributions = current_balance + year_contributions

            # Apply compound growth for this year
            growth_factor = 1 + rate_decimal
            end_of_year_balance = balance_with_contributions * growth_factor

            # Record year breakdown with NISA information
            year_breakdown.append(
                {
                    "year": year + 1,
                    "starting_balance": float(current_balance),
                    "contributions": float(year_contributions),
                    "balance_before_growth": float(balance_with_contributions),
                    "growth_rate": float(rate_decimal),
                    "ending_balance": float(end_of_year_balance),
                    "interest_earned": float(
                        end_of_year_balance - balance_with_contributions
                    ),
                    "nisa_usage": nisa_usage,
                }
            )

            current_balance = end_of_year_balance

        # Calculate final metrics
        projected_total_value = current_balance
        interest_gains = projected_total_value - starting_balance - total_contributions

        # Calculate projected composition using future ratios (plans by region and by asset class)
        projected_composition = ProjectionCalculationService._project_future_composition_by_region(
            user=user,
            plans=plans,
            projection_years=projection_years,
            rate_decimal=rate_decimal,
        )
        projected_composition_by_class = ProjectionCalculationService._project_future_composition_by_asset_class(
            user=user,
            plans=plans,
            projection_years=projection_years,
            rate_decimal=rate_decimal,
        )

        # Create and return Projection record
        projection = Projection.objects.create(
            user=user,
            projection_years=projection_years,
            annual_return_rate=annual_return_rate,
            starting_balance_jpy=starting_balance,
            total_accumulated_contributions_jpy=total_contributions,
            total_interest_gains_jpy=interest_gains,
            projected_total_value_jpy=projected_total_value,
            projected_composition_by_region=json.dumps(projected_composition),
            projected_composition_by_asset_class=json.dumps(projected_composition_by_class),
            year_by_year_breakdown=json.dumps(year_breakdown),
        )

        return projection

    @staticmethod
    def _get_current_portfolio_total(user: User) -> Decimal:
        """
        Get the current total portfolio value for a user using database aggregation.

        OPTIMIZATION: Uses Django Sum() aggregation instead of Python loop.
        - Old approach: Load all holdings into memory, sum in Python (N+1 if accessing FK fields)
        - New approach: Single database aggregation query

        Args:
            user: The user

        Returns:
            Total portfolio value in JPY
        """
        result = InvestmentHolding.objects.filter(user=user).aggregate(
            total=Sum("current_amount_jpy")
        )
        return result["total"] or Decimal(0)

    @staticmethod
    def _calculate_year_contributions(user: User, year: int) -> Decimal:
        """
        Calculate total contributions for a given projection year.

        Assumes:
        - MONTHLY: 12 contributions per year
        - DAILY: 365 contributions per year
        - BONUS_MONTH: contributions on specified months only

        Args:
            user: The user
            year: Year index (0-based)

        Returns:
            Total contributions for that year
        """
        plans = RecurringInvestmentPlan.objects.filter(user=user)
        total_contributions = Decimal(0)

        today = date.today()
        projection_date = today + timedelta(days=365 * year)

        for plan in plans:
            # Skip if plan hasn't started yet or has ended
            if plan.start_date > projection_date:
                continue
            if plan.end_date and plan.end_date < projection_date:
                continue

            # Calculate contributions based on frequency
            if plan.frequency == "MONTHLY":
                total_contributions += plan.amount_jpy * 12
            elif plan.frequency == "DAILY":
                total_contributions += plan.amount_jpy * 365
            elif plan.frequency == "BONUS_MONTH":
                # Parse bonus_months (comma-separated string or list)
                if plan.bonus_months:
                    if isinstance(plan.bonus_months, str):
                        months = [int(m.strip()) for m in plan.bonus_months.split(",")]
                    else:
                        months = plan.bonus_months
                    total_contributions += plan.amount_jpy * len(months)

        return total_contributions

    @staticmethod
    def _calculate_year_contributions_cached(plans: List, year: int) -> Decimal:
        """
        Calculate total contributions for a given projection year using pre-fetched plans.

        OPTIMIZATION: Use pre-fetched plans list instead of querying database per year.
        This eliminates N database queries in the projection loop.

        Args:
            plans: Pre-fetched list of RecurringInvestmentPlan objects
            year: Year index (0-based)

        Returns:
            Total contributions for that year
        """
        total_contributions = Decimal(0)

        today = date.today()

        # Helper: count months between first-of-month dates inclusive
        def _count_months_inclusive(start_d: date, end_d: date) -> int:
            if end_d < start_d:
                return 0
            return (end_d.year - start_d.year) * 12 + (end_d.month - start_d.month) + 1

        # Helper: compute overlap window between [a_start, a_end] and [b_start, b_end]
        def _overlap(a_start: date, a_end: date, b_start: date, b_end: date) -> Optional[tuple]:
            start = max(a_start, b_start)
            end = min(a_end, b_end)
            if end < start:
                return None
            return (start, end)

        # Helper: count business days (Mon-Fri) and exclude JP holidays if library is available
        def _count_business_days_inclusive(start_d: date, end_d: date) -> int:
            if end_d < start_d:
                return 0
            try:
                import jpholiday  # type: ignore
            except Exception:
                jpholiday = None  # type: ignore
            count = 0
            d = start_d
            one = timedelta(days=1)
            while d <= end_d:
                if d.weekday() < 5:  # Mon-Fri
                    if jpholiday is None or not jpholiday.is_holiday(d):
                        count += 1
                d += one
            return count

        # Determine calendar window for the requested projection year
        if year == 0:
            year_start = today
            year_end = date(today.year, 12, 31)
        else:
            y = today.year + year
            year_start = date(y, 1, 1)
            year_end = date(y, 12, 31)

        for plan in plans:
            # Plan's active window
            plan_start = plan.start_date
            plan_end = plan.end_date if plan.end_date else year_end  # open-ended treated as year_end for overlap

            window = _overlap(plan_start, plan_end, year_start, year_end)
            if not window:
                continue

            start_w, end_w = window

            if plan.frequency == "MONTHLY":
                months = _count_months_inclusive(start_w.replace(day=1), end_w.replace(day=1))
                total_contributions += plan.amount_jpy * months
            elif plan.frequency == "DAILY":
                days = _count_business_days_inclusive(start_w, end_w)
                total_contributions += plan.amount_jpy * days
            elif plan.frequency == "BONUS_MONTH":
                if plan.bonus_months:
                    if isinstance(plan.bonus_months, str):
                        months_list = [int(m.strip()) for m in plan.bonus_months.split(",") if m.strip()]
                    else:
                        months_list = list(plan.bonus_months)
                    months_in_window = set(range(start_w.month, end_w.month + 1))
                    eligible = [m for m in months_list if m in months_in_window]
                    total_contributions += plan.amount_jpy * len(eligible)

        return total_contributions

    @staticmethod
    def _calculate_nisa_usage_for_year(
        plans: List,
        year: int,
        cumulative_nisa: Dict[str, Decimal],
        base_annual: Optional[Dict[str, Decimal]] = None,
    ) -> Dict[str, Dict[str, Decimal]]:
        """
        Calculate NISA frame usage for a given projection year.

        Args:
            plans: Pre-fetched list of RecurringInvestmentPlan objects
            year: Year index (0-based)
            cumulative_nisa: Dictionary tracking cumulative NISA usage across years
                            {"tsumitate": Decimal, "growth": Decimal}

        Returns:
            Dictionary with NISA usage details:
            {
                "tsumitate": {"used": amount, "remaining": amount, "limit": amount},
                "growth": {"used": amount, "remaining": amount, "limit": amount},
                "total": {"used": amount, "remaining": amount, "limit": amount},
                "lifetime_tsumitate": {"used": amount, "remaining": amount},
                "lifetime_growth": {"used": amount, "remaining": amount, "limit": amount},
                "lifetime_total": {"used": amount, "remaining": amount, "limit": amount}
            }
        """
        from portfolio.models import InvestmentHolding

        today = date.today()

        # Annual contributions for this year (seed with existing current-year usage if provided)
        nisa_tsumitate_annual = (
            Decimal(base_annual.get("tsumitate", 0)) if base_annual else Decimal(0)
        )
        nisa_growth_annual = (
            Decimal(base_annual.get("growth", 0)) if base_annual else Decimal(0)
        )
        base_tsumitate = nisa_tsumitate_annual
        base_growth = nisa_growth_annual
        overflow_general_annual = Decimal(0)

        # Define calendar window for the year
        if year == 0:
            year_start = today
            year_end = date(today.year, 12, 31)
        else:
            y = today.year + year
            year_start = date(y, 1, 1)
            year_end = date(y, 12, 31)

        def _overlap(a_start: date, a_end: date, b_start: date, b_end: date) -> Optional[tuple]:
            start = max(a_start, b_start)
            end = min(a_end, b_end)
            if end < start:
                return None
            return (start, end)

        def _count_business_days_inclusive(start_d: date, end_d: date) -> int:
            if end_d < start_d:
                return 0
            try:
                import jpholiday  # type: ignore
            except Exception:
                jpholiday = None  # type: ignore
            count = 0
            d = start_d
            one = timedelta(days=1)
            while d <= end_d:
                if d.weekday() < 5:
                    if jpholiday is None or not jpholiday.is_holiday(d):
                        count += 1
                d += one
            return count

        for plan in plans:

            # Only count NISA accounts
            if plan.target_account_type not in [
                "NISA_TSUMITATE",
                "NISA_GROWTH",
            ]:
                continue

            # Calculate annual contribution for this plan
            annual_contribution = Decimal(0)
            # Partial/Full year based on overlap with calendar window
            plan_start = plan.start_date
            plan_end = plan.end_date if plan.end_date else year_end
            window = _overlap(plan_start, plan_end, year_start, year_end)
            if not window:
                continue
            start_w, end_w = window
            if plan.frequency == "MONTHLY":
                months = (end_w.year - start_w.year) * 12 + (end_w.month - start_w.month) + 1
                annual_contribution = plan.amount_jpy * months
            elif plan.frequency == "DAILY":
                days = _count_business_days_inclusive(start_w, end_w)
                annual_contribution = plan.amount_jpy * days
            elif plan.frequency == "BONUS_MONTH":
                if plan.bonus_months:
                    if isinstance(plan.bonus_months, str):
                        months_list = [int(m.strip()) for m in plan.bonus_months.split(",") if m.strip()]
                    else:
                        months_list = list(plan.bonus_months)
                    months_in_window = set(range(start_w.month, end_w.month + 1))
                    eligible = [m for m in months_list if m in months_in_window]
                    annual_contribution = plan.amount_jpy * len(eligible)

            # Determine remaining limits before allocation
            annual_total_used = nisa_tsumitate_annual + nisa_growth_annual
            annual_total_remaining = InvestmentHolding.NISA_ANNUAL_LIMIT_TOTAL - annual_total_used
            lifetime_total_used = cumulative_nisa["tsumitate"] + cumulative_nisa["growth"]
            lifetime_total_remaining = InvestmentHolding.NISA_LIFETIME_LIMIT_TOTAL - lifetime_total_used

            if plan.target_account_type == "NISA_TSUMITATE":
                per_frame_remaining = InvestmentHolding.NISA_ANNUAL_LIMIT_TSUMITATE - nisa_tsumitate_annual
                allowed = min(
                    annual_contribution,
                    max(per_frame_remaining, 0),
                    max(annual_total_remaining, 0),
                    max(lifetime_total_remaining, 0),
                )
                allowed = max(allowed, 0)
                nisa_tsumitate_annual += allowed
                overflow_general_annual += max(annual_contribution - allowed, 0)
            elif plan.target_account_type == "NISA_GROWTH":
                per_frame_remaining = InvestmentHolding.NISA_ANNUAL_LIMIT_GROWTH - nisa_growth_annual
                lifetime_growth_remaining = (
                    InvestmentHolding.NISA_LIFETIME_LIMIT_GROWTH - cumulative_nisa["growth"]
                )
                allowed = min(
                    annual_contribution,
                    max(per_frame_remaining, 0),
                    max(annual_total_remaining, 0),
                    max(lifetime_total_remaining, 0),
                    max(lifetime_growth_remaining, 0),
                )
                allowed = max(allowed, 0)
                nisa_growth_annual += allowed
                overflow_general_annual += max(annual_contribution - allowed, 0)

        # Update cumulative NISA usage with only the incremental amounts allocated this year
        incremental_tsumitate = nisa_tsumitate_annual - base_tsumitate
        incremental_growth = nisa_growth_annual - base_growth
        if incremental_tsumitate > 0:
            cumulative_nisa["tsumitate"] += incremental_tsumitate
        if incremental_growth > 0:
            cumulative_nisa["growth"] += incremental_growth

        # Calculate remaining limits
        nisa_total_annual = nisa_tsumitate_annual + nisa_growth_annual

        return {
            "tsumitate": {
                "used": float(nisa_tsumitate_annual),
                "remaining": float(
                    max(InvestmentHolding.NISA_ANNUAL_LIMIT_TSUMITATE - nisa_tsumitate_annual, 0)
                ),
                "limit": float(InvestmentHolding.NISA_ANNUAL_LIMIT_TSUMITATE),
            },
            "growth": {
                "used": float(nisa_growth_annual),
                "remaining": float(
                    max(InvestmentHolding.NISA_ANNUAL_LIMIT_GROWTH - nisa_growth_annual, 0)
                ),
                "limit": float(InvestmentHolding.NISA_ANNUAL_LIMIT_GROWTH),
            },
            "total": {
                "used": float(nisa_total_annual),
                "remaining": float(
                    max(InvestmentHolding.NISA_ANNUAL_LIMIT_TOTAL - nisa_total_annual, 0)
                ),
                "limit": float(InvestmentHolding.NISA_ANNUAL_LIMIT_TOTAL),
            },
            "lifetime_tsumitate": {
                "used": float(cumulative_nisa["tsumitate"]),
                "remaining": float(
                    max(
                        InvestmentHolding.NISA_LIFETIME_LIMIT_TOTAL
                        - cumulative_nisa["tsumitate"],
                        0,
                    )
                ),
            },
            "lifetime_growth": {
                "used": float(cumulative_nisa["growth"]),
                "remaining": float(
                    max(
                        InvestmentHolding.NISA_LIFETIME_LIMIT_GROWTH
                        - cumulative_nisa["growth"],
                        0,
                    )
                ),
                "limit": float(InvestmentHolding.NISA_LIFETIME_LIMIT_GROWTH),
            },
            "lifetime_total": {
                "used": float(
                    cumulative_nisa["tsumitate"] + cumulative_nisa["growth"]
                ),
                "remaining": float(
                    max(
                        InvestmentHolding.NISA_LIFETIME_LIMIT_TOTAL
                        - (cumulative_nisa["tsumitate"] + cumulative_nisa["growth"]),
                        0,
                    )
                ),
                "limit": float(InvestmentHolding.NISA_LIFETIME_LIMIT_TOTAL),
            },
            "overflow_to_general": float(overflow_general_annual),
        }

    @staticmethod
    def _project_future_composition_by_region(
        user: User,
        plans: List,
        projection_years: int,
        rate_decimal: Decimal,
    ) -> Dict[str, Dict]:
        """
        Project future composition by asset region using current holdings per region
        and planned contributions per region over each projection year.

        For each year:
        - Compute contributions per region based on overlap with that calendar year
          (year 0 uses today..12/31; future years use 1/1..12/31)
        - Apply growth uniformly per region: (amount + contributions) * (1 + r)

        Returns mapping: region -> { amount, percentage }
        """
        # Aggregate current holdings by region
        composition_query = (
            InvestmentHolding.objects.filter(user=user)
            .values("asset_region")
            .annotate(current_amount=Sum("current_amount_jpy"))
        )
        region_amounts: Dict[str, Decimal] = {}
        for item in composition_query:
            region = item["asset_region"] or "OTHER"
            region_amounts[region] = Decimal(item["current_amount"] or 0)

        # If no holdings and no plans, return empty
        if not region_amounts and not plans:
            return {}

        today = date.today()

        def _overlap(a_start: date, a_end: date, b_start: date, b_end: date):
            start = max(a_start, b_start)
            end = min(a_end, b_end)
            if end < start:
                return None
            return (start, end)

        def _count_months_inclusive(start_d: date, end_d: date) -> int:
            if end_d < start_d:
                return 0
            return (end_d.year - start_d.year) * 12 + (end_d.month - start_d.month) + 1

        def _count_business_days_inclusive(start_d: date, end_d: date) -> int:
            if end_d < start_d:
                return 0
            try:
                import jpholiday  # type: ignore
            except Exception:
                jpholiday = None  # type: ignore
            count = 0
            d = start_d
            one = timedelta(days=1)
            while d <= end_d:
                if d.weekday() < 5 and (jpholiday is None or not jpholiday.is_holiday(d)):
                    count += 1
                d += one
            return count

        growth_factor = Decimal(1) + rate_decimal

        for year in range(projection_years):
            if year == 0:
                year_start = today
                year_end = date(today.year, 12, 31)
            else:
                y = today.year + year
                year_start = date(y, 1, 1)
                year_end = date(y, 12, 31)

            # Initialize contributions per region for this year
            contrib_by_region: Dict[str, Decimal] = {}

            for plan in plans:
                # Determine overlap with this year's window
                plan_start = plan.start_date
                plan_end = plan.end_date or year_end
                window = _overlap(plan_start, plan_end, year_start, year_end)
                if not window:
                    continue
                start_w, end_w = window

                # Determine amount for this plan during the window
                annual_contribution = Decimal(0)
                if plan.frequency == "MONTHLY":
                    months = _count_months_inclusive(start_w.replace(day=1), end_w.replace(day=1))
                    annual_contribution = plan.amount_jpy * months
                elif plan.frequency == "DAILY":
                    days = _count_business_days_inclusive(start_w, end_w)
                    annual_contribution = plan.amount_jpy * days
                elif plan.frequency == "BONUS_MONTH":
                    if plan.bonus_months:
                        if isinstance(plan.bonus_months, str):
                            months_list = [int(m.strip()) for m in plan.bonus_months.split(",") if m.strip()]
                        else:
                            months_list = list(plan.bonus_months)
                        months_in_window = set(range(start_w.month, end_w.month + 1))
                        eligible = [m for m in months_list if m in months_in_window]
                        annual_contribution = plan.amount_jpy * len(eligible)

                # Attribute to plan's target region
                region = getattr(plan, "target_asset_region", None) or "OTHER"
                contrib_by_region[region] = contrib_by_region.get(region, Decimal(0)) + annual_contribution

            # Apply contributions and growth per region
            # Ensure regions from contributions exist in bucket
            for region, amt in contrib_by_region.items():
                if region not in region_amounts:
                    region_amounts[region] = Decimal(0)

            # Update each region
            for region in list(region_amounts.keys()):
                add = contrib_by_region.get(region, Decimal(0))
                region_amounts[region] = (region_amounts[region] + add) * growth_factor

        # Build final composition map
        total = sum(region_amounts.values()) or Decimal(0)
        if total == 0:
            return {}
        result: Dict[str, Dict] = {}
        for region, amount in region_amounts.items():
            percentage = float((amount / total) * Decimal(100))
            result[region] = {"amount": float(amount), "percentage": percentage}
        return result

    @staticmethod
    def _project_future_composition_by_asset_class(
        user: User,
        plans: List,
        projection_years: int,
        rate_decimal: Decimal,
    ) -> Dict[str, Dict]:
        """
        Project future composition by asset class, mirroring region-based approach.
        Uses current holdings per asset_class plus planned contributions per class each year,
        applying growth uniformly.
        """
        # Aggregate current holdings by asset class
        composition_query = (
            InvestmentHolding.objects.filter(user=user)
            .values("asset_class")
            .annotate(current_amount=Sum("current_amount_jpy"))
        )
        class_amounts: Dict[str, Decimal] = {}
        for item in composition_query:
            cls_key = item["asset_class"] or "OTHER"
            class_amounts[cls_key] = Decimal(item["current_amount"] or 0)

        if not class_amounts and not plans:
            return {}

        today = date.today()

        def _overlap(a_start: date, a_end: date, b_start: date, b_end: date):
            start = max(a_start, b_start)
            end = min(a_end, b_end)
            if end < start:
                return None
            return (start, end)

        def _count_months_inclusive(start_d: date, end_d: date) -> int:
            if end_d < start_d:
                return 0
            return (end_d.year - start_d.year) * 12 + (end_d.month - start_d.month) + 1

        def _count_business_days_inclusive(start_d: date, end_d: date) -> int:
            if end_d < start_d:
                return 0
            try:
                import jpholiday  # type: ignore
            except Exception:
                jpholiday = None  # type: ignore
            count = 0
            d = start_d
            one = timedelta(days=1)
            while d <= end_d:
                if d.weekday() < 5 and (jpholiday is None or not jpholiday.is_holiday(d)):
                    count += 1
                d += one
            return count

        growth_factor = Decimal(1) + rate_decimal

        for year in range(projection_years):
            if year == 0:
                year_start = today
                year_end = date(today.year, 12, 31)
            else:
                y = today.year + year
                year_start = date(y, 1, 1)
                year_end = date(y, 12, 31)

            contrib_by_class: Dict[str, Decimal] = {}

            for plan in plans:
                plan_start = plan.start_date
                plan_end = plan.end_date or year_end
                window = _overlap(plan_start, plan_end, year_start, year_end)
                if not window:
                    continue
                start_w, end_w = window

                annual_contribution = Decimal(0)
                if plan.frequency == "MONTHLY":
                    months = _count_months_inclusive(start_w.replace(day=1), end_w.replace(day=1))
                    annual_contribution = plan.amount_jpy * months
                elif plan.frequency == "DAILY":
                    days = _count_business_days_inclusive(start_w, end_w)
                    annual_contribution = plan.amount_jpy * days
                elif plan.frequency == "BONUS_MONTH":
                    if plan.bonus_months:
                        if isinstance(plan.bonus_months, str):
                            months_list = [int(m.strip()) for m in plan.bonus_months.split(",") if m.strip()]
                        else:
                            months_list = list(plan.bonus_months)
                        months_in_window = set(range(start_w.month, end_w.month + 1))
                        eligible = [m for m in months_list if m in months_in_window]
                        annual_contribution = plan.amount_jpy * len(eligible)

                cls_key = getattr(plan, "target_asset_class", None) or "OTHER"
                contrib_by_class[cls_key] = contrib_by_class.get(cls_key, Decimal(0)) + annual_contribution

            for cls_key, amt in contrib_by_class.items():
                if cls_key not in class_amounts:
                    class_amounts[cls_key] = Decimal(0)

            for cls_key in list(class_amounts.keys()):
                add = contrib_by_class.get(cls_key, Decimal(0))
                class_amounts[cls_key] = (class_amounts[cls_key] + add) * growth_factor

        total = sum(class_amounts.values()) or Decimal(0)
        if total == 0:
            return {}
        result: Dict[str, Dict] = {}
        for cls_key, amount in class_amounts.items():
            percentage = float((amount / total) * Decimal(100))
            result[cls_key] = {"amount": float(amount), "percentage": percentage}
        return result
