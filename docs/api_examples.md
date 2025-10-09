## API usage examples

This page contains quick examples for interacting with the AI Agent HTTP API.

Base URL (local dev): http://localhost:8000

1) Invoke the agent (synchronous)

curl example:

```bash
curl -X POST http://localhost:8000/v1/invoke \
  -H "Content-Type: application/json" \
  -d '{"input":"Summarize the following text: ..."}'
```

Python example (requests):

```python
import requests

resp = requests.post(
    'http://localhost:8000/v1/invoke',
    json={'input': 'Summarize the following text: ...'}
)
print(resp.json())
```

2) Invoke the agent with streaming (SSE)

curl (basic):

```bash
curl -N -X POST http://localhost:8000/v1/invoke/stream \
  -H "Content-Type: application/json" \
  -d '{"input":"Stream this text back in chunks"}'
```

Python example (httpx stream):

```python
import httpx

with httpx.stream('POST', 'http://localhost:8000/v1/invoke/stream', json={'input': '...'}, timeout=None) as r:
    for chunk in r.iter_bytes():
        if chunk:
            print(chunk.decode('utf-8'), end='')
```

3) List available tools

```bash
curl http://localhost:8000/v1/tools
```

4) Run a named tool

```bash
curl -X POST http://localhost:8000/v1/tools/echo/run \
  -H "Content-Type: application/json" \
  -d '{"input":"hello"}'
```

5) Health check

```bash
curl http://localhost:8000/health
```

Notes
- Replace `localhost:8000` with your deployed host when not running locally.
- Use the `Authorization` header if your instance is configured to require an API token.
