from agents.agent import MyAgent
from utils import run_agent

import os
import json
from dotenv import load_dotenv
load_dotenv()

QUESTIONS_FILEPATH: str = os.getenv("QUESTIONS_FILEPATH", default="metadata.jsonl")
OLLAMA_API_BASE: str = os.getenv("OLLAMA_API_BASE", default="http://localhost:11434")
OLLAMA_API_KEY: str | None = os.getenv("OLLAMA_API_KEY")


print(f"Using OLLAMA API base: {OLLAMA_API_BASE}")

if __name__ == "__main__":
    agent = MyAgent(
        provider="litellm",
        model_id="gemma3:12b-it-qat",
        api_base=OLLAMA_API_BASE,
        api_key=OLLAMA_API_KEY,
        planning_interval=3,
    )

    with open(QUESTIONS_FILEPATH, "r") as f:
        questions = json.load(f)

    answers = run_agent(agent, [questions[0]])
    print("Answers:", answers)
    print("Finished running the agent.")
