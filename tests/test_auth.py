"""
Test cases for authentication endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base
import tempfile
import os

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_register_user():
    """Test user registration"""
    user_data = {
        "name": "Test User",
        "email": "test@example.com", 
        "password": "testpassword123"
    }
    
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["name"] == user_data["name"]
    assert "id" in data


def test_register_duplicate_email():
    """Test registration with duplicate email"""
    user_data = {
        "name": "Test User 2",
        "email": "test@example.com",  # Same email as previous test
        "password": "testpassword123"
    }
    
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 409


def test_login_user():
    """Test user login"""
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "user" in data
    assert data["user"]["email"] == login_data["email"]


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401


def test_get_current_user():
    """Test getting current user info"""
    # First login to get token
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    login_response = client.post("/api/auth/login", json=login_data)
    token = login_response.json()["token"]
    
    # Use token to get user info
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == login_data["email"]


def test_get_current_user_invalid_token():
    """Test getting current user with invalid token"""
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401


# Cleanup
def teardown_module():
    """Clean up test database"""
    if os.path.exists("./test.db"):
        os.remove("./test.db")
