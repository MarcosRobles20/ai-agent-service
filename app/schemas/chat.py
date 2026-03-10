from typing import List, Optional
from pydantic import BaseModel


class ChatMessage(BaseModel):

    role: str
    content: str


class ChatRequest(BaseModel):

    messages: List[ChatMessage]
    idChat: Optional[str] = None
    isNewChat: Optional[bool] = False
    model: Optional[str] = "qwen3:8b"


class ChatResponse(BaseModel):

    response: str