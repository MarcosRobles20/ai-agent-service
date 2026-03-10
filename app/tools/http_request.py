import requests
from bs4 import BeautifulSoup
from readability import Document
from langchain_core.tools import tool
from app.agent.events import agent_event


@tool
def http_request(url: str) -> dict:
    """
    Fetch a webpage and return the readable text content.
    Use this when the user provides a URL.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {
                "type": "http_response",
                "data": {"url": url, "content": None},
                "meta": {"status_code": response.status_code},
                "content": f"Error fetching page: {response.status_code}",
                "agent_events": [
                    agent_event("page_read", url.split("/")[2] if "/" in url else url, {"url": url})
                ]
            }
        html = response.text
        doc = Document(html)
        content_html = doc.summary()
        soup = BeautifulSoup(content_html, "html.parser")
        text = soup.get_text(separator="\n")
        return {
            "type": "http_response",
            "data": {"url": url, "content": text[:8000]},
            "meta": {"status_code": response.status_code},
            "content": f"Fetched content from {url}",
            "agent_events": [
                agent_event("page_read", url.split("/")[2] if "/" in url else url, {"url": url})
            ]
        }
    except Exception as e:
        return {
            "type": "http_response",
            "data": {"url": url, "content": None},
            "meta": {"error": str(e)},
            "content": f"HTTP request error: {str(e)}",
            "agent_events": [
                agent_event("page_read", url.split("/")[2] if "/" in url else url, {"url": url})
            ]
        }