from langchain_ollama import ChatOllama


def get_llm(model="qwen3:8b"):

    return ChatOllama(
        model=model,
        temperature=0.2
    )