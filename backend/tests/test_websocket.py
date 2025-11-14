"""
Unit tests for WebSocket endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import init_db
import asyncio


@pytest.fixture(scope="function")
async def setup_db():
    """Set up test database."""
    await init_db()
    yield


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_websocket_connection(client, setup_db):
    """Test WebSocket connection to status endpoint."""
    # First create a job
    response = client.post(
        "/api/generate",
        json={"prompt": "Test application"}
    )
    assert response.status_code == 200
    job_id = response.json()["job_id"]
    
    # Connect via WebSocket
    with client.websocket_connect(f"/api/ws/status/{job_id}") as websocket:
        # Should receive initial status
        data = websocket.receive_json()
        assert data["type"] == "status_update"
        assert "data" in data
        assert data["data"]["job_id"] == job_id

