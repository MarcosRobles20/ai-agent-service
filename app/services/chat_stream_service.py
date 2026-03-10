from typing import Any, AsyncIterator
import json

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph
from app.schemas.chat import ChatRequest


SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


def safe_json(obj):
    """Convierte objetos complejos a dict para serialización JSON."""
    if hasattr(obj, "dict"):
        return obj.dict()
    elif hasattr(obj, "model_dump"):  # Para Pydantic v2
        return obj.model_dump()
    elif hasattr(obj, "__dict__") and not isinstance(obj, type):
        return obj.__dict__
    elif isinstance(obj, list):
        return [safe_json(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: safe_json(v) for k, v in obj.items()}
    return obj


def normalize(obj):
    """Normaliza objetos complejos a tipos simples para JSON SSE."""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {k: normalize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize(v) for v in obj]
    # LangChain message objects
    if isinstance(obj, ToolMessage):
        return normalize(obj.content)
    if isinstance(obj, (AIMessage, HumanMessage)):
        return normalize(obj.content)
    if hasattr(obj, "content"):
        return normalize(obj.content)
    return str(obj)


def sse_event(payload: dict) -> str:
    """Convierte un dict en un evento SSE válido."""
    clean_payload = normalize(payload)
    return f"data: {json.dumps(clean_payload, ensure_ascii=False)}\n\n"


class ChatStreamService:
    """Servicio para streaming de chat sobre SSE."""

    @staticmethod
    async def stream_chat(request: ChatRequest, graph: StateGraph) -> AsyncIterator[str]:

        thread_id = str(request.idChat or "default")

        messages = []
        for msg in request.messages:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))

        async for event in graph.astream_events(
            {"messages": messages, "model": request.model or "qwen3:8b"},
            config={"configurable": {"thread_id": thread_id}},
            version="v2",
        ):

            kind = event.get("event")

            # =========================
            # TOOL START
            # =========================
            if kind == "on_tool_start":

                tool_name = event.get("name")
                tool_input = event.get("data", {}).get("input")

                # status = TOOL_STATUS_MESSAGES.get(
                #     tool_name,
                #     f"Ejecutando herramienta {tool_name}..."
                # )  # Comentado: tools_status messages ya no se usan

                # Status SSE
                # event_data = {"type": "status", "content": status}
                # print("[SSE emitido]", event_data)  # Comentado para limpieza de PR
                yield sse_event(event_data)

                # Tool call SSE
                event_data = {"type": "tool_call", "tool": tool_name, "data": safe_json(tool_input)}
                yield sse_event(event_data)

            # =========================
            # TOOL END
            # =========================
            elif kind == "on_tool_end":

                tool_name = event.get("name")
                tool_output = event.get("data", {}).get("output")

                # Normalizar ToolMessage a dict plano
                if hasattr(tool_output, "content"):
                    clean_output = normalize(tool_output.content)
                else:
                    clean_output = tool_output

                # --- asegurar que sea dict aunque venga como string JSON ---
                if isinstance(clean_output, str):
                    try:
                        clean_output = json.loads(clean_output)
                    except Exception:
                        pass  # si no es JSON, lo dejamos como está

                # Extraer agent_events si existen
                agent_events = None
                if isinstance(clean_output, dict):
                    agent_events = clean_output.pop("agent_events", None)

                # Emitir tool_result sin agent_events
                event_data = {"type": "tool_result", "tool": tool_name, "data": clean_output}
                yield sse_event(event_data)

                # Emitir agent_events por separado
                if agent_events:
                    for e in agent_events:
                        event_data = {
                            "type": "agent_event",
                            "event_type": e.get("type"),
                            "content": e.get("content"),
                            "metadata": e.get("metadata")
                        }
                        yield sse_event(event_data)

            # =========================
            # MODEL START (pensando)
            # =========================
            elif kind == "on_chat_model_start":
                event_data = {"type": "status", "content": "🤔 Pensando..."}
                yield sse_event(event_data)

            # =========================
            # TOKEN STREAM
            # =========================
            elif kind == "on_chat_model_stream":

                chunk = event["data"]["chunk"]
                content = getattr(chunk, "content", None)

                if isinstance(content, str) and content:
                    event_data = {"type": "token", "content": content}
                    yield sse_event(event_data)

                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict):
                            text = block.get("text")
                            if text:
                                event_data = {"type": "token", "content": text}
                                yield sse_event(event_data)

        # =========================
        # DONE
        # =========================
        event_data = {
            "type": "done",
            "idChat": request.idChat,
            "isNewChat": request.isNewChat,
            "model": request.model
        }
        yield sse_event(event_data)