"""Pytest configuration for Runbox client tests."""

import os
import pytest

# Set test environment variables
os.environ["RUNBOX_URL"] = "http://localhost:8080"
os.environ["RUNBOX_API_KEY"] = "test-api-key"


@pytest.fixture
def api_key() -> str:
    """Return test API key."""
    return "test-api-key"


@pytest.fixture
def base_url() -> str:
    """Return test base URL."""
    return "http://localhost:8080"

