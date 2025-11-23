from __future__ import annotations

from decimal import Decimal
from typing import Dict

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class InvestmentHolding(models.Model):
    """Investment holding model with NISA limit constants"""

    # NISA 2024+ investment limits (JPY)
    NISA_ANNUAL_LIMIT_TSUMITATE = Decimal("1200000")  # 120万円/年
    NISA_ANNUAL_LIMIT_GROWTH = Decimal("2400000")  # 240万円/年
    NISA_ANNUAL_LIMIT_TOTAL = Decimal("3600000")  # 360万円/年（合計）
    NISA_LIFETIME_LIMIT_TOTAL = Decimal("18000000")  # 1,800万円（生涯総額）
    NISA_LIFETIME_LIMIT_GROWTH = Decimal("12000000")  # 1,200万円（成長枠の生涯上限）

    class AccountType(models.TextChoices):
        NISA_TSUMITATE = "NISA_TSUMITATE", "NISA (つみたて投資枠)"
        NISA_GROWTH = "NISA_GROWTH", "NISA (成長投資枠)"
        GENERAL = "GENERAL", "General Account"

    class AssetClass(models.TextChoices):
        INDIVIDUAL_STOCK = "INDIVIDUAL_STOCK", "Individual Stock"
        MUTUAL_FUND = "MUTUAL_FUND", "Mutual Fund"
        CRYPTOCURRENCY = "CRYPTOCURRENCY", "Cryptocurrency"
        REIT = "REIT", "REIT"
        GOVERNMENT_BOND = "GOVERNMENT_BOND", "Government Bond"
        OTHER = "OTHER", "Other"

    class AssetRegion(models.TextChoices):
        DOMESTIC_STOCKS = "DOMESTIC_STOCKS", "Domestic Stocks"
        INTERNATIONAL_STOCKS = "INTERNATIONAL_STOCKS", "International Stocks"
        DOMESTIC_BONDS = "DOMESTIC_BONDS", "Domestic Bonds"
        INTERNATIONAL_BONDS = "INTERNATIONAL_BONDS", "International Bonds"
        DOMESTIC_REITS = "DOMESTIC_REITS", "Domestic REITs"
        INTERNATIONAL_REITS = "INTERNATIONAL_REITS", "International REITs"
        CRYPTOCURRENCY = "CRYPTOCURRENCY", "Cryptocurrency"
        OTHER = "OTHER", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="holdings"
    )
    account_type = models.CharField(max_length=20, choices=AccountType.choices)
    asset_class = models.CharField(max_length=30, choices=AssetClass.choices)
    asset_region = models.CharField(max_length=30, choices=AssetRegion.choices)
    asset_identifier = models.CharField(max_length=100)
    asset_name = models.CharField(max_length=200)
    current_amount_jpy = models.DecimalField(
        max_digits=20, decimal_places=2, validators=[MinValueValidator(0)]
    )
    purchase_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "asset_region"]),
            models.Index(fields=["user"]),
        ]
        unique_together = (
            "user",
            "account_type",
            "asset_class",
            "asset_region",
            "asset_identifier",
        )

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"{self.asset_name} ({self.asset_identifier}) - {self.user}"

    @classmethod
    def get_nisa_usage_by_year(
        cls, user, year: int = None
    ) -> Dict[str, Dict[str, Decimal]]:
        """Calculate NISA usage for a specific year or current year.

        Returns:
            Dict with 'tsumitate' and 'growth' keys, each containing
            'amount' (total invested) and 'remaining' (available quota)
        """
        from django.db.models import Q, Sum

        if year is None:
            year = timezone.now().year

        # Filter holdings by year (using purchase_date or created_at)
        year_filter = Q(purchase_date__year=year) | (
            Q(purchase_date__isnull=True) & Q(created_at__year=year)
        )

        tsumitate_total = (
            cls.objects.filter(
                user=user, account_type=cls.AccountType.NISA_TSUMITATE
            )
            .filter(year_filter)
            .aggregate(total=Sum("current_amount_jpy"))["total"]
            or Decimal("0")
        )

        growth_total = (
            cls.objects.filter(user=user, account_type=cls.AccountType.NISA_GROWTH)
            .filter(year_filter)
            .aggregate(total=Sum("current_amount_jpy"))["total"]
            or Decimal("0")
        )

        return {
            "tsumitate": {
                "amount": tsumitate_total,
                "remaining": cls.NISA_ANNUAL_LIMIT_TSUMITATE - tsumitate_total,
            },
            "growth": {
                "amount": growth_total,
                "remaining": cls.NISA_ANNUAL_LIMIT_GROWTH - growth_total,
            },
            "total": {
                "amount": tsumitate_total + growth_total,
                "remaining": cls.NISA_ANNUAL_LIMIT_TOTAL
                - (tsumitate_total + growth_total),
            },
        }

    @classmethod
    def get_nisa_lifetime_usage(cls, user) -> Dict[str, Dict[str, Decimal]]:
        """Calculate lifetime NISA usage across all years.

        Returns:
            Dict with 'tsumitate', 'growth', and 'total' usage information
        """
        from django.db.models import Sum

        tsumitate_total = (
            cls.objects.filter(
                user=user, account_type=cls.AccountType.NISA_TSUMITATE
            ).aggregate(total=Sum("current_amount_jpy"))["total"]
            or Decimal("0")
        )

        growth_total = (
            cls.objects.filter(user=user, account_type=cls.AccountType.NISA_GROWTH)
            .aggregate(total=Sum("current_amount_jpy"))["total"]
            or Decimal("0")
        )

        total_nisa = tsumitate_total + growth_total

        return {
            "tsumitate": {
                "amount": tsumitate_total,
                "remaining": cls.NISA_LIFETIME_LIMIT_TOTAL - total_nisa,
            },
            "growth": {
                "amount": growth_total,
                "remaining": cls.NISA_LIFETIME_LIMIT_GROWTH - growth_total,
            },
            "total": {
                "amount": total_nisa,
                "remaining": cls.NISA_LIFETIME_LIMIT_TOTAL - total_nisa,
            },
        }


