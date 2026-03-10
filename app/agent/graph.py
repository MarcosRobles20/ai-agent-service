from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from .state import AgentState
from .nodes import call_model, tool_node
from .router import route_intent


# ---------------------------------------------------------
# Construcción del grafo del agente
# ---------------------------------------------------------
def create_graph(memory):
    """
    Crea y compila el grafo del agente.

    Flujo general:

        START
          │
          ▼
        agent
          │
     ┌────┴────┐
     │         │
     ▼         ▼
   tools      END
     │
     ▼
   agent

    El agente decide si usar herramientas.
    Si hay tool_call → ejecuta tool_node.
    Luego vuelve al agente para continuar razonando.
    """

    # -----------------------------------------------------
    # Configuración de memoria persistente
    # -----------------------------------------------------
    # SQLite se usa como checkpointer para que LangGraph
    # pueda guardar el estado de las conversaciones.
    # Esto permite mantener historial por thread_id.

    # Inicializar el builder con el estado global del agente
    builder = StateGraph(AgentState)

    # -------------------------------------------------
    # NODOS
    # -------------------------------------------------
    # Nodo principal: el modelo LLM que razona
    builder.add_node("agent", call_model)
    # Nodo que ejecuta herramientas solicitadas por el LLM
    builder.add_node("tools", tool_node)
    # -------------------------------------------------
    # EDGES (conexiones entre nodos)
    # -------------------------------------------------
    # Punto de entrada del grafo
    builder.add_edge(START, "agent")
    # Router condicional que decide qué hacer
    builder.add_conditional_edges(
      "agent",
      route_intent,
      {
          # Si el modelo pidió una tool
          "tools": "tools",
          # Si ya tiene respuesta final
          "__end__": END,
      },
    )
    # Después de ejecutar una herramienta,
    # volvemos al agente para continuar razonando
    builder.add_edge("tools", "agent")
    # -------------------------------------------------
    # Compilación del grafo
    # -------------------------------------------------
    graph = builder.compile(checkpointer=memory)
    return graph

