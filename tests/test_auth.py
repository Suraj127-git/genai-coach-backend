import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
import uuid


client = TestClient(app)


def test_register_and_login_flow():
    email = f"alice_{uuid.uuid4().hex[:8]}@example.com"
    r = client.post("/auth/register", json={
        "email": email,
        "password": "password123",
        "name": "Alice"
    })
    assert r.status_code == 200
    data = r.json()
    assert "token" in data
    assert data["user"]["email"] == email

    r2 = client.post("/auth/login", json={
        "email": email,
        "password": "password123"
    })
    assert r2.status_code == 200
    data2 = r2.json()
    token = data2["token"]

    r3 = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r3.status_code == 200
    me = r3.json()
    assert me["email"] == email

    # cookie set
    assert "refresh_token" in r2.cookies
    # refresh endpoint returns new tokens
    r4 = client.post("/auth/refresh", json={"refresh_token": r2.cookies.get("refresh_token")})
    assert r4.status_code == 200
    pair = r4.json()
    assert "access_token" in pair and "refresh_token" in pair

    # logout clears cookie
    r5 = client.post("/auth/logout")
    assert r5.status_code == 200