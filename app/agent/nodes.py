from langchain_ollama import ChatOllama
from .state import AgentState


llm = ChatOllama(
    model="qwen3:8b",
    temperature=0
)


def call_model(state: AgentState):

    messages = state["messages"]

    response = llm.invoke(messages)

    return {
        "messages": [response]
    }