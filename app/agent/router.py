def route_intent(state):
    last_message = state["messages"][-1]

    # 1️ Si hay tool_calls pendientes → vamos a tools
    if getattr(last_message, "tool_calls", None):
        return "tools"

    # 2️ Si la última respuesta del agente no contiene tokens, no hacemos nada (permanece en el nodo)
    if getattr(last_message, "content", None) in (None, ""):
        return None  # sigue en el mismo nodo "agent"

    # 3️ Si ya tenemos contenido, podemos terminar
    return "__end__"