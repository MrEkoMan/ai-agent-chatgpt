## Quick guidance for AI coding agents working on ai-agent-chatgpt

Concise, actionable notes to get an automated coding assistant productive in this repo.

- Project entry points
  - `agent.py` — canonical example runner. It exposes `build_agent(...)` and will lazily import LangChain; when LangChain isn't installed a small fallback executor is returned (implements invoke(payload)->{output}).
  - `tools/` — example tools live here (`tools/echo_tool.py`, `tools/__init__.py` exports `example_tool` and `make_tool`).
  - `tests/` — pytest examples that exercise the fallback executor and show mocking patterns.

- Big-picture architecture
  - Purpose: a minimal LangChain-based agent example that demonstrates prompt composition, tool wiring, and output parsing without forcing heavy runtime deps for static edits.
  - Data flow (full LangChain path): user input -> ChatPromptTemplate (chat_history, agent_scratchpad) -> ChatOpenAI LLM -> OpenAIFunctionsAgentOutputParser -> AgentExecutor.invoke() -> dict{output}.
  - Fallback path: if LangChain imports fail, `build_agent()` returns a lightweight executor that calls the first tool (if present) or echoes the input. This keeps tests and CI fast.

- Developer workflows & common commands
  - Create/activate venv and install deps (PowerShell):

    ```powershell
    python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
    ```

  - Run the example agent locally (uses lazy imports — will use fallback if langchain not installed):

    ```powershell
    python agent.py
    ```

  - Tests (pytest): tests mock or rely on fallback executor so they run without LangChain.

- Project-specific conventions and patterns
  - Agent composition pattern: `agent = mapping | prompt | llm | parser` — preserve order when adding or modifying components.
  - Tools: repo uses a small canonical tool shape (dict with keys `name`, `func`, `description`) exported by `tools.make_tool`. Tests call `agent.build_agent()` which by default wires `tools.example_tool`.
  - Short-term memory: kept as an in-memory list `chat_history` (no persistence). If adding persistence, preserve the list interface in the prompt lambdas.

- Integration points and testing notes
  - LangChain/OpenAI: external runtime dependency. Unit tests should either:
    - Patch `langchain_community.chat_models.ChatOpenAI` and AgentExecutor internals, or
    - Use the fallback executor by running without LangChain installed (the tests in `tests/` show this approach).
  - Secrets: put API keys in a `.env` file at the repo root (variables in uppercase). Add `.env` to `.gitignore` if you want to avoid committing secrets.

- Examples of common edits (concrete)
  - Add a new tool: create `tools/my_tool.py` exporting a function `def run(input: str) -> str`, then add `tools_list = [ make_tool('mytool', run, 'desc') ]` and call `build_agent(tools=tools_list)`.
  - Change system prompt: edit the first system message in `ChatPromptTemplate.from_messages(...)` inside `agent.build_agent` when LangChain is available.

- Files to reference quickly
  - `agent.py` — build_agent + lazy imports + fallback executor
  - `tools/__init__.py` — `make_tool`, `example_tool` canonical shape
  - `tools/echo_tool.py` — tiny example tool
  - `tests/test_agent.py` — shows fallback executor usage in tests
  - `requirements.txt` — runtime deps; `pytest` is included for tests

If you'd like, I can expand this with a short snippet demonstrating how to mock `ChatOpenAI` in tests or add a CI workflow that runs `pytest` using the `requirements.txt` environment. Tell me which you'd prefer.

### Quick pytest mock snippet

Use this pattern when you want to unit-test logic that invokes the LLM without making network calls. It patches the LangChain model and the agent invoke call.

```python
from unittest.mock import patch

def test_agent_with_mocked_llm():
  # Replace the ChatOpenAI constructor with a lightweight dummy so build_agent
  # doesn't attempt a real network LLM.
  with patch('langchain_community.chat_models.ChatOpenAI') as MockChat:
    MockChat.return_value = object()  # any object is fine for construction

    # Patch AgentExecutor.invoke to return a deterministic value
    with patch('langchain.agents.AgentExecutor.invoke') as mock_invoke:
      mock_invoke.return_value = {'output': 'mocked'}

      executor = build_agent()  # imports are lazy; safe to call
      out = executor.invoke({'input': 'hello', 'chat_history': []})
      assert out['output'] == 'mocked'
```
