def route_intent(state):
    last_message = state["messages"][-1]

    # Route to tools only when the model emitted tool calls.
    if getattr(last_message, "tool_calls", None):
        return "tools"

    return "__end__"