from typing import Callable, Dict

def make_tool(name: str, func: Callable, description: str = "") -> Dict:
    """Return a canonical tool descriptor used by this repo's examples.

    The shape is intentionally small and matches common LangChain-like tools:
    { 'name': str, 'func': callable, 'description': str }
    """
    return {"name": name, "func": func, "description": description}

# Export a small example tool using the repository's echo tool
try:
    from .echo_tool import echo_tool
    example_tool = make_tool("echo", echo_tool, "Echoes input text with a prefix")
except Exception:
    # Keep import-safe if echo_tool is not present
    example_tool = make_tool("echo", lambda s: f"echo: {s}", "Fallback echo tool")

__all__ = ["make_tool", "example_tool"]
