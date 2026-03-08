from typing import Any, AsyncIterator
import json

from langchain_core.messages import AIMessage, HumanMessage

from app.schemas.chat import ChatRequest


SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


class ChatStreamService:
    """Application service for streaming chat responses over SSE."""

    @staticmethod
    async def stream_chat(request: ChatRequest, graph: Any) -> AsyncIterator[str]:
        thread_id = str(request.idChat or "default")

        messages = []
        for msg in request.messages:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))

        async for chunk, _metadata in graph.astream(
            {"messages": messages, "model": request.model or "qwen3:8b"},
            config={"configurable": {"thread_id": thread_id}},
            stream_mode="messages",
        ):
            content = getattr(chunk, "content", None)

            # Most model providers emit plain token text as strings.
            if isinstance(content, str) and content:
                yield f'data: {json.dumps({"type": "token", "content": content})}\n\n'
                continue

            # Some providers emit structured content blocks.
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        text = block.get("text")
                        if isinstance(text, str) and text:
                            yield f'data: {json.dumps({"type": "token", "content": text})}\n\n'

        yield f'data: {json.dumps({"type": "done", "idChat": request.idChat, "isNewChat": request.isNewChat, "model": request.model or "qwen3:8b"})}\n\n'
