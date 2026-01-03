import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """테스트 클라이언트"""
    return TestClient(app)

@pytest.fixture
def test_user():
    """테스트 유저 데이터"""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User"
    }

