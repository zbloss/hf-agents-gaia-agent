from agents.agent import MyAgent
from utils import run_agent

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
    "num_ctx": OLLAMA_NUM_CTX,
}

print(f"Using args: {myagent_args}")

if __name__ == "__main__":
    agent = MyAgent(**myagent_args)

    with open(QUESTIONS_FILEPATH, "r") as f:
        questions = json.load(f)

    answers = run_agent(agent, [questions[1]])
    print("Answers:", answers)
    print("Finished running the agent.")
