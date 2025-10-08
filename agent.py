import warnings
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# A simple canonical tool shape is provided by tools.__init__ (example_tool)
from tools import example_tool

# Lazy-import safe agent builder
load_dotenv()


class _FallbackExecutor:
    """Lightweight fallback executor used when LangChain is unavailable.

    Keeps behavior minimal and deterministic for unit tests and local dev.
    """

    def __init__(
        self, agent: Any = None, tools: Optional[List] = None, verbose: bool = False
    ):
        self.agent = agent
        self.tools = tools or []
        self.verbose = verbose

    def invoke(self, payload: Dict) -> Dict:
        tool_res = None
        if self.tools:
            t = self.tools[0]
            func = t.get("func") if isinstance(t, dict) else getattr(t, "func", None)
            if callable(func):
                try:
                    tool_res = func(payload.get("input"))
                except Exception:
                    tool_res = None
        return {"output": tool_res or f"fallback: received {payload.get('input')!r}"}


def _import_langchain_components() -> Dict[str, Any]:
    """Attempt to import LangChain components from known locations.

    Returns a mapping of names to symbols if successful. Raises on failure.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            # prefer the langchain-openai package if installed
            from langchain_openai import ChatOpenAI  # type: ignore
        except Exception:
            try:
                from langchain_community.chat_models import ChatOpenAI  # type: ignore
            except Exception:
                from langchain.chat_models import ChatOpenAI  # type: ignore

        from langchain.agents import AgentExecutor
        from langchain.agents.format_scratchpad import (
            format_to_openai_function_messages,
        )
        from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
        from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

    return {
        "ChatOpenAI": ChatOpenAI,
        "AgentExecutor": AgentExecutor,
        "format_to_openai_function_messages": format_to_openai_function_messages,
        "OpenAIFunctionsAgentOutputParser": OpenAIFunctionsAgentOutputParser,
        "ChatPromptTemplate": ChatPromptTemplate,
        "MessagesPlaceholder": MessagesPlaceholder,
    }


def build_agent(
    llm: Any | None = None,
    chat_history: Optional[List[Dict]] | None = None,
    tools: Optional[List] | None = None,
    temperature: float = 0.0,
) -> Any:
    """Construct and return an AgentExecutor for this example repo.

    If LangChain isn't available, returns a lightweight fallback executor
    implementing a minimal `invoke(payload)->dict` contract used by tests.
    """
    if chat_history is None:
        chat_history = []
    if tools is None:
        tools = [example_tool]

    try:
        comps = _import_langchain_components()
        ChatOpenAI = comps["ChatOpenAI"]
        AgentExecutor = comps["AgentExecutor"]
        format_to_openai_function_messages = comps["format_to_openai_function_messages"]
        OpenAIFunctionsAgentOutputParser = comps["OpenAIFunctionsAgentOutputParser"]
        ChatPromptTemplate = comps["ChatPromptTemplate"]
        MessagesPlaceholder = comps["MessagesPlaceholder"]

        if llm is None:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                llm = ChatOpenAI(model="gpt-4-1106-preview", temperature=temperature)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "You are a helpful personal AI assistant named TARS. "
                        "You have a geeky, clever, sarcastic, and edgy sense of humor."
                    ),
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_function_messages(
                    x["intermediate_steps"]
                ),
                "chat_history": lambda x: x["chat_history"],
            }
            | prompt
            | llm
            | OpenAIFunctionsAgentOutputParser()
        )

        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        return agent_executor
    except Exception:
        return _FallbackExecutor(agent=None, tools=tools, verbose=True)


if __name__ == "__main__":
    # Show a simple usage with the example tool wired in by default
    executor = build_agent()
    out = executor.invoke({"input": "hello world", "chat_history": []})
    print(out.get("output"))
