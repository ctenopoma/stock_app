from django.http import JsonResponse
from django.urls import include, path
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView

from portfolio.views import (
    InvestmentHoldingViewSet,
    PortfolioSummaryView,
    ProjectionViewSet,
    RecurringInvestmentPlanViewSet,
)

from .schema import urlpatterns as schema_urlpatterns


def health(request):
    return JsonResponse({"status": "ok"})


class PortfolioSummaryAPIView(APIView):
    """Endpoint for portfolio summary: GET /portfolio/summary"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get portfolio summary for authenticated user"""
        summary = PortfolioSummaryView.get_portfolio_summary(request.user)
        return Response(summary)


# Create router and register viewsets
router = DefaultRouter()
# Accept both with and without trailing slash for API routes
router.trailing_slash = "/?"
router.register(r"holdings", InvestmentHoldingViewSet, basename="holding")
router.register(
    r"recurring-plans", RecurringInvestmentPlanViewSet, basename="recurring-plan"
)
router.register(r"projections", ProjectionViewSet, basename="projection")

urlpatterns = [
    path("health/", health, name="health"),
    path("auth/", include("accounts.urls")),
    path(
        "portfolio/summary/",
        PortfolioSummaryAPIView.as_view(),
        name="portfolio-summary",
    ),
    path("", include(router.urls)),
]

# Append schema/docs URLs (drf-spectacular)
urlpatterns += schema_urlpatterns
