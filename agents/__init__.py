from smolagents import (
    DuckDuckGoSearchTool,
    VisitWebpageTool,
    WikipediaSearchTool,
)
from tools.text_search import TextSearch
from tools.text_splitter import text_splitter
from tools.webpage_parser import WebpageParser
from tools.parse_wikipedia_table import WikipediaParser
from tools.open_files import OpenFilesTool

DEFAULT_ARGS = myagent_args = {
    "provider": "litellm",
    "model_id": "gemini/gemini-2.0-flash-lite",
    # "api_base": OLLAMA_API_BASE,
    "planning_interval": 3,
    "add_base_tools": True,
    "tools": [
        DuckDuckGoSearchTool(),
        WikipediaParser(),
        VisitWebpageTool(),
        TextSearch(),
        text_splitter,
        WikipediaSearchTool(
            content_type="text",
            extract_format="HTML"
        ),
        WebpageParser(),
        OpenFilesTool(),
    ],
    "additional_authorized_imports": [
        "pandas",
        "numpy",
        "datetime",
        "json",
        "re",
        "math",
        "os",
        "requests",
        "csv",
        "urllib",
    ],
    "num_ctx": 128_000,
    "temperature": 0.2,
}
