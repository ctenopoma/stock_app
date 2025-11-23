"""
Views for Portfolio app
REST endpoints for managing investment holdings, recurring plans, and projections
"""

from django.db.models import Count, Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import InvestmentHolding, Projection, RecurringInvestmentPlan
from .serializers import (
    InvestmentHoldingSerializer,
    ProjectionSerializer,
    RecurringInvestmentPlanSerializer,
)
from .services import ProjectionCalculationService


class InvestmentHoldingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for InvestmentHolding CRUD operations
    Endpoints:
    - GET /holdings - list all holdings (paginated)
    - POST /holdings - create a new holding
    - GET /holdings/{id} - retrieve a specific holding
    - PUT /holdings/{id} - update a holding (full replacement)
    - PATCH /holdings/{id} - partial update a holding
    - DELETE /holdings/{id} - delete a holding
    """

    serializer_class = InvestmentHoldingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return holdings for the authenticated user only"""
        print(
            f"[DEBUG] InvestmentHoldingViewSet: user={self.request.user}, authenticated={self.request.user.is_authenticated}"
        )
        print(
            f"[DEBUG] InvestmentHoldingViewSet: session_key={self.request.session.session_key}"
        )
        print(
            f"[DEBUG] InvestmentHoldingViewSet: cookies={list(self.request.COOKIES.keys())}"
        )
        return InvestmentHolding.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Automatically set the user to the authenticated user"""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Ensure user ownership is maintained"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="nisa-usage")
    def nisa_usage(self, request):
        """Return current year's NISA annual usage and lifetime usage for the user."""
        from django.utils import timezone

        year = timezone.now().year
        annual = InvestmentHolding.get_nisa_usage_by_year(request.user, year)
        lifetime = InvestmentHolding.get_nisa_lifetime_usage(request.user)

        # Convert Decimals to float for JSON serialization
        def to_float_dict(d):
            out = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    out[k] = {kk: float(vv) for kk, vv in v.items()}
                else:
                    out[k] = float(v)
            return out

        return Response({
            "annual": to_float_dict(annual),
            "lifetime": to_float_dict(lifetime),
            "year": year,
        })


class RecurringInvestmentPlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet for RecurringInvestmentPlan CRUD operations
    Endpoints:
    - GET /recurring-plans - list all plans (paginated)
    - POST /recurring-plans - create a new plan
    - GET /recurring-plans/{id} - retrieve a specific plan
    - PUT /recurring-plans/{id} - update a plan (full replacement)
    - PATCH /recurring-plans/{id} - partial update a plan
    - DELETE /recurring-plans/{id} - delete a plan
    """

    serializer_class = RecurringInvestmentPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return plans for the authenticated user only"""
        return RecurringInvestmentPlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Automatically set the user to the authenticated user"""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Ensure user ownership is maintained"""
        serializer.save(user=self.request.user)


class ProjectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Projection CRUD operations
    Endpoints:
    - GET /projections - list all projections (paginated)
    - POST /projections - create a new projection (calls calculate_projection service)
    - GET /projections/{id} - retrieve a specific projection
    """

    serializer_class = ProjectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return projections for the authenticated user only"""
        return Projection.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Automatically set the user to the authenticated user"""
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Override create to use ProjectionCalculationService

        Expected request body:
        {
            "projection_years": 10,
            "annual_return_rate": 4.0
        }
        """
        try:
            projection_years = request.data.get("projection_years")
            annual_return_rate = request.data.get("annual_return_rate")

            # Validate inputs
            if not projection_years or not annual_return_rate:
                return Response(
                    {"error": "projection_years and annual_return_rate are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Call the calculation service with authenticated user
            from decimal import Decimal

            projection = ProjectionCalculationService.calculate_projection(
                user=request.user,
                projection_years=int(projection_years),
                annual_return_rate=Decimal(str(annual_return_rate)),
            )

            serializer = self.get_serializer(projection)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Projection calculation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PortfolioSummaryView:
    """
    View for portfolio summary endpoint
    Returns: composition by region, account type, asset class, and total value
    Note: This is implemented as a custom action in holdings viewset or separate view

    Performance optimizations:
    - Uses database aggregation (values() + annotate) instead of Python loops
    - Single query per composition type (region, account_type, asset_class)
    - Eliminates N+1 query problems present in previous implementation
    """

    @staticmethod
    def get_portfolio_summary(user):
        """
        Calculate portfolio summary from user's holdings using database aggregation.

        Returns dict with total value and composition breakdowns.

        Optimization: Uses Django ORM aggregation instead of Python loops to avoid N+1 queries.
        """

        # Single aggregation query for total value and count
        total_query = InvestmentHolding.objects.filter(user=user).aggregate(
            total_value_jpy=Sum("current_amount_jpy"), holdings_count=Count("id")
        )

        total_value_jpy = float(total_query.get("total_value_jpy") or 0)
        holdings_count = total_query.get("holdings_count") or 0

        # Optimized queries for compositions (single DB query per dimension)
        def get_composition_by_field(field_name):
            """
            Query composition by a specific field using database aggregation.
            Single database query instead of Python loop.
            """
            composition_query = (
                InvestmentHolding.objects.filter(user=user)
                .values(field_name)
                .annotate(amount=Sum("current_amount_jpy"))
            )

            if total_value_jpy == 0:
                return {}

            return {
                item[field_name]: {
                    "amount": float(item["amount"]),
                    "percentage": (float(item["amount"]) / total_value_jpy) * 100,
                }
                for item in composition_query
            }

        return {
            "total_value_jpy": total_value_jpy,
            "holdings_count": holdings_count,
            "composition_by_region": get_composition_by_field("asset_region"),
            "composition_by_account_type": get_composition_by_field("account_type"),
            "composition_by_asset_class": get_composition_by_field("asset_class"),
        }
