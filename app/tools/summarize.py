from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from app.agent.events import agent_event

@tool
def summarize(text: str) -> dict:
    """
    Genera un resumen conciso de un texto largo.
    Úsala cuando el usuario pida resumir un artículo, documento o cualquier fragmento de texto.
    """
    llm = ChatOllama(
        model="qwen3:8b",
        temperature=0
    )
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Eres un asistente experto en resumir textos. "
            "Genera resúmenes concisos, claros y en el mismo idioma del texto original.",
        ),
        ("user", "Resume el siguiente texto:\n\n{text}"),
    ])
    chain = prompt | llm
    response = chain.invoke({"text": text})
    return {
        "type": "summary",
        "data": {"summary": response.content},
        "meta": {},
        "content": response.content,
        "agent_events": [
            agent_event("summarized", "summary", {"summary": response.content})
        ]
    }
