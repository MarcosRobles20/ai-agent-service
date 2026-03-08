from langchain_core.tools import tool


@tool
def rag_tool(query: str) -> str:
    """
    Realiza una consulta a un sistema de Recuperación Augmentada por Generación (RAG).
    Útil para obtener información relevante de una base de datos o documentos.
    """
    # Aquí iría la lógica para consultar el sistema RAG con la query y devolver los resultados.
    return "Resultados de la consulta RAG para: " + query