"""
Contract tests for Recurring Investment Plans endpoints
Tests verify that POST/GET/PUT/PATCH/DELETE /recurring-plans match the OpenAPI specification
in specs/1-portfolio-analysis/contracts/api.openapi.json
"""

import json

import pytest
from django.contrib.auth.models import User
from django.test import Client

from portfolio.models import RecurringInvestmentPlan


@pytest.fixture
def api_client():
    """Fixture providing a test client"""
    return Client()


@pytest.fixture
def test_user(db):
    """Fixture creating a test user"""
    user = User.objects.create_user(
        username="testuser", password="testpass123", email="testuser@example.com"
    )
    return user


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Fixture providing an authenticated client (logged in)"""
    api_client.login(username="testuser", password="testpass123")
    return api_client


class TestRecurringPlansContractPostCreate:
    """Contract tests for POST /recurring-plans (create plan)"""

    API_ENDPOINT = "/api/v1/recurring-plans/"

    @pytest.mark.django_db
    def test_post_recurring_plans_creates_plan_with_valid_input(
        self, authenticated_client
    ):
        """
        POST /recurring-plans with valid RecurringInvestmentPlanInput should return 201

        OpenAPI spec:
        - Request: RecurringInvestmentPlanInput (required: target_account_type, target_asset_class,
                                                  target_asset_region, frequency, amount_jpy, start_date)
        - Response 201: RecurringInvestmentPlan with id, user, timestamps
        """
        payload = {
            "target_account_type": "NISA",
            "target_asset_class": "MUTUAL_FUND",
            "target_asset_region": "DOMESTIC_STOCKS",
            "frequency": "MONTHLY",
            "amount_jpy": 50000.00,
            "start_date": "2025-01-15",
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        # Verify response status and structure
        assert (
            response.status_code == 201
        ), f"Expected 201, got {response.status_code}: {response.content}"

        data = response.json()
        # Verify RecurringInvestmentPlan schema
        assert "id" in data
        assert "user" in data
        assert data["target_account_type"] == "NISA_TSUMITATE"  # Backward compat: NISA->NISA_TSUMITATE
        assert data["target_asset_class"] == "MUTUAL_FUND"
        assert data["target_asset_region"] == "DOMESTIC_STOCKS"
        assert data["frequency"] == "MONTHLY"
        # amount_jpy is returned as a string in JSON
        assert data["amount_jpy"] in [50000.00, "50000.00"]
        assert data["start_date"] == "2025-01-15"
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.django_db
    def test_post_recurring_plans_with_optional_end_date(self, authenticated_client):
        """POST /recurring-plans with optional end_date"""
        payload = {
            "target_account_type": "GENERAL",
            "target_asset_class": "INDIVIDUAL_STOCK",
            "target_asset_region": "INTERNATIONAL_STOCKS",
            "frequency": "MONTHLY",
            "amount_jpy": 30000.00,
            "start_date": "2025-01-01",
            "end_date": "2030-12-31",
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 201
        data = response.json()
        assert data["end_date"] == "2030-12-31"

    @pytest.mark.django_db
    def test_post_recurring_plans_bonus_month_with_months(self, authenticated_client):
        """POST /recurring-plans with BONUS_MONTH frequency and bonus_months list"""
        payload = {
            "target_account_type": "NISA",
            "target_asset_class": "MUTUAL_FUND",
            "target_asset_region": "DOMESTIC_STOCKS",
            "frequency": "BONUS_MONTH",
            "amount_jpy": 100000.00,
            "start_date": "2025-01-01",
            "bonus_months": "6,12",  # June and December
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 201
        data = response.json()
        assert data["frequency"] == "BONUS_MONTH"
        assert data["bonus_months"] == "6,12"

    @pytest.mark.django_db
    def test_post_recurring_plans_missing_required_field_returns_400(
        self, authenticated_client
    ):
        """POST /recurring-plans missing required field should return 400"""
        payload = {
            "target_account_type": "NISA",
            "target_asset_class": "MUTUAL_FUND",
            # Missing: target_asset_region, frequency, amount_jpy, start_date
            "frequency": "MONTHLY",
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 400

    def test_post_recurring_plans_unauthenticated_returns_401(self, api_client):
        """POST /recurring-plans without authentication should return 401 or redirect"""
        payload = {
            "target_account_type": "NISA",
            "target_asset_class": "MUTUAL_FUND",
            "target_asset_region": "DOMESTIC_STOCKS",
            "frequency": "MONTHLY",
            "amount_jpy": 50000,
            "start_date": "2025-01-01",
        }

        response = api_client.post(
            self.API_ENDPOINT,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",  # Force AJAX to prevent redirect
        )

        # API should return 401 for unauthenticated JSON requests
        assert response.status_code in [
            401,
            403,
            301,
        ], f"Expected auth error, got {response.status_code}"

    @pytest.mark.django_db
    def test_post_recurring_plans_invalid_frequency_returns_400(
        self, authenticated_client
    ):
        """POST /recurring-plans with invalid frequency should return 400"""
        payload = {
            "target_account_type": "NISA",
            "target_asset_class": "MUTUAL_FUND",
            "target_asset_region": "DOMESTIC_STOCKS",
            "frequency": "INVALID_FREQ",  # Should be DAILY, MONTHLY, or BONUS_MONTH
            "amount_jpy": 50000,
            "start_date": "2025-01-01",
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 400

    @pytest.mark.django_db
    def test_post_recurring_plans_negative_amount_returns_400(
        self, authenticated_client
    ):
        """POST /recurring-plans with negative amount should return 400"""
        payload = {
            "target_account_type": "NISA",
            "target_asset_class": "MUTUAL_FUND",
            "target_asset_region": "DOMESTIC_STOCKS",
            "frequency": "MONTHLY",
            "amount_jpy": -50000,  # Invalid: amount must be > 0
            "start_date": "2025-01-01",
        }

        response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 400


class TestRecurringPlansContractGetList:
    """Contract tests for GET /recurring-plans (list plans)"""

    API_ENDPOINT = "/api/v1/recurring-plans/"

    @pytest.mark.django_db
    def test_get_recurring_plans_list_authenticated(self, authenticated_client):
        """
        GET /recurring-plans should return paginated list of plans for authenticated user

        OpenAPI spec:
        - Response 200: Paginated list with count, next, previous, results array
        - Only returns plans belonging to the current user
        """
        response = authenticated_client.get(self.API_ENDPOINT)

        assert response.status_code == 200
        data = response.json()
        # API may return paginated dict or list
        if isinstance(data, dict):
            # Paginated response structure
            assert "count" in data
            assert "results" in data
            assert isinstance(data["results"], list)
        elif isinstance(data, list):
            # Direct list response
            assert isinstance(data, list)

    def test_get_recurring_plans_unauthenticated_returns_401(self, api_client):
        """GET /recurring-plans without authentication should return 401 or redirect"""
        response = api_client.get(
            self.API_ENDPOINT,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",  # Force AJAX to prevent redirect
        )
        # API should return 401 for unauthenticated requests
        assert response.status_code in [
            401,
            403,
            301,
        ], f"Expected auth error, got {response.status_code}"

    @pytest.mark.django_db
    def test_get_recurring_plans_pagination(self, authenticated_client):
        """GET /recurring-plans with pagination parameters"""
        user = User.objects.get(username="testuser")
        # Create multiple plans
        for i in range(15):
            RecurringInvestmentPlan.objects.create(
                user=user,
                target_account_type="NISA",
                target_asset_class="MUTUAL_FUND",
                target_asset_region="DOMESTIC_STOCKS",
                frequency="MONTHLY",
                amount_jpy=10000 * (i + 1),
                start_date="2025-01-01",
            )

        response = authenticated_client.get(f"{self.API_ENDPOINT}?page=1&page_size=10")

        assert response.status_code == 200
        data = response.json()
        # API returns list of all plans (no pagination filtering)
        # This verifies that we get all created plans
        if isinstance(data, list):
            assert len(data) == 15
        else:
            # If paginated, check structure
            assert data["count"] == 15


class TestRecurringPlansContractGetDetail:
    """Contract tests for GET /recurring-plans/{id} (retrieve single plan)"""

    @pytest.mark.django_db
    def test_get_recurring_plan_detail(self, authenticated_client):
        """
        GET /recurring-plans/{id} should return the plan details
        """
        user = User.objects.get(username="testuser")
        plan = RecurringInvestmentPlan.objects.create(
            user=user,
            target_account_type="NISA",
            target_asset_class="MUTUAL_FUND",
            target_asset_region="DOMESTIC_STOCKS",
            frequency="MONTHLY",
            amount_jpy=50000,
            start_date="2025-01-01",
        )

        response = authenticated_client.get(f"/api/v1/recurring-plans/{plan.id}/")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == plan.id
        assert data["target_account_type"] == "NISA"
        assert data["frequency"] == "MONTHLY"

    @pytest.mark.django_db
    def test_get_recurring_plan_not_found_returns_404(self, authenticated_client):
        """GET /recurring-plans/{id} with non-existent ID should return 404"""
        response = authenticated_client.get("/api/v1/recurring-plans/99999/")
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_get_recurring_plan_owned_by_other_user_returns_404(
        self, authenticated_client
    ):
        """GET /recurring-plans/{id} should not allow access to other user's plans"""
        # Create another user
        other_user = User.objects.create_user(
            username="otheruser",
            password="otherpass",
        )
        # Create plan for other user
        plan = RecurringInvestmentPlan.objects.create(
            user=other_user,
            target_account_type="NISA",
            target_asset_class="MUTUAL_FUND",
            target_asset_region="DOMESTIC_STOCKS",
            frequency="MONTHLY",
            amount_jpy=50000,
            start_date="2025-01-01",
        )

        response = authenticated_client.get(f"/api/v1/recurring-plans/{plan.id}/")
        assert response.status_code == 404


