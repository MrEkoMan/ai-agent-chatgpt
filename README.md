# ai-agent-chatgpt

AI Agent built using ChatGPT and LangChain.

## Quick links for contributors

- See `.github/copilot-instructions.md` for concise guidance aimed at automation and AI-based coding assistants. It documents the project entry points (`agent.py`), development workflow, testing hints, and how to add tools.
- Key files:
  - `agent.py` — example runner and agent composition
  - `requirements.txt` — Python dependencies
  - `tools/` — small helper tools (see `tools/echo_tool.py`)
  - `tests/` — pytest examples that mock the LLM for fast, offline tests

## Running locally

Create and activate a virtualenv and install deps:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

Run the example agent:

```powershell
python agent.py
```

## Recommended development workflow

Follow these steps for a reliable, repeatable development environment on Windows/macOS/Linux.

1) Local Python workflow (fast iterate)

```powershell
# create and activate a venv
python -m venv .venv; .\.venv\Scripts\Activate.ps1
# install deps (pytest included)
pip install -r requirements.txt
# run tests locally
python -m pytest -q
# run the example agent
python agent.py
```

2) Docker (build a proxied runtime image)

```powershell
docker build -t ai-agent:latest .
docker run --rm ai-agent:latest
```

3) Development with docker-compose (recommended for iterative work on Windows)

The repository includes `docker-compose.override.yml` which, when present, runs the container as root to avoid permission issues when mounting the host workspace.

```powershell
# build and run with the override (docker-compose automatically picks it up)
docker compose up --build

# run tests inside the container (one-off)
docker compose run --rm ai-agent python -m pytest -q
```

Environment variables

- Put secrets (like OPENAI_API_KEY) in a `.env` file at the repo root. The compose files and Dockerfile will read `.env` when present.
- Avoid committing `.env` — consider adding it to `.gitignore`.

Pinned dependencies (optional but recommended)

For reproducible Docker builds and deployments pin your dependencies into `requirements.lock`.
You can generate it from your development environment:

PowerShell (Windows):
```powershell
.\tools\pin_requirements.ps1
```

POSIX (macOS/Linux):
```bash
./tools/pin_requirements.sh
```

The Dockerfile will prefer `requirements.lock` if present, falling back to `requirements.txt` otherwise.

Permission notes

- By default the image runs as a non-root `appuser`. For development on Windows the override runs as `root` because mounted volumes can otherwise be owned by the host and be unwritable by the container user.
- For production builds remove the override and rely on the non-root user in the Dockerfile.

If you need help reproducing a failing `docker run` (exit code 1), paste the container logs (run `docker compose up --build` and share the output) and I will debug it with you.
