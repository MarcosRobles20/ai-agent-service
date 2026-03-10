from datetime import datetime
from langchain.tools import tool
from app.agent.events import agent_event

@tool
def get_current_time() -> dict:
    """Devuelve la fecha y hora actual del sistema."""
    now = datetime.now()
    value = now.strftime("%Y-%m-%d %H:%M:%S")
    return {
        "type": "current_time",
        "data": {"current_time": value},
        "meta": {},
        "content": value,
        "agent_events": [
            agent_event("time_retrieved", value, {"current_time": value})
        ]
    }

