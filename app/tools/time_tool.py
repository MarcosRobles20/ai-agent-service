from datetime import datetime
from langchain.tools import tool


@tool
def get_current_time() -> str:
    """Devuelve la fecha y hora actual del sistema."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

