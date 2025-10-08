# Contributing

Thanks for contributing! This file describes the recommended local developer
workflow for the ai-agent project so contributions are fast, consistent and
easy to review.

Prerequisites
-------------
- Python 3.11+ (project targets 3.13 in CI)
- Git
- Docker (optional, for container-based testing)

Local development setup
-----------------------
1) Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2) Install runtime dependencies and developer tools:

```powershell
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Pre-commit and linters
----------------------
This repository includes `pre-commit` configured to run `ruff`, `black` and
`isort` on staged files. To enable hooks locally run:

```powershell
pre-commit install
```

Run the linters manually with:

```powershell
python -m ruff check .
python -m ruff format .
black .
isort .
```

Testing
-------
Unit tests use `pytest` and are designed to run offline (they mock or use a
fallback executor so no LLM keys are required). Run tests with:

```powershell
python -m pytest -q
```

Running the app
---------------
Run the example agent locally:

```powershell
python agent.py
```

Or run the HTTP API (FastAPI + Uvicorn):

```powershell
# If you want to run the API directly
python -m uvicorn api:app --host 0.0.0.0 --port 8000
```

Docker (optional)
-----------------
Build the image and run it:

```powershell
docker build -t ai-agent:latest .
docker run --rm -p 8000:8000 ai-agent:latest
```

Creating a pull request
-----------------------
1) Create a feature branch: `git checkout -b feat/description`.
2) Make small, focused commits. Run tests and linters locally before pushing.
3) Push the branch and open a PR. The CI will run lint and tests.

Notes
-----
- If you depend on a specific LangChain provider package (e.g. `langchain-openai`)
  add it to `requirements.txt` and the pinning workflow will update `requirements.lock`.
- If CI fails due to a lint error, run the linters locally and update the code
  or configuration as an incremental change.

Thank you for improving ai-agent — contributions are greatly appreciated!