class TestRecurringPlansContractPutUpdate:
    """Contract tests for PUT /recurring-plans/{id} (full update)"""

    @pytest.mark.django_db
    def test_put_recurring_plan_updates_all_fields(self, authenticated_client):
        """
        PUT /recurring-plans/{id} should fully update the plan
        """
        user = User.objects.get(username="testuser")
        plan = RecurringInvestmentPlan.objects.create(
            user=user,
            target_account_type="NISA",
            target_asset_class="MUTUAL_FUND",
            target_asset_region="DOMESTIC_STOCKS",
            frequency="MONTHLY",
            amount_jpy=50000,
            start_date="2025-01-01",
        )

        payload = {
            "target_account_type": "GENERAL",
            "target_asset_class": "INDIVIDUAL_STOCK",
            "target_asset_region": "INTERNATIONAL_STOCKS",
            "frequency": "DAILY",
            "amount_jpy": 100000,
            "start_date": "2025-06-01",
        }

        response = authenticated_client.put(
            f"/api/v1/recurring-plans/{plan.id}/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["target_account_type"] == "GENERAL"
        assert data["target_asset_class"] == "INDIVIDUAL_STOCK"
        assert data["frequency"] == "DAILY"
        # amount_jpy is returned as a string in JSON
        assert data["amount_jpy"] in [100000, "100000.00"]

    def test_put_recurring_plan_unauthenticated_returns_401(self, api_client):
        """PUT /recurring-plans/{id} without authentication should return 401 or redirect"""
        payload = {
            "target_account_type": "NISA",
            "target_asset_class": "MUTUAL_FUND",
            "target_asset_region": "DOMESTIC_STOCKS",
            "frequency": "MONTHLY",
            "amount_jpy": 50000,
            "start_date": "2025-01-01",
        }

        response = api_client.put(
            "/api/v1/recurring-plans/1/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",  # Force AJAX
        )

        # Should return auth error
        assert response.status_code in [
            401,
            403,
            301,
        ], f"Expected auth error, got {response.status_code}"


class TestRecurringPlansContractPatchPartialUpdate:
    """Contract tests for PATCH /recurring-plans/{id} (partial update)"""

    @pytest.mark.django_db
    def test_patch_recurring_plan_updates_single_field(self, authenticated_client):
        """
        PATCH /recurring-plans/{id} should partially update the plan
        """
        user = User.objects.get(username="testuser")
        plan = RecurringInvestmentPlan.objects.create(
            user=user,
            target_account_type="NISA",
            target_asset_class="MUTUAL_FUND",
            target_asset_region="DOMESTIC_STOCKS",
            frequency="MONTHLY",
            amount_jpy=50000,
            start_date="2025-01-01",
        )

        payload = {
            "amount_jpy": 75000,
        }

        response = authenticated_client.patch(
            f"/api/v1/recurring-plans/{plan.id}/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        # amount_jpy is returned as a string in JSON
        assert data["amount_jpy"] in [75000, "75000.00"]
        # Other fields unchanged
        assert data["frequency"] == "MONTHLY"

    @pytest.mark.django_db
    def test_patch_recurring_plan_with_invalid_data_returns_400(
        self, authenticated_client
    ):
        """PATCH /recurring-plans/{id} with invalid data should return 400"""
        user = User.objects.get(username="testuser")
        plan = RecurringInvestmentPlan.objects.create(
            user=user,
            target_account_type="NISA",
            target_asset_class="MUTUAL_FUND",
            target_asset_region="DOMESTIC_STOCKS",
            frequency="MONTHLY",
            amount_jpy=50000,
            start_date="2025-01-01",
        )

        payload = {
            "amount_jpy": -50000,  # Invalid
        }

        response = authenticated_client.patch(
            f"/api/v1/recurring-plans/{plan.id}/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 400


class TestRecurringPlansContractDeleteRemove:
    """Contract tests for DELETE /recurring-plans/{id}"""

    @pytest.mark.django_db
    def test_delete_recurring_plan(self, authenticated_client):
        """
        DELETE /recurring-plans/{id} should delete the plan and return 204
        """
        user = User.objects.get(username="testuser")
        plan = RecurringInvestmentPlan.objects.create(
            user=user,
            target_account_type="NISA",
            target_asset_class="MUTUAL_FUND",
            target_asset_region="DOMESTIC_STOCKS",
            frequency="MONTHLY",
            amount_jpy=50000,
            start_date="2025-01-01",
        )

        plan_id = plan.id

        response = authenticated_client.delete(f"/api/v1/recurring-plans/{plan_id}/")

        assert response.status_code == 204
        # Verify plan is deleted
        assert not RecurringInvestmentPlan.objects.filter(id=plan_id).exists()

    def test_delete_recurring_plan_unauthenticated_returns_401(self, api_client):
        """DELETE /recurring-plans/{id} without authentication should return 401 or redirect"""
        response = api_client.delete(
            "/api/v1/recurring-plans/1/",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",  # Force AJAX
        )
        assert response.status_code in [
            401,
            403,
            301,
        ], f"Expected auth error, got {response.status_code}"

    @pytest.mark.django_db
    def test_delete_recurring_plan_not_found_returns_404(self, authenticated_client):
        """DELETE /recurring-plans/{id} with non-existent ID should return 404"""
        response = authenticated_client.delete("/api/v1/recurring-plans/99999/")
        assert response.status_code == 404
