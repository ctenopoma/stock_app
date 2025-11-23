"""
Pytest configuration and shared fixtures
"""

import os
import sys
from pathlib import Path

# Add src directory to path BEFORE importing django
backend_dir = Path(__file__).resolve().parent.parent
src_dir = backend_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Configure Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

import pytest
from django.contrib.auth.models import User
from django.test import Client


@pytest.fixture
def db():
    """Database fixture - handled by pytest-django"""
    pass


@pytest.fixture
def client():
    """Django test client"""
    return Client()


@pytest.fixture
def user(db):
    """Create a test user"""
    return User.objects.create_user(
        username="testuser", password="testpass123", email="test@example.com"
    )


@pytest.fixture
def authenticated_client(client, user):
    """Authenticated test client"""
    client.login(username="testuser", password="testpass123")
    return client
