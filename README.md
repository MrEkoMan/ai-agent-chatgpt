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
# ai-agent-chatgpt
AI Agent built using ChatGPT
