from langchain_core.tools import tool
from app.agent.events import agent_event

@tool
def multiply(a: int, b: int) -> dict:
    """Multiply two numbers"""
    result = a * b
    return {
        "type": "math_result",
        "data": {"a": a, "b": b, "result": result},
        "meta": {},
        "content": f"{a} * {b} = {result}",
        "agent_events": [
            agent_event("math_operation", "multiply", {"a": a, "b": b, "result": result})
        ]
    }