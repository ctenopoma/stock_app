# Generated migration for portfolio models (SQLite compatible)

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="InvestmentHolding",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "account_type",
                    models.CharField(
                        choices=[("NISA", "NISA"), ("GENERAL", "General Account")],
                        max_length=20,
                    ),
                ),
                (
                    "asset_class",
                    models.CharField(
                        choices=[
                            ("INDIVIDUAL_STOCK", "Individual Stock"),
                            ("MUTUAL_FUND", "Mutual Fund"),
                            ("CRYPTOCURRENCY", "Cryptocurrency"),
                            ("REIT", "REIT"),
                            ("GOVERNMENT_BOND", "Government Bond"),
                            ("OTHER", "Other"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "asset_region",
                    models.CharField(
                        choices=[
                            ("DOMESTIC_STOCKS", "Domestic Stocks"),
                            ("INTERNATIONAL_STOCKS", "International Stocks"),
                            ("DOMESTIC_BONDS", "Domestic Bonds"),
                            ("INTERNATIONAL_BONDS", "International Bonds"),
                            ("DOMESTIC_REITS", "Domestic REITs"),
                            ("INTERNATIONAL_REITS", "International REITs"),
                            ("CRYPTOCURRENCY", "Cryptocurrency"),
                            ("OTHER", "Other"),
                        ],
                        max_length=30,
                    ),
                ),
                ("asset_identifier", models.CharField(max_length=100)),
                ("asset_name", models.CharField(max_length=200)),
                (
                    "current_amount_jpy",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=20,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("purchase_date", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="holdings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RecurringInvestmentPlan",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "target_account_type",
                    models.CharField(
                        choices=[("NISA", "NISA"), ("GENERAL", "General Account")],
                        max_length=20,
                    ),
                ),
                (
                    "target_asset_class",
                    models.CharField(
                        choices=[
                            ("INDIVIDUAL_STOCK", "Individual Stock"),
                            ("MUTUAL_FUND", "Mutual Fund"),
                            ("CRYPTOCURRENCY", "Cryptocurrency"),
                            ("REIT", "REIT"),
                            ("GOVERNMENT_BOND", "Government Bond"),
                            ("OTHER", "Other"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "target_asset_region",
                    models.CharField(
                        choices=[
                            ("DOMESTIC_STOCKS", "Domestic Stocks"),
                            ("INTERNATIONAL_STOCKS", "International Stocks"),
                            ("DOMESTIC_BONDS", "Domestic Bonds"),
                            ("INTERNATIONAL_BONDS", "International Bonds"),
                            ("DOMESTIC_REITS", "Domestic REITs"),
                            ("INTERNATIONAL_REITS", "International REITs"),
                            ("CRYPTOCURRENCY", "Cryptocurrency"),
                            ("OTHER", "Other"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "frequency",
                    models.CharField(
                        choices=[
                            ("DAILY", "Daily"),
                            ("MONTHLY", "Monthly"),
                            ("BONUS_MONTH", "Bonus Month"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "amount_jpy",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=20,
                        validators=[django.core.validators.MinValueValidator(0.01)],
                    ),
                ),
                ("start_date", models.DateField()),
                ("end_date", models.DateField(blank=True, null=True)),
                (
                    "bonus_months",
                    models.TextField(
                        blank=True,
                        help_text="Comma-separated month numbers (1-12)",
                        null=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="plans",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Projection",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "projection_years",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(50),
                        ]
                    ),
                ),
                (
                    "annual_return_rate",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=6,
                        validators=[
                            django.core.validators.MinValueValidator(-100),
                            django.core.validators.MaxValueValidator(100),
                        ],
                    ),
                ),
                (
                    "starting_balance_jpy",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=20,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "total_accumulated_contributions_jpy",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=20,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "total_interest_gains_jpy",
                    models.DecimalField(decimal_places=2, max_digits=20),
                ),
                (
                    "projected_total_value_jpy",
                    models.DecimalField(decimal_places=2, max_digits=20),
                ),
                (
                    "projected_composition_by_region",
                    models.TextField(
                        default="", help_text="JSON string of region-wise composition"
                    ),
                ),
                (
                    "year_by_year_breakdown",
                    models.TextField(
                        blank=True,
                        help_text="JSON string of year-by-year breakdown",
                        null=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("valid_until", models.DateTimeField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="projections",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="projection",
            index=models.Index(
                fields=["user", "created_at"], name="portfolio_pr_user_id_created_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="recurringinvestmentplan",
            index=models.Index(fields=["user"], name="portfolio_re_user_id_idx"),
        ),
        migrations.AddIndex(
            model_name="investmentholding",
            index=models.Index(
                fields=["user", "asset_region"],
                name="portfolio_in_user_id_asset_region_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="investmentholding",
            index=models.Index(fields=["user"], name="portfolio_in_user_id_idx"),
        ),
        migrations.AddConstraint(
            model_name="investmentholding",
            constraint=models.UniqueConstraint(
                fields=[
                    "user",
                    "account_type",
                    "asset_class",
                    "asset_region",
                    "asset_identifier",
                ],
                name="unique_holding_per_user",
            ),
        ),
    ]
