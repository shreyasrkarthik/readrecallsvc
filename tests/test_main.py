"""
Test cases for main application endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "ReadRecall FastAPI Service"
    assert "version" in data
    assert "status" in data
    assert "timestamp" in data


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


def test_not_found():
    """Test 404 endpoint"""
    response = client.get("/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