class RecurringInvestmentPlan(models.Model):
    class Frequency(models.TextChoices):
        DAILY = "DAILY", "Daily"
        MONTHLY = "MONTHLY", "Monthly"
        BONUS_MONTH = "BONUS_MONTH", "Bonus Month"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="plans"
    )
    target_account_type = models.CharField(
        max_length=20, choices=InvestmentHolding.AccountType.choices
    )
    target_asset_class = models.CharField(
        max_length=30, choices=InvestmentHolding.AssetClass.choices
    )
    target_asset_region = models.CharField(
        max_length=30, choices=InvestmentHolding.AssetRegion.choices
    )
    # Optional descriptive fields for the planned instrument
    target_asset_identifier = models.CharField(max_length=100, blank=True, default="")
    target_asset_name = models.CharField(max_length=200, blank=True, default="")
    frequency = models.CharField(max_length=20, choices=Frequency.choices)
    amount_jpy = models.DecimalField(
        max_digits=20, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    bonus_months = models.TextField(
        null=True, blank=True, help_text="Comma-separated month numbers (1-12)"
    )
    continue_if_limit_exceeded = models.BooleanField(
        default=False,
        help_text="If True, continue investing even after exceeding NISA limits (will use general account)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["user"])]

    def clean(self):
        # Basic validation: start_date <= end_date
        if self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date must be <= end_date")
        # If BONUS_MONTH, ensure bonus_months present and valid
        if self.frequency == self.Frequency.BONUS_MONTH:
            if not self.bonus_months:
                raise ValueError(
                    "bonus_months must be provided for BONUS_MONTH frequency"
                )
            for m in self.bonus_months:
                if not (1 <= int(m) <= 12):
                    raise ValueError(
                        "bonus_months must contain integers between 1 and 12"
                    )

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"Plan {self.id} for {self.user} - {self.amount_jpy} {self.frequency}"


class Projection(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projections"
    )
    projection_years = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    annual_return_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(-100), MaxValueValidator(100)],
    )
    starting_balance_jpy = models.DecimalField(
        max_digits=20, decimal_places=2, validators=[MinValueValidator(0)]
    )
    total_accumulated_contributions_jpy = models.DecimalField(
        max_digits=20, decimal_places=2, validators=[MinValueValidator(0)]
    )
    total_interest_gains_jpy = models.DecimalField(max_digits=20, decimal_places=2)
    projected_total_value_jpy = models.DecimalField(max_digits=20, decimal_places=2)
    projected_composition_by_region = models.TextField(
        default="", help_text="JSON string of region-wise composition"
    )
    projected_composition_by_asset_class = models.TextField(
        default="", help_text="JSON string of asset-class-wise composition"
    )
    year_by_year_breakdown = models.TextField(
        null=True, blank=True, help_text="JSON string of year-by-year breakdown"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["user", "created_at"])]

    def mark_stale_after(self, hours: int = 1) -> None:
        self.valid_until = timezone.now() + timezone.timedelta(hours=hours)
        self.save(update_fields=["valid_until"])

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"Projection {self.id} for {self.user} - {self.projection_years}y @ {self.annual_return_rate}%"
