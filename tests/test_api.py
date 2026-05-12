from fastapi.testclient import TestClient
from main import app
from database import Base, engine

client = TestClient(app)

def setup_module(module):
    Base.metadata.create_all(bind=engine)

# ----- TEST REGISTER -----
def test_register():
    response = client.post("/register", json={
        "username": "pytestuser",
        "email": "pytestuser@test.com",
        "password": "password123"
    })
    assert response.status_code in [200, 400]

# ----- TEST LOGIN RETURNS OTP MESSAGE -----
def test_login_returns_otp():
    # Register first
    client.post("/register", json={
        "username": "otptestuser",
        "email": "otptestuser@test.com",
        "password": "password123"
    })
    response = client.post("/login", data={
        "username": "otptestuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "OTP sent" in response.json()["message"]

# ----- TEST WRONG PASSWORD -----
def test_login_wrong_password():
    response = client.post("/login", data={
        "username": "otptestuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

# ----- TEST BALANCE WITHOUT TOKEN -----
def test_balance_no_token():
    response = client.get("/balance")
    assert response.status_code == 401

# ----- TEST REGISTER DUPLICATE -----
def test_register_duplicate():
    client.post("/register", json={
        "username": "duplicateuser",
        "email": "duplicate@test.com",
        "password": "password123"
    })
    response = client.post("/register", json={
        "username": "duplicateuser",
        "email": "duplicate@test.com",
        "password": "password123"
    })
    assert response.status_code == 400

# ----- TEST FORGOT PASSWORD -----
def test_forgot_password_unknown_email():
    response = client.post("/forgot-password?email=unknown@test.com")
    assert response.status_code == 200
    assert "message" in response.json()