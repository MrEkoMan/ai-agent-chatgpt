import asyncio
import json
import os
import time
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import Body, FastAPI, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Local imports and app
from agent import build_agent

# OpenAPI tags
TAGS = [
    {"name": "agent", "description": "Agent invocation and streaming endpoints."},
    {"name": "tools", "description": "Tool discovery and execution endpoints."},
]


app = FastAPI(
    title="ai-agent API",
    version="0.1.0",
    description=(
        "Lightweight AI agent example. Use `/v1/invoke` to run the agent, "
        "`/v1/invoke/stream` for streaming responses, and `/v1/tools` to "
        "inspect available tools."
    ),
    openapi_tags=TAGS,
)

# API auth token (runtime). For development put it in .env or docker-compose env_file.
API_KEY = os.environ.get("AGENT_API_KEY")
# Admin credentials for login (development). Set these in the environment in production.
ADMIN_USER = os.environ.get("AGENT_ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("AGENT_ADMIN_PASS", "password")

# Token storage: token -> expiry timestamp (unix seconds)
_TOKENS: Dict[str, int] = {}
# Token lifetime in seconds (default 24 hours)
TOKEN_LIFETIME = int(os.environ.get("AGENT_TOKEN_LIFETIME", 60 * 60 * 24))


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    expires_at: int


class LogoutResponse(BaseModel):
    detail: str


class InvokeRequest(BaseModel):
    input: str = Field(
        ..., json_schema_extra={"example": "Summarize the following text: ..."}
    )
    chat_history: Optional[List[Dict[str, Any]]] = Field(
        None, description="Conversation history"
    )
    tools: Optional[List[str]] = Field(
        None, description="Optional list of tool names to allow"
    )


class ToolRunRequest(BaseModel):
    input: Any = Field(..., json_schema_extra={"example": "some input for the tool"})


class InvokeResponse(BaseModel):
    output: Optional[str] = Field(None, description="Primary assistant output")
    used_tools: List[str] = Field(
        default_factory=list, description="List of tools used"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Runtime metadata"
    )


class ToolsResponse(BaseModel):
    tools: List[Dict[str, str]] = Field(..., description="Available tools")


class ToolRunResponse(BaseModel):
    tool_name: str = Field(..., description="Name of the tool invoked")
    result: Any = Field(..., description="Tool execution result")


class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "ok"})


# Build a shared executor on first request. Uses lazy imports in agent.build_agent().
_executor = None

# Module-level Body examples to avoid function-call defaults warnings (B008)
INVOKE_BODY = Body(
    ...,
    examples={
        "default": {
            "summary": "Example invoke",
            "value": {"input": "Summarize the following text: ..."},
        }
    },
)

RUN_TOOL_BODY = Body(
    ...,
    examples={"default": {"summary": "Example tool run", "value": {"input": "abc"}}},
)

INVOKE_STREAM_BODY = Body(
    ...,
    examples={
        "default": {
            "summary": "Example invoke stream",
            "value": {"input": "Summarize the following text: ..."},
        }
    },
)


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
    # Accept either the single shared API_KEY or an issued session token
    if token == API_KEY:
        return True
    # prune expired tokens
    now = int(time.time())
    expired = [t for t, exp in _TOKENS.items() if exp <= now]
    for t in expired:
        _TOKENS.pop(t, None)

    exp = _TOKENS.get(token)
    if not exp or exp <= now:
        raise HTTPException(status_code=401, detail="Invalid API token")
    return True


def _issue_token() -> LoginResponse:
    import uuid

    token = uuid.uuid4().hex
    exp = int(time.time()) + TOKEN_LIFETIME
    _TOKENS[token] = exp
    return LoginResponse(token=token, expires_at=exp)


async def _invoke_executor_async(executor, payload: dict) -> dict:
    # Run blocking executor.invoke in a thread to avoid blocking the event loop
    return await asyncio.to_thread(executor.invoke, payload)


@app.post(
    "/v1/invoke",
    response_model=InvokeResponse,
    tags=["agent"],
    summary="Invoke the agent synchronously",
)
async def invoke(
    req: InvokeRequest = INVOKE_BODY,
    authorization: Optional[str] = Header(None),
    request: Request = None,
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


@app.get(
    "/v1/tools",
    response_model=ToolsResponse,
    tags=["tools"],
    summary="List available tools",
)
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


@app.post("/login", response_model=LoginResponse, tags=["agent"], summary="Login and get a session token")
async def login(req: LoginRequest = Body(...)):
    # Simple username/password auth for issuing temporary tokens (dev only)
    if req.username != ADMIN_USER or req.password != ADMIN_PASS:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return _issue_token()


@app.post("/logout", response_model=LogoutResponse, tags=["agent"], summary="Logout and revoke session token")
async def logout(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    if token in _TOKENS:
        _TOKENS.pop(token, None)
        return {"detail": "Logged out"}
    # If token is the static API_KEY, we don't revoke it
    if token == API_KEY:
        return {"detail": "Static API key cannot be revoked via logout"}
    raise HTTPException(status_code=401, detail="Invalid token")


@app.post(
    "/v1/tools/{name}/run",
    response_model=ToolRunResponse,
    tags=["tools"],
    summary="Execute a named tool",
)
async def run_tool(
    name: str,
    body: ToolRunRequest = RUN_TOOL_BODY,
    authorization: Optional[str] = Header(None),
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


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["agent"],
    summary="Service health check",
)
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


@app.post(
    "/v1/invoke/stream",
    tags=["agent"],
    summary="Invoke the agent with streaming (SSE)",
    responses={
        200: {
            "description": "Server-Sent Events streaming response with JSON payloads.",
            "content": {"text/event-stream": {"schema": {"type": "string"}}},
        }
    },
)
async def invoke_stream(
    req: InvokeRequest = INVOKE_STREAM_BODY,
    authorization: Optional[str] = Header(None),
):
    check_auth(authorization)
    payload = {"input": req.input, "chat_history": req.chat_history or []}

    async def event_stream():
        async for ev in _sse_event_generator(payload):
            yield ev

    return StreamingResponse(event_stream(), media_type="text/event-stream")
