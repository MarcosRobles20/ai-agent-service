from app.tools.http_request import http_request
from app.tools.web_search import web_search
from app.tools.rag_tool import rag_tool
from app.tools.time_tool import get_current_time
from app.tools.math_tool import multiply
from app.tools.summarize import summarize

tools = [
    get_current_time,
    multiply,
    rag_tool,
    web_search,
    http_request,
    summarize,
]