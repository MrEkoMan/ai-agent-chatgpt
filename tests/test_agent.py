import pytest

from agent import build_agent


def test_build_agent_fallback_invokes_tool():
    # In environments without LangChain, build_agent returns a fallback executor
    executor = build_agent()
    result = executor.invoke({"input": "abc", "chat_history": []})
    # Fallback executor includes example_tool by default and will call it
    assert isinstance(result, dict)
    assert "output" in result


def test_echo_tool_importable():
    # Simple import check for the example tool
    from tools.echo_tool import echo_tool

    assert echo_tool("x") == "echo: x"
