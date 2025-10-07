from dotenv import load_dotenv
from typing import Callable

# Lazy-import safe agent builder
load_dotenv()

# A simple canonical tool shape is provided by tools.__init__ (example_tool)
from tools import example_tool


def build_agent(llm: object | None = None, chat_history: list | None = None, tools: list | None = None, temperature: float = 0.0):
    """Construct and return an AgentExecutor for this example repo.

    This function imports LangChain pieces lazily. If LangChain isn't
    available, a small fallback executor is returned which implements a
    minimal `invoke(payload: dict) -> dict` contract used by tests and the
    README examples.
    """
    if chat_history is None:
        chat_history = []
    if tools is None:
        tools = [example_tool]

    # Try to import LangChain and related utilities. If that fails return
    # a lightweight fallback executor so the module remains importable and
    # tests can run offline.
    try:
        from langchain_community.chat_models import ChatOpenAI
        from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain.agents.format_scratchpad import format_to_openai_function_messages
        from langchain.agents import AgentExecutor
        from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser

        if llm is None:
            llm = ChatOpenAI(model="gpt-4-1106-preview", temperature=temperature)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful personal AI assistant named TARS. You have a geeky, clever, sarcastic, and edgy sense of humor."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"]),
                "chat_history": lambda x: x["chat_history"],
            }
            | prompt
            | llm
            | OpenAIFunctionsAgentOutputParser()
        )

        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        return agent_executor

    except Exception:
        # Lightweight fallback that implements a minimal invoke contract.
        class _FallbackExecutor:
            def __init__(self, agent=None, tools=None, verbose=False):
                self.agent = agent
                self.tools = tools or []
                self.verbose = verbose

            def invoke(self, payload: dict):
                # If tools are present and the first tool is callable, demonstrate calling it
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

        return _FallbackExecutor(agent=None, tools=tools, verbose=True)


if __name__ == "__main__":
    # Show a simple usage with the example tool wired in by default
    executor = build_agent()
    out = executor.invoke({"input": "hello world", "chat_history": []})
    print(out.get("output"))