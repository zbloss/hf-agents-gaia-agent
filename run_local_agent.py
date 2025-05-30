from agents.agent import MyAgent
from utils import run_agent
from smolagents import (
    DuckDuckGoSearchTool,
    # WikipediaSearchTool,
    VisitWebpageTool,
)
from tools.text_search import TextSearch
from tools.text_splitter import text_splitter
from tools.webpage_parser import WebpageParser
from tools.parse_wikipedia_table import WikipediaParser
from tools.open_files import OpenFilesTool
from prompts.default_prompt import generate_prompt
from agents import DEFAULT_ARGS


import os
import json
from dotenv import load_dotenv

load_dotenv()

QUESTIONS_FILEPATH: str = os.getenv("QUESTIONS_FILEPATH", default="metadata.jsonl")
OLLAMA_MODEL_ID: str = os.getenv("OLLAMA_MODEL_ID", default="gemma3:12b-it-qat")
OLLAMA_API_BASE: str = os.getenv("OLLAMA_API_BASE", default="http://localhost:11434")
OLLAMA_API_KEY: str | None = os.getenv("GOOGLE_AI_STUDIO_API_KEY")
OLLAMA_NUM_CTX: int = int(os.getenv("OLLAMA_NUM_CTX", default=8192))


myagent_args = {
    "provider": "litellm",
    "model_id": "gemini/gemini-2.0-flash-lite",
    # "api_base": OLLAMA_API_BASE,
    "planning_interval": 3,
    "tools": [
        DuckDuckGoSearchTool(),
        WikipediaParser(),
        VisitWebpageTool(),
        TextSearch(),
        text_splitter,
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
    "num_ctx": 8192,
    "temperature": 0.2,
}

print(f"Using args: {DEFAULT_ARGS}")

if __name__ == "__main__":
    agent = MyAgent(**DEFAULT_ARGS)

    with open(QUESTIONS_FILEPATH, "r") as f:
        questions = json.load(f)

    question = questions[0]
    question_text = question.get("question")
    file_name = question.get("file_name")
    prompt = generate_prompt(question_text, file_name)

    answers = run_agent(agent, [questions[0]])
    print("Answers:", answers)
    print("Finished running the agent.")
