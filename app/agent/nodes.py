from langchain_core.messages import SystemMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import ToolNode

from app.tools import (
    get_current_time,
    http_request,
    multiply,
    rag_tool,
    web_search,
    summarize
)

# ---------------------------------------------------
# Tools disponibles para el agente
# ---------------------------------------------------

tools = [
    get_current_time,
    multiply,
    rag_tool,
    web_search,
    http_request,
    summarize
]

# ---------------------------------------------------
# Modelo (se crea dinámicamente en call_model)
# ---------------------------------------------------

# ---------------------------------------------------
# System prompt del agente
# ---------------------------------------------------

system_message = SystemMessage(
    content="""
    You are an AI agent with access to tools.

    Rules:
    - If the question requires information after 2024 you MUST use web_search.
    - If the user provides a URL you MUST use http_request.
    - If retrieved content is long you should use summarize.
    - Do NOT answer from memory when a tool can be used.
    - Prefer tools over guessing.
    """
)

# ---------------------------------------------------
# Nodo que llama al modelo
# ---------------------------------------------------

def call_model(state):

    model = state.get("model", "qwen3:8b")

    llm = ChatOllama(
        model=model,
        temperature=0
    )

    llm_with_tools = llm.bind_tools(tools)

    messages = [system_message] + state["messages"]

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }

# ---------------------------------------------------
# Nodo que ejecuta tools
# ---------------------------------------------------

tool_node = ToolNode(tools)