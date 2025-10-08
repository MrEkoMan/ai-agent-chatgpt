from fastapi.testclient import TestClient

import api


class SimpleExecutor:
    def invoke(self, payload):
        return {"output": "ok", "used_tools": []}


def test_invoke_missing_token(monkeypatch):
    # require a token
    monkeypatch.setattr(api, "API_KEY", "secret123")
    monkeypatch.setattr(api, "get_executor", lambda: SimpleExecutor())
    client = TestClient(api.app)

    r = client.post("/v1/invoke", json={"input": "hello"})
    assert r.status_code == 401
    assert "Missing Authorization header" in r.json().get("detail", "")


def test_invoke_invalid_token(monkeypatch):
    monkeypatch.setattr(api, "API_KEY", "secret123")
    monkeypatch.setattr(api, "get_executor", lambda: SimpleExecutor())
    client = TestClient(api.app)

    headers = {"Authorization": "Bearer wrong"}
    r = client.post("/v1/invoke", json={"input": "hello"}, headers=headers)
    assert r.status_code == 401
    assert "Invalid API token" in r.json().get("detail", "")


def test_invoke_valid_token(monkeypatch):
    monkeypatch.setattr(api, "API_KEY", "secret123")
    monkeypatch.setattr(api, "get_executor", lambda: SimpleExecutor())
    client = TestClient(api.app)

    headers = {"Authorization": "Bearer secret123"}
    r = client.post("/v1/invoke", json={"input": "hello"}, headers=headers)
    assert r.status_code == 200
    assert r.json().get("output") == "ok"


def test_tools_require_auth(monkeypatch):
    monkeypatch.setattr(api, "API_KEY", "secret123")
    monkeypatch.setattr(api, "get_executor", lambda: SimpleExecutor())
    client = TestClient(api.app)

    r = client.get("/v1/tools")
    assert r.status_code == 401

    r2 = client.get("/v1/tools", headers={"Authorization": "Bearer secret123"})
    assert r2.status_code == 200
