import sqlite3

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from .state import AgentState
from .nodes import call_model


def create_graph():

    builder = StateGraph(AgentState)

    builder.add_node("model", call_model)

    builder.add_edge(START, "model")
    builder.add_edge("model", END)

    conn = sqlite3.connect("agent_memory.db", check_same_thread=False)
    memory = SqliteSaver(conn)

    graph = builder.compile(checkpointer=memory)

    return graph