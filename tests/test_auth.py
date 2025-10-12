
import time

from fastapi.testclient import TestClient
import pytest

import api
from api import ADMIN_PASS, ADMIN_USER, TOKEN_LIFETIME, _TOKENS, app


@pytest.fixture(autouse=True)
def set_test_api_key():
    # Temporarily set API_KEY for tests in this module
    orig = getattr(api, "API_KEY", None)
    api.API_KEY = "tests-key"
    yield
    api.API_KEY = orig


client = TestClient(app)


def test_login_success_and_use_token():
    # login
    r = client.post("/login", json={"username": ADMIN_USER, "password": ADMIN_PASS})
    assert r.status_code == 200
    data = r.json()
    assert "token" in data and "expires_at" in data

    token = data["token"]

    # use token to call protected endpoint
    r2 = client.get("/v1/tools", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200


def test_login_failure():
    r = client.post("/login", json={"username": "bad", "password": "no"})
    assert r.status_code == 401


def test_logout_revokes_token():
    r = client.post("/login", json={"username": ADMIN_USER, "password": ADMIN_PASS})
    token = r.json()["token"]

    # logout
    r2 = client.post("/logout", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200

    # token should no longer work
    r3 = client.get("/v1/tools", headers={"Authorization": f"Bearer {token}"})
    assert r3.status_code == 401


def test_token_expiry():
    # issue token and set its expiry to a past time
    r = client.post("/login", json={"username": ADMIN_USER, "password": ADMIN_PASS})
    token = r.json()["token"]
    # simulate expiry
    _TOKENS[token] = int(time.time()) - 1

    r2 = client.get("/v1/tools", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 401
