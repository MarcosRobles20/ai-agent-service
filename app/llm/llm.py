from langchain_ollama import ChatOllama


def get_llm(model: str) -> ChatOllama:

    return ChatOllama(
        model=model,
        temperature=0.2
    )