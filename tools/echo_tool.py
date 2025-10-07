def echo_tool(input_text: str) -> str:
    """A tiny example tool for the agent that returns an echoed string.

    This demonstrates how a simple tool can be implemented and wired into
    `tools = [ { 'name': 'echo', 'func': echo_tool } ]` and passed to `AgentExecutor`.
    """
    return f"echo: {input_text}"
