"""
Integration tests for Holdings CRUD operations
Tests end-to-end workflows with database persistence
"""

import json

import pytest
from django.contrib.auth.models import User


@pytest.mark.integration
class TestHoldingsCRUDIntegration:
    """Integration tests for complete CRUD workflow"""

    API_ENDPOINT = "/api/v1/holdings"

    def test_complete_holdings_crud_workflow(self, db, authenticated_client):
        """
        Integration test: Create, Read, Update, Delete a holding

        Workflow:
        1. Create a holding via POST /holdings
        2. Retrieve it via GET /holdings/{id}
        3. Update it via PUT /holdings/{id}
        4. Delete it via DELETE /holdings/{id}
        5. Verify it's gone via GET /holdings/{id} (404)
        """
        # Step 1: CREATE
        payload = {
            "account_type": "NISA",
            "asset_class": "MUTUAL_FUND",
            "asset_region": "DOMESTIC_STOCKS",
            "asset_identifier": "JP0123456789",
            "asset_name": "Test Fund",
            "current_amount_jpy": 100000.00,
            "purchase_date": "2025-01-01",
        }

        create_response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )

        assert create_response.status_code == 201
        created_holding = create_response.json()
        holding_id = created_holding["id"]

        # Verify created holding has expected fields
        assert created_holding["asset_name"] == "Test Fund"
        assert created_holding["current_amount_jpy"] == 100000.00
        assert "created_at" in created_holding
        assert "updated_at" in created_holding

        # Step 2: READ (by ID)
        get_response = authenticated_client.get(f"{self.API_ENDPOINT}/{holding_id}")
        assert get_response.status_code == 200
        retrieved_holding = get_response.json()
        assert retrieved_holding["id"] == holding_id
        assert retrieved_holding["asset_name"] == "Test Fund"

        # Step 3: UPDATE
        update_payload = {
            "account_type": "GENERAL",  # Changed from NISA
            "asset_class": "INDIVIDUAL_STOCK",  # Changed from MUTUAL_FUND
            "asset_region": "INTERNATIONAL_STOCKS",  # Changed
            "asset_identifier": "JP0123456789",
            "asset_name": "Updated Fund",  # Changed
            "current_amount_jpy": 150000.00,  # Changed
            "purchase_date": "2025-02-01",  # Changed
        }

        update_response = authenticated_client.put(
            f"{self.API_ENDPOINT}/{holding_id}",
            data=json.dumps(update_payload),
            content_type="application/json",
        )

        assert update_response.status_code == 200
        updated_holding = update_response.json()
        assert updated_holding["account_type"] == "GENERAL"
        assert updated_holding["asset_class"] == "INDIVIDUAL_STOCK"
        assert updated_holding["asset_name"] == "Updated Fund"
        assert updated_holding["current_amount_jpy"] == 150000.00

        # Verify update persisted
        verify_response = authenticated_client.get(f"{self.API_ENDPOINT}/{holding_id}")
        assert verify_response.status_code == 200
        verified_holding = verify_response.json()
        assert verified_holding["asset_name"] == "Updated Fund"

        # Step 4: DELETE
        delete_response = authenticated_client.delete(
            f"{self.API_ENDPOINT}/{holding_id}"
        )
        assert delete_response.status_code == 204

        # Step 5: VERIFY DELETED
        final_get = authenticated_client.get(f"{self.API_ENDPOINT}/{holding_id}")
        assert final_get.status_code == 404

    def test_partial_update_via_patch(self, db, authenticated_client):
        """Test PATCH for partial updates"""
        # Create
        payload = {
            "account_type": "NISA",
            "asset_class": "MUTUAL_FUND",
            "asset_region": "DOMESTIC_STOCKS",
            "asset_identifier": "JP0123456789",
            "asset_name": "Test Fund",
            "current_amount_jpy": 100000.00,
        }

        create_response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )
        holding_id = create_response.json()["id"]

        # Partial update (only amount)
        patch_payload = {"current_amount_jpy": 200000.00}

        patch_response = authenticated_client.patch(
            f"{self.API_ENDPOINT}/{holding_id}",
            data=json.dumps(patch_payload),
            content_type="application/json",
        )

        assert patch_response.status_code == 200
        patched = patch_response.json()
        assert patched["current_amount_jpy"] == 200000.00
        # Other fields should remain unchanged
        assert patched["asset_name"] == "Test Fund"
        assert patched["account_type"] == "NISA"

    def test_create_multiple_holdings_and_list(self, db, authenticated_client):
        """Create multiple holdings and verify list returns all"""
        holdings_data = [
            {
                "account_type": "NISA",
                "asset_class": "MUTUAL_FUND",
                "asset_region": "DOMESTIC_STOCKS",
                "asset_identifier": "JP0001",
                "asset_name": "Fund 1",
                "current_amount_jpy": 100000,
            },
            {
                "account_type": "GENERAL",
                "asset_class": "INDIVIDUAL_STOCK",
                "asset_region": "INTERNATIONAL_STOCKS",
                "asset_identifier": "US0001",
                "asset_name": "Stock 1",
                "current_amount_jpy": 50000,
            },
            {
                "account_type": "NISA",
                "asset_class": "CRYPTOCURRENCY",
                "asset_region": "CRYPTOCURRENCY",
                "asset_identifier": "BTC",
                "asset_name": "Bitcoin",
                "current_amount_jpy": 500000,
            },
        ]

        created_ids = []
        for data in holdings_data:
            response = authenticated_client.post(
                self.API_ENDPOINT,
                data=json.dumps(data),
                content_type="application/json",
            )
            assert response.status_code == 201
            created_ids.append(response.json()["id"])

        # List all holdings
        list_response = authenticated_client.get(self.API_ENDPOINT)
        assert list_response.status_code == 200
        list_data = list_response.json()

        # Verify all created holdings are in the list
        assert list_data["count"] >= 3
        result_ids = [h["id"] for h in list_data["results"]]
        for holding_id in created_ids:
            assert holding_id in result_ids

    def test_holdings_isolation_per_user(self, db, client):
        """
        Integration test: Holdings are isolated per user
        User A cannot see or modify User B's holdings
        """
        # Create two users
        user_a = User.objects.create_user(username="usera", password="pass123")
        user_b = User.objects.create_user(username="userb", password="pass123")

        # Create holding for user A
        client.login(username="usera", password="pass123")
        payload_a = {
            "account_type": "NISA",
            "asset_class": "MUTUAL_FUND",
            "asset_region": "DOMESTIC_STOCKS",
            "asset_identifier": "JP0001",
            "asset_name": "User A Fund",
            "current_amount_jpy": 100000,
        }
        response_a = client.post(
            self.API_ENDPOINT,
            data=json.dumps(payload_a),
            content_type="application/json",
        )
        holding_a_id = response_a.json()["id"]

        # Create holding for user B
        client.logout()
        client.login(username="userb", password="pass123")
        payload_b = {
            "account_type": "GENERAL",
            "asset_class": "INDIVIDUAL_STOCK",
            "asset_region": "INTERNATIONAL_STOCKS",
            "asset_identifier": "US0001",
            "asset_name": "User B Stock",
            "current_amount_jpy": 50000,
        }
        response_b = client.post(
            self.API_ENDPOINT,
            data=json.dumps(payload_b),
            content_type="application/json",
        )
        holding_b_id = response_b.json()["id"]

        # User A should not see User B's holding
        client.logout()
        client.login(username="usera", password="pass123")
        list_response = client.get(self.API_ENDPOINT)
        result_ids = [h["id"] for h in list_response.json()["results"]]

        assert holding_a_id in result_ids
        assert holding_b_id not in result_ids

        # User A should not be able to access User B's holding
        detail_response = client.get(f"{self.API_ENDPOINT}/{holding_b_id}")
        assert detail_response.status_code == 404

    def test_validation_persists_across_operations(self, db, authenticated_client):
        """Test that validation rules persist throughout operations"""
        # Attempt to create with invalid account_type
        invalid_payload = {
            "account_type": "INVALID",
            "asset_class": "MUTUAL_FUND",
            "asset_region": "DOMESTIC_STOCKS",
            "asset_identifier": "JP0001",
            "asset_name": "Invalid Fund",
            "current_amount_jpy": 100000,
        }

        response = authenticated_client.post(
            self.API_ENDPOINT,
            data=json.dumps(invalid_payload),
            content_type="application/json",
        )
        assert response.status_code == 400

        # Attempt to create with negative amount
        negative_payload = {
            "account_type": "NISA",
            "asset_class": "MUTUAL_FUND",
            "asset_region": "DOMESTIC_STOCKS",
            "asset_identifier": "JP0001",
            "asset_name": "Negative Fund",
            "current_amount_jpy": -100000,
        }

        response = authenticated_client.post(
            self.API_ENDPOINT,
            data=json.dumps(negative_payload),
            content_type="application/json",
        )
        assert response.status_code == 400

        # Attempt to update with invalid values
        # First create a valid holding
        valid_payload = {
            "account_type": "NISA",
            "asset_class": "MUTUAL_FUND",
            "asset_region": "DOMESTIC_STOCKS",
            "asset_identifier": "JP0001",
            "asset_name": "Valid Fund",
            "current_amount_jpy": 100000,
        }
        create_response = authenticated_client.post(
            self.API_ENDPOINT,
            data=json.dumps(valid_payload),
            content_type="application/json",
        )
        holding_id = create_response.json()["id"]

        # Try to update with invalid values
        invalid_update = {
            "account_type": "NISA",
            "asset_class": "MUTUAL_FUND",
            "asset_region": "DOMESTIC_STOCKS",
            "asset_identifier": "JP0001",
            "asset_name": "Valid Fund",
            "current_amount_jpy": -50000,  # Invalid
        }

        update_response = authenticated_client.put(
            f"{self.API_ENDPOINT}/{holding_id}",
            data=json.dumps(invalid_update),
            content_type="application/json",
        )
        assert update_response.status_code == 400

    def test_holdings_timestamp_management(self, db, authenticated_client):
        """Test that created_at and updated_at are properly managed"""
        payload = {
            "account_type": "NISA",
            "asset_class": "MUTUAL_FUND",
            "asset_region": "DOMESTIC_STOCKS",
            "asset_identifier": "JP0001",
            "asset_name": "Test Fund",
            "current_amount_jpy": 100000,
        }

        # Create
        create_response = authenticated_client.post(
            self.API_ENDPOINT, data=json.dumps(payload), content_type="application/json"
        )
        created_holding = create_response.json()
        holding_id = created_holding["id"]
        original_created_at = created_holding["created_at"]
        original_updated_at = created_holding["updated_at"]

        # Verify created_at and updated_at are set
        assert original_created_at is not None
        assert original_updated_at is not None

        # Update
        import time

        time.sleep(1)  # Ensure time passes

        update_payload = {
            "account_type": "NISA",
            "asset_class": "MUTUAL_FUND",
            "asset_region": "DOMESTIC_STOCKS",
            "asset_identifier": "JP0001",
            "asset_name": "Updated Fund",
            "current_amount_jpy": 150000,
        }

        update_response = authenticated_client.put(
            f"{self.API_ENDPOINT}/{holding_id}",
            data=json.dumps(update_payload),
            content_type="application/json",
        )
        updated_holding = update_response.json()
        new_updated_at = updated_holding["updated_at"]

        # created_at should not change
        assert updated_holding["created_at"] == original_created_at
        # updated_at should be newer
        assert new_updated_at >= original_updated_at

    def test_pagination_integration(self, db, authenticated_client):
        """Test pagination works correctly with multiple holdings"""
        # Create 15 holdings
        for i in range(15):
            payload = {
                "account_type": "NISA",
                "asset_class": "MUTUAL_FUND",
                "asset_region": "DOMESTIC_STOCKS",
                "asset_identifier": f"JP{i:04d}",
                "asset_name": f"Fund {i}",
                "current_amount_jpy": 100000 + (i * 10000),
            }
            response = authenticated_client.post(
                self.API_ENDPOINT,
                data=json.dumps(payload),
                content_type="application/json",
            )
            assert response.status_code == 201

        # Get page 1 with page_size=10
        page1_response = authenticated_client.get(
            f"{self.API_ENDPOINT}?page=1&page_size=10"
        )
        assert page1_response.status_code == 200
        page1_data = page1_response.json()
        assert len(page1_data["results"]) <= 10
        assert page1_data["next"] is not None or page1_data["count"] <= 10

        # Get page 2 if it exists
        if page1_data["next"]:
            page2_response = authenticated_client.get(
                f"{self.API_ENDPOINT}?page=2&page_size=10"
            )
            assert page2_response.status_code == 200
