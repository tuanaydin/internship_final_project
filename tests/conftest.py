import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Provide one in-process HTTP client for API regression tests."""

    with TestClient(app) as test_client:
        yield test_client