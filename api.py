import asyncio
import json
import os
import time
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Local imports and app
from agent import build_agent

app = FastAPI(title="ai-agent API")

# API auth token (runtime). For development put it in .env or docker-compose env_file.
API_KEY = os.environ.get("AGENT_API_KEY")


class InvokeRequest(BaseModel):
    input: str
    chat_history: Optional[List[Dict[str, Any]]] = None
    tools: Optional[List[str]] = None


class ToolRunRequest(BaseModel):
    input: Any


# Build a shared executor on first request. Uses lazy imports in agent.build_agent().
_executor = None


def get_executor():
    global _executor
    if _executor is None:
        _executor = build_agent()
    return _executor


def _build_payload(req: InvokeRequest) -> Dict[str, Any]:
    return {"input": req.input, "chat_history": req.chat_history or []}


def _serialize_tool(t: Any) -> Dict[str, str]:
    if isinstance(t, dict):
        return {
            "name": t.get("name"),
            "description": t.get("description"),
        }

    return {
        "name": getattr(t, "name", str(t)),
        "description": getattr(t, "description", ""),
    }


def check_auth(authorization: Optional[str]):
    if API_KEY is None:
        return True
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API token")
    return True


async def _invoke_executor_async(executor, payload: dict) -> dict:
    # Run blocking executor.invoke in a thread to avoid blocking the event loop
    return await asyncio.to_thread(executor.invoke, payload)


@app.post("/v1/invoke")
async def invoke(
    req: InvokeRequest,
    request: Request,
    authorization: Optional[str] = Header(None),
):
    check_auth(authorization)
    executor = get_executor()

    payload = _build_payload(req)
    start = time.time()
    try:
        out = await _invoke_executor_async(executor, payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    duration = int((time.time() - start) * 1000)
    return {
        "output": out.get("output"),
        "used_tools": out.get("used_tools", []),
        "metadata": {"duration_ms": duration},
    }


@app.get("/v1/tools")
async def list_tools(authorization: Optional[str] = Header(None)):
    check_auth(authorization)
    executor = get_executor()
    tools = []
    try:
        for t in getattr(executor, "tools", []):
            tools.append(_serialize_tool(t))
    except Exception:
        pass
    return {"tools": tools}


@app.post("/v1/tools/{name}/run")
async def run_tool(
    name: str, body: ToolRunRequest, authorization: Optional[str] = Header(None)
):
    check_auth(authorization)
    executor = get_executor()
    for t in getattr(executor, "tools", []):
        tname = t.get("name") if isinstance(t, dict) else getattr(t, "name", None)
        func = t.get("func") if isinstance(t, dict) else getattr(t, "func", None)
        if tname != name or not callable(func):
            continue
        try:
            result = await asyncio.to_thread(func, body.input)
            return {"tool_name": name, "result": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
    raise HTTPException(status_code=404, detail="Tool not found")


@app.get("/health")
async def health():
    return {"status": "ok"}


async def _chunk_string(s: str, chunk_size: int = 256):
    for i in range(0, len(s), chunk_size):
        yield s[i : i + chunk_size]


async def _sse_event_generator(payload: dict) -> AsyncGenerator[str, None]:
    """Return an SSE generator yielding JSON chunks for the payload's output.

    If underlying executor provides a streaming generator (attribute
    `stream_invoke`), use it. Otherwise fallback to chunking the full
    output string.
    """
    executor = get_executor()
    stream_fn = getattr(executor, "stream_invoke", None)
    if callable(stream_fn):
        def gen():
            for piece in stream_fn(payload):
                yield piece

        loop = asyncio.get_running_loop()
        for piece in await loop.run_in_executor(None, lambda: list(gen())):
            data = json.dumps({"output": piece})
            yield f"data: {data}\n\n"
        return

    # Fallback: call invoke and chunk the result
    out = await _invoke_executor_async(executor, payload)
    text = out.get("output") or ""
    async for chunk in _chunk_string(text):
        data = json.dumps({"output": chunk})
        yield f"data: {data}\n\n"


@app.post("/v1/invoke/stream")
async def invoke_stream(
    req: InvokeRequest, authorization: Optional[str] = Header(None)
):
    check_auth(authorization)
    payload = {"input": req.input, "chat_history": req.chat_history or []}

    async def event_stream():
        async for ev in _sse_event_generator(payload):
            yield ev

    return StreamingResponse(event_stream(), media_type="text/event-stream")
