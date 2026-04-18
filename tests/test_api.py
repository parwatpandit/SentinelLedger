import pytest
from fastapi.testclient import TestClient
from main import app
import time

client = TestClient(app)

# ----- TEST REGISTER -----
def test_register():
    unique = f"pytestuser_{int(time.time())}"
    response = client.post("/register", json={
        "username": unique,
        "email": f"{unique}@test.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "account_number" in response.json()

# ----- TEST DUPLICATE REGISTER -----
def test_register_duplicate():
    response = client.post("/register", json={
        "username": "pytestuser",
        "email": "pytest@test.com",
        "password": "password123"
    })
    assert response.status_code == 400

# ----- TEST LOGIN -----
def test_login():
    response = client.post("/login", data={
        "username": "pytestuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

# ----- TEST WRONG PASSWORD -----
def test_login_wrong_password():
    response = client.post("/login", data={
        "username": "pytestuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

# ----- TEST BALANCE -----
def test_balance():
    # Login first
    login = client.post("/login", data={
        "username": "pytestuser",
        "password": "password123"
    })
    token = login.json()["access_token"]

    response = client.get("/balance", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert "balance" in response.json()

# ----- TEST UNAUTHORIZED BALANCE -----
def test_balance_no_token():
    response = client.get("/balance")
    assert response.status_code == 401