import json

from fastapi.testclient import TestClient

import api


class DummyExecutor:
    def __init__(self):
        self.tools = [
            {
                "name": "echo",
                "func": lambda s: f"echo: {s}",
                "description": "echoes",
            }
        ]

    def invoke(self, payload):
        return {"output": f"processed: {payload.get('input')}", "used_tools": []}

    def stream_invoke(self, payload):
        # simple generator for streaming
        text = f"streamed: {payload.get('input')}"
        for i in range(0, len(text), 8):
            yield text[i : i + 8]


def test_health():
    client = TestClient(api.app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_invoke(monkeypatch):
    dummy = DummyExecutor()
    monkeypatch.setattr(api, "get_executor", lambda: dummy)
    client = TestClient(api.app)

    r = client.post("/v1/invoke", json={"input": "hello"})
    assert r.status_code == 200
    assert r.json()["output"] == "processed: hello"


def test_list_tools(monkeypatch):
    dummy = DummyExecutor()
    monkeypatch.setattr(api, "get_executor", lambda: dummy)
    client = TestClient(api.app)

    r = client.get("/v1/tools")
    assert r.status_code == 200
    assert any(t["name"] == "echo" for t in r.json()["tools"])


def test_run_tool(monkeypatch):
    dummy = DummyExecutor()
    monkeypatch.setattr(api, "get_executor", lambda: dummy)
    client = TestClient(api.app)

    r = client.post("/v1/tools/echo/run", json={"input": "abc"})
    assert r.status_code == 200
    assert r.json()["result"] == "echo: abc"


def test_stream_invoke(monkeypatch):
    dummy = DummyExecutor()
    monkeypatch.setattr(api, "get_executor", lambda: dummy)
    client = TestClient(api.app)

    with client.stream(
        "POST",
        "/v1/invoke/stream",
        content=json.dumps({"input": "hello"}),
        headers={"Content-Type": "application/json"},
    ) as r:
        assert r.status_code == 200
        chunks = []
        for chunk in r.iter_lines():
            if chunk:
                # chunk may be bytes or str depending on client
                if isinstance(chunk, bytes):
                    text = chunk.decode().strip()
                else:
                    text = chunk.strip()
                # each chunk is 'data: <json>'
                if text.startswith("data:"):
                    payload = json.loads(text[len("data:"):].strip())
                    chunks.append(payload.get("output"))
    # chunks may split the marker; join and assert expected text present
    joined = "".join(chunks)
    assert "streamed:" in joined
