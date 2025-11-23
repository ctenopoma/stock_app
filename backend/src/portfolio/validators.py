"""
Validators for Portfolio app
Custom validation functions for investment data
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_positive_decimal(value: Decimal | float) -> None:
    """Validate that a value is positive (> 0)"""
    if isinstance(value, str):
        value = Decimal(value)
    if value <= 0:
        raise ValidationError(
            _("%(value)s must be positive (greater than 0)"),
            params={"value": value},
        )


def validate_non_negative_decimal(value: Decimal | float) -> None:
    """Validate that a value is non-negative (>= 0)"""
    if isinstance(value, str):
        value = Decimal(value)
    if value < 0:
        raise ValidationError(
            _("%(value)s must be non-negative"),
            params={"value": value},
        )


def validate_asset_identifier(value: str) -> None:
    """Validate asset identifier format"""
    if not value or not value.strip():
        raise ValidationError(_("Asset identifier cannot be empty"))

    if len(value) > 100:
        raise ValidationError(_("Asset identifier must be 100 characters or less"))


def validate_asset_name(value: str) -> None:
    """Validate asset name format"""
    if not value or not value.strip():
        raise ValidationError(_("Asset name cannot be empty"))

    if len(value) > 200:
        raise ValidationError(_("Asset name must be 200 characters or less"))


def validate_bonus_months(value: str) -> None:
    """Validate bonus months for recurring plans"""
    if not value or not value.strip():
        return  # Empty is allowed (handled by model)

    try:
        months = [int(m.strip()) for m in value.split(",")]
        for month in months:
            if not (1 <= month <= 12):
                raise ValidationError(
                    _("Bonus months must be between 1 and 12, got %(value)d"),
                    params={"value": month},
                )
    except ValueError as e:
        raise ValidationError(
            _("Bonus months must be comma-separated integers"),
        ) from e


def validate_return_rate(value: Decimal | float) -> None:
    """Validate annual return rate (-100 to 100)"""
    if isinstance(value, str):
        value = Decimal(value)

    if value < -100 or value > 100:
        raise ValidationError(
            _("Annual return rate must be between -100 and 100 percent, got %(value)s"),
            params={"value": value},
        )


def validate_projection_years(value: int) -> None:
    """Validate projection years (1-50)"""
    if not (1 <= value <= 50):
        raise ValidationError(
            _("Projection years must be between 1 and 50, got %(value)d"),
            params={"value": value},
        )
