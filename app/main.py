from fastapi import FastAPI
from langchain_core.messages import HumanMessage, AIMessage

from app.agent.graph import create_graph
from app.schemas.chat import ChatRequest

app = FastAPI()

graph = create_graph()


@app.post("/chat")
def chat(request: ChatRequest):

    messages = []

    for msg in request.messages[-1:]:

        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))

        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))

    thread_id = str(request.idChat or "default")

    result = graph.invoke(
        {"messages": messages},
        config={"configurable": {"thread_id": thread_id}},
    )
    last_message = result["messages"][-1]

    return {
        "response": last_message.content
    }