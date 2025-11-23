"""
Serializers for Portfolio app models
Handles validation and serialization of model data for API responses
"""

from django.utils import timezone
from rest_framework import serializers

from .models import InvestmentHolding, Projection, RecurringInvestmentPlan


class InvestmentHoldingSerializer(serializers.ModelSerializer):
    """Serializer for InvestmentHolding model"""

    class Meta:
        model = InvestmentHolding
        fields = [
            "id",
            "user",
            "account_type",
            "asset_class",
            "asset_region",
            "asset_identifier",
            "asset_name",
            "current_amount_jpy",
            "purchase_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def to_internal_value(self, data):
        """Apply backward compatibility for 'NISA' before Meta validation."""
        if data.get("account_type") == "NISA":
            data = data.copy()
            data["account_type"] = InvestmentHolding.AccountType.NISA_TSUMITATE
        return super().to_internal_value(data)

    def validate_account_type(self, value: str) -> str:
        """Backward compatibility: accept 'NISA' and map to NISA_TSUMITATE."""
        if value == "NISA":
            return InvestmentHolding.AccountType.NISA_TSUMITATE
        return value

    def validate(self, data):
        """Validate NISA investment limits (annual and lifetime)."""
        from decimal import Decimal

        account_type = data.get("account_type")
        amount = Decimal(str(data.get("current_amount_jpy", 0)))
        user = self.context["request"].user

        # Only validate NISA accounts
        if account_type not in [
            InvestmentHolding.AccountType.NISA_TSUMITATE,
            InvestmentHolding.AccountType.NISA_GROWTH,
        ]:
            return data

        # Get purchase year (use current year if not provided)
        purchase_date = data.get("purchase_date")
        year = (
            purchase_date.year
            if purchase_date
            else timezone.now().year
        )

        # Check annual limits
        annual_usage = InvestmentHolding.get_nisa_usage_by_year(user, year)

        if account_type == InvestmentHolding.AccountType.NISA_TSUMITATE:
            if amount > annual_usage["tsumitate"]["remaining"]:
                raise serializers.ValidationError(
                    f"つみたて投資枠の年間上限（{InvestmentHolding.NISA_ANNUAL_LIMIT_TSUMITATE:,.0f}円）を超過します。"
                    f"残り枠: {annual_usage['tsumitate']['remaining']:,.0f}円"
                )
        elif account_type == InvestmentHolding.AccountType.NISA_GROWTH:
            if amount > annual_usage["growth"]["remaining"]:
                raise serializers.ValidationError(
                    f"成長投資枠の年間上限（{InvestmentHolding.NISA_ANNUAL_LIMIT_GROWTH:,.0f}円）を超過します。"
                    f"残り枠: {annual_usage['growth']['remaining']:,.0f}円"
                )

        # Check total annual limit
        if amount > annual_usage["total"]["remaining"]:
            raise serializers.ValidationError(
                f"NISA年間合計上限（{InvestmentHolding.NISA_ANNUAL_LIMIT_TOTAL:,.0f}円）を超過します。"
                f"残り枠: {annual_usage['total']['remaining']:,.0f}円"
            )

        # Check lifetime limits
        lifetime_usage = InvestmentHolding.get_nisa_lifetime_usage(user)

        if account_type == InvestmentHolding.AccountType.NISA_GROWTH:
            if amount > lifetime_usage["growth"]["remaining"]:
                raise serializers.ValidationError(
                    f"成長投資枠の生涯上限（{InvestmentHolding.NISA_LIFETIME_LIMIT_GROWTH:,.0f}円）を超過します。"
                    f"残り枠: {lifetime_usage['growth']['remaining']:,.0f}円"
                )

        # Check total lifetime limit
        if amount > lifetime_usage["total"]["remaining"]:
            raise serializers.ValidationError(
                f"NISA生涯上限（{InvestmentHolding.NISA_LIFETIME_LIMIT_TOTAL:,.0f}円）を超過します。"
                f"残り枠: {lifetime_usage['total']['remaining']:,.0f}円"
            )

        return data

    def create(self, validated_data):
        """Override create to set the user from request context"""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class RecurringInvestmentPlanSerializer(serializers.ModelSerializer):
    """Serializer for RecurringInvestmentPlan model"""

    bonus_months = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Comma-separated month numbers (1-12) for BONUS_MONTH frequency",
    )

    class Meta:
        model = RecurringInvestmentPlan
        fields = [
            "id",
            "user",
            "target_account_type",
            "target_asset_class",
            "target_asset_region",
            "target_asset_identifier",
            "target_asset_name",
            "frequency",
            "amount_jpy",
            "start_date",
            "end_date",
            "bonus_months",
            "continue_if_limit_exceeded",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def to_internal_value(self, data):
        """Apply backward compatibility for 'NISA' before Meta validation."""
        if data.get("target_account_type") == "NISA":
            data = data.copy()
            data["target_account_type"] = InvestmentHolding.AccountType.NISA_TSUMITATE
        return super().to_internal_value(data)

    def validate(self, data):
        """Validate bonus_months and NISA annual limits for plans."""
        from decimal import Decimal

        from django.utils import timezone

        frequency = data.get("frequency")
        bonus_months = data.get("bonus_months")

        if frequency == RecurringInvestmentPlan.Frequency.BONUS_MONTH:
            if not bonus_months:
                raise serializers.ValidationError(
                    "bonus_months must be provided for BONUS_MONTH frequency"
                )
            try:
                months = [int(m.strip()) for m in bonus_months.split(",")]
                for month in months:
                    if not (1 <= month <= 12):
                        raise serializers.ValidationError(
                            "bonus_months must contain integers between 1 and 12"
                        )
            except ValueError:
                raise serializers.ValidationError(
                    "bonus_months must be comma-separated integers"
                )

        # Validate NISA annual limits for recurring plans
        target_account_type = data.get("target_account_type")
        amount_jpy = Decimal(str(data.get("amount_jpy", 0)))
        continue_if_limit_exceeded = data.get("continue_if_limit_exceeded", False)

        if target_account_type in [
            InvestmentHolding.AccountType.NISA_TSUMITATE,
            InvestmentHolding.AccountType.NISA_GROWTH,
        ]:
            # Calculate annual contribution based on frequency
            annual_contribution = Decimal("0")
            if frequency == RecurringInvestmentPlan.Frequency.DAILY:
                annual_contribution = amount_jpy * 365
            elif frequency == RecurringInvestmentPlan.Frequency.MONTHLY:
                annual_contribution = amount_jpy * 12
            elif frequency == RecurringInvestmentPlan.Frequency.BONUS_MONTH:
                if bonus_months:
                    month_count = len(bonus_months.split(","))
                    annual_contribution = amount_jpy * month_count

            # Only enforce strict limit check if continue_if_limit_exceeded is False
            if not continue_if_limit_exceeded:
                # Check annual limit for the plan
                if target_account_type == InvestmentHolding.AccountType.NISA_TSUMITATE:
                    if annual_contribution > InvestmentHolding.NISA_ANNUAL_LIMIT_TSUMITATE:
                        raise serializers.ValidationError(
                            f"つみたて投資枠の年間上限（{InvestmentHolding.NISA_ANNUAL_LIMIT_TSUMITATE:,.0f}円）を超える投資計画です。"
                            f"計画の年間投資額: {annual_contribution:,.0f}円。"
                            f"上限超過後も投資を継続する場合は、'continue_if_limit_exceeded'をTrueに設定してください。"
                        )
                elif target_account_type == InvestmentHolding.AccountType.NISA_GROWTH:
                    if annual_contribution > InvestmentHolding.NISA_ANNUAL_LIMIT_GROWTH:
                        raise serializers.ValidationError(
                            f"成長投資枠の年間上限（{InvestmentHolding.NISA_ANNUAL_LIMIT_GROWTH:,.0f}円）を超える投資計画です。"
                            f"計画の年間投資額: {annual_contribution:,.0f}円。"
                            f"上限超過後も投資を継続する場合は、'continue_if_limit_exceeded'をTrueに設定してください。"
                        )

                # Check total annual limit
                if annual_contribution > InvestmentHolding.NISA_ANNUAL_LIMIT_TOTAL:
                    raise serializers.ValidationError(
                        f"NISA年間合計上限（{InvestmentHolding.NISA_ANNUAL_LIMIT_TOTAL:,.0f}円）を超える投資計画です。"
                        f"計画の年間投資額: {annual_contribution:,.0f}円。"
                        f"上限超過後も投資を継続する場合は、'continue_if_limit_exceeded'をTrueに設定してください。"
                    )

        return data

    def create(self, validated_data):
        """Override create to set the user from request context"""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ProjectionSerializer(serializers.ModelSerializer):
    """Serializer for Projection model"""

    projected_composition_by_region = serializers.CharField(
        help_text="JSON string of region-wise composition"
    )
    projected_composition_by_asset_class = serializers.CharField(
        help_text="JSON string of asset-class-wise composition"
    )
    year_by_year_breakdown = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="JSON string of year-by-year breakdown",
    )

    class Meta:
        model = Projection
        fields = [
            "id",
            "user",
            "projection_years",
            "annual_return_rate",
            "starting_balance_jpy",
            "total_accumulated_contributions_jpy",
            "total_interest_gains_jpy",
            "projected_total_value_jpy",
            "projected_composition_by_region",
            "projected_composition_by_asset_class",
            "year_by_year_breakdown",
            "created_at",
            "valid_until",
        ]
        read_only_fields = ["id", "user", "created_at", "valid_until"]

    def create(self, validated_data):
        """Override create to set the user from request context"""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
