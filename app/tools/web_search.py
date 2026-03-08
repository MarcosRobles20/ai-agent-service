from langchain.tools import tool
from ddgs import DDGS


@tool
def web_search(query: str) -> str:
    """
    Search the web and return top results.
    Use this when the user asks for recent or factual information.
    """

    results_text = []

    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)

            for r in results:
                title = r.get("title", "")
                link = r.get("href", "")
                snippet = r.get("body", "")

                results_text.append(
                    f"Title: {title} \n URL: {link} \n Snippet: {snippet} \n"
                )

        if not results_text:
            return "No results found."

        return "\n".join(results_text)

    except Exception as e:
        return f"Search error: {str(e)}"