from fastapi import APIRouter
from app.schemas.chat import ChatRequest
from app.agent.graph import run_agent

router = APIRouter()


@router.post("/chat")
def chat(request: ChatRequest):

    answer = run_agent(request.messages)

    return {
        "response": answer
    }

