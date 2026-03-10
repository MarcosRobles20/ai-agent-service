def agent_event(type: str, content: str, metadata: dict | None = None):
    return {
        "type": type,
        "content": content,
        "metadata": metadata or {}
    }
