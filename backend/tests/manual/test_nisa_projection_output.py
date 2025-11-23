"""
Manual test script to verify NISA usage projection output
Run with: python test_nisa_projection_output.py
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from decimal import Decimal
from django.contrib.auth.models import User
from portfolio.models import RecurringInvestmentPlan
from portfolio.services import ProjectionCalculationService
import json

# Get or create test user
user, created = User.objects.get_or_create(
    username="demo_user",
    defaults={"email": "demo@example.com"}
)
if created:
    user.set_password("demo123")
    user.save()

# Clear existing plans for clean test
RecurringInvestmentPlan.objects.filter(user=user).delete()

# Create NISA investment plans
plan1 = RecurringInvestmentPlan.objects.create(
    user=user,
    target_account_type="NISA_TSUMITATE",
    target_asset_class="MUTUAL_FUND",
    target_asset_region="DOMESTIC_STOCKS",
    frequency="MONTHLY",
    amount_jpy=50000,  # 600,000 per year
    start_date="2025-01-01",
)

plan2 = RecurringInvestmentPlan.objects.create(
    user=user,
    target_account_type="NISA_GROWTH",
    target_asset_class="INDIVIDUAL_STOCK",
    target_asset_region="INTERNATIONAL_STOCKS",
    frequency="MONTHLY",
    amount_jpy=100000,  # 1,200,000 per year
    start_date="2025-01-01",
)

# Calculate projection
projection = ProjectionCalculationService.calculate_projection(
    user=user,
    projection_years=3,
    annual_return_rate=Decimal("5.0")
)

# Parse and display year breakdown
year_breakdown = json.loads(projection.year_by_year_breakdown)

print("=" * 80)
print("NISA Usage Projection - Year by Year Breakdown")
print("=" * 80)

for year_data in year_breakdown:
    year = year_data["year"]
    nisa = year_data["nisa_usage"]
    
    print(f"\n【Year {year}】")
    print(f"  Portfolio Balance: ¥{year_data['ending_balance']:,.0f}")
    print(f"  Contributions: ¥{year_data['contributions']:,.0f}")
    print(f"  Interest Earned: ¥{year_data['interest_earned']:,.0f}")
    
    print(f"\n  NISA Annual Usage:")
    print(f"    つみたて投資枠: ¥{nisa['tsumitate']['used']:,.0f} / ¥{nisa['tsumitate']['limit']:,.0f} (残り: ¥{nisa['tsumitate']['remaining']:,.0f})")
    print(f"    成長投資枠:     ¥{nisa['growth']['used']:,.0f} / ¥{nisa['growth']['limit']:,.0f} (残り: ¥{nisa['growth']['remaining']:,.0f})")
    print(f"    年間合計:       ¥{nisa['total']['used']:,.0f} / ¥{nisa['total']['limit']:,.0f} (残り: ¥{nisa['total']['remaining']:,.0f})")
    
    print(f"\n  NISA Lifetime Usage:")
    print(f"    つみたて累計:   ¥{nisa['lifetime_tsumitate']['used']:,.0f} (残り: ¥{nisa['lifetime_tsumitate']['remaining']:,.0f})")
    print(f"    成長累計:       ¥{nisa['lifetime_growth']['used']:,.0f} / ¥{nisa['lifetime_growth']['limit']:,.0f} (残り: ¥{nisa['lifetime_growth']['remaining']:,.0f})")
    print(f"    生涯合計:       ¥{nisa['lifetime_total']['used']:,.0f} / ¥{nisa['lifetime_total']['limit']:,.0f} (残り: ¥{nisa['lifetime_total']['remaining']:,.0f})")

print("\n" + "=" * 80)
print("Summary:")
print(f"  Starting Balance: ¥{projection.starting_balance_jpy:,.0f}")
print(f"  Total Contributions: ¥{projection.total_accumulated_contributions_jpy:,.0f}")
print(f"  Interest Gains: ¥{projection.total_interest_gains_jpy:,.0f}")
print(f"  Projected Total: ¥{projection.projected_total_value_jpy:,.0f}")
print("=" * 80)
