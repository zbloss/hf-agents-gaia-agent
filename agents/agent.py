from smolagents import (
    CodeAgent,
    DuckDuckGoSearchTool,
    WikipediaSearchTool,
    LiteLLMModel,
    Tool,
)
from tools.text_search import TextSearch
from tools.text_splitter import text_splitter
from tools.video_analyzer import WebVideoAnalyzerTool
from typing import Callable

class MyAgent:
    def __init__(
        self,
        provider: str = "litellm",
        model_id: str = "gemini/gemini-2.0-flash-lite",
        api_base: str | None = None,
        api_key: str | None = None,
        planning_interval: int = 3,
        num_ctx: int = 8192,
        tools: list[Tool] = [],
        add_base_tools: bool = True,
        temperature: float = 0.2,
        additional_authorized_imports: list[str] = [],
        step_callbacks: list[Callable] = [],
        max_steps: int = 20,
        verbosity_level: int = 2,
    ):
        """
        Initializes the agent depending on the provider and model ID.
        Args:
            provider (str): The provider of the model (e.g., "litellm", "huggingface").
            model_id (str): The ID of the model to be used.
            tools (list[Tool]): The tools to be used by the agent.
            api_base (str | None): The base URL of the API.
            api_key (str | None): The API key.
            planning_interval (int): The interval for planning.
            num_ctx (int): The number of context tokens.
            add_base_tools (bool): Whether to add base tools.
            temperature (float): The temperature for the model.
            additional_authorized_imports (list[str]): The additional authorized imports.
            step_callbacks (list[Callable]): The step callbacks.
            max_steps (int): The maximum steps.
            verbosity_level (int): The verbosity level.
        Returns:
            None: None
        """
        self.provider = provider
        self.model_id = model_id
        self.api_base = api_base
        self.api_key = api_key
        self.planning_interval = planning_interval
        self.num_ctx = num_ctx
        self.temperature = temperature

        model = LiteLLMModel(
            model_id=self.model_id,
            api_base=self.api_base,
            api_key=self.api_key,
            num_ctx=self.num_ctx,
            add_base_tools=add_base_tools,
            temperature=self.temperature,
        )

        # Initialize the agent with the specified provider and model ID
        if provider == "litellm":
            self.agent = CodeAgent(
                model=model,
                tools=tools,
                planning_interval=self.planning_interval,
                additional_authorized_imports=additional_authorized_imports,
                step_callbacks=step_callbacks,
                max_steps=max_steps,
                verbosity_level=verbosity_level,
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        print(f"Agent initialized with provider: {provider}, model ID: {model_id}")

    def __call__(self, question: str) -> str:
        """
        Given a question, run the agent and return the answer.

        Args:
            question (str): The question to be answered.
        Returns:
            str: The answer to the question.
        """

        final_answer = self.agent.run(question)
        print(f"Agent received question (first 50 chars): {question[:50]}...")
        print(f"Agent returning fixed answer: {final_answer}")
        return final_answer
