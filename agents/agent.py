from smolagents import (
    CodeAgent,
    DuckDuckGoSearchTool,
    WikipediaSearchTool,
    LiteLLMModel,
)
from tools.text_search import TextSearch
from tools.text_splitter import text_splitter
from tools.video_analyzer import YouTubeObjectCounterTool


class MyAgent:
    def __init__(
        self,
        provider: str = "litellm",
        model_id: str = "ollama_chat/gemma3:12b-it-qat",
        api_base: str | None = None,
        api_key: str | None = None,
        planning_interval: int = 3,
        num_ctx: int = 8192,
    ):
        """
        Initializes the agent depending on the provider and model ID.
        Args:
            provider (str): The provider of the model (e.g., "litellm", "huggingface").
            model_id (str): The ID of the model to be used.
        Returns:
            None: None
        """
        self.provider = provider
        self.model_id = model_id
        self.api_base = api_base
        self.api_key = api_key
        self.planning_interval = planning_interval
        self.num_ctx = num_ctx

        model = LiteLLMModel(
            model_id=self.model_id,
            api_base=self.api_base,
            api_key=self.api_key,
            num_ctx=self.num_ctx,
            add_base_tools=True,
        )

        tools = [
            DuckDuckGoSearchTool(),  # Search tool for web queries
            WikipediaSearchTool(),  # Search tool for Wikipedia queries
            TextSearch(),  # Search tool for text queries
            text_splitter,  # Text splitter tool for breaking down large texts
            # into manageable lists.
            YouTubeObjectCounterTool(),  # Tool for analyzing YouTube videos
        ]

        # Initialize the agent with the specified provider and model ID
        if provider == "litellm":
            self.agent = CodeAgent(
                model=model,
                tools=tools,
                planning_interval=planning_interval,
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
