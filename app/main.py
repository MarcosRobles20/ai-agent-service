from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import ollama
from app.agent.graph import create_graph
from app.schemas.chat import ChatRequest
from app.services.chat_stream_service import ChatStreamService, SSE_HEADERS



@asynccontextmanager
async def lifespan(app: FastAPI):

    # ---- STARTUP ----
    memory_cm = AsyncSqliteSaver.from_conn_string("agent_memory.db")
    memory = await memory_cm.__aenter__()

    graph = create_graph(memory)

    app.state.graph = graph
    app.state.memory_cm = memory_cm

    yield

    # ---- SHUTDOWN ----
    await memory_cm.__aexit__(None, None, None)


app = FastAPI(lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/agent-stream")
async def chat(request: ChatRequest):
    return StreamingResponse(
        ChatStreamService.stream_chat(request=request, graph=app.state.graph),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )

@app.get("/models")
def get_models_ollama():
    models = ollama.list()
    return models

@app.post("/")
def root():
    return {"message": "AI service funcionando. Envíe solicitudes POST a /agent-stream con el formato adecuado."}
