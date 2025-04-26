from smolagents import LiteLLMModel, OpenAIServerModel
from dotenv import load_dotenv
load_dotenv()

model_id = "ollama_chat/gemma3:12b-it-qat"
api_base = "http://localhost:11434/v1"

# model = LiteLLMModel(
#     model_id=model_id, api_base=api_base
# )

# model = OpenAIServerModel(
#     api_base = api_base
# )

from openai import OpenAI

client = OpenAI(base_url=api_base)
models = client.models.list()
for model in models:
    print(model)
