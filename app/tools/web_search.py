from langchain.tools import tool
from ddgs import DDGS
from pydantic import BaseModel
from app.agent.events import agent_event

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str

@tool
def web_search(query: str) -> dict:
    """
    Search the web and return top results.
    Use this when the user asks for recent or factual information.
    """
    results_list = []
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            for r in results:
                results_list.append(SearchResult(
                    title=r.get("title", ""),
                    url=r.get("href", ""),
                    snippet=r.get("body", "")
                ).dict())
        # Retorna un dict Python, no un string serializado
        return {
            "type": "web_search",
            "data": {"query": query, "results": results_list},
            "meta": {"source": "ddgs"},
            "content": f"Found {len(results_list)} results for '{query}'",
            "agent_events": [
                agent_event("research_query", query),
                *[
                    agent_event(
                        "source",
                        r["url"].split("/")[2] if "url" in r and r["url"] else "",
                        {"url": r["url"], "title": r["title"]}
                    ) for r in results_list if r.get("url")
                ]
            ]
        }
    except Exception as e:
        return {
            "type": "web_search",
            "data": {"query": query, "results": []},
            "meta": {"source": "ddgs", "error": str(e)},
            "content": f"Error searching for '{query}': {str(e)}",
            "agent_events": [agent_event("research_query", query)]
        }