import requests
from bs4 import BeautifulSoup
from readability import Document
from langchain_core.tools import tool


@tool
def http_request(url: str) -> str:
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
            return f"Error fetching page: {response.status_code}"

        html = response.text

        # Extract main article
        doc = Document(html)
        content_html = doc.summary()

        soup = BeautifulSoup(content_html, "html.parser")

        text = soup.get_text(separator="\n")

        # limitar tamaño
        return text[:8000]

    except Exception as e:
        return f"HTTP request error: {str(e)}"