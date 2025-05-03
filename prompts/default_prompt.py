def generate_prompt(question_text, file_name):
    """
    Generates a prompt for the agent based on the provided question text and file name.

    Args:
        question_text (str): The question to be answered.
        file_name (str): The name of the file to be used in the task.

    Returns:
        str: The generated prompt.
    """
    # Define the full prompt with instructions and guidelines

    full_prompt = f"""You are a highly precise answering agent.
    When given a question:
    - If necessary, perform a web search using the tool `DuckDuckGoSearchTool` to find possible sources of information.
    - Use the `visit_webpage` tool to visit the webpage and extract the content in markdown format.
    - Use the `WikipediaSearchTool` to search for any information on Wikipedia, this will return HTML content. You need to then use the `WikipediaParser` tool to parse the HTML content into a clean, readable text format.
    - If the file_name provided ends in ".py", use the `PythonInterpreterTool` to execute the code in the file and return the output.
    - Use the `PythonInterpreterTool` to execute any Python code snippets you generate.
    - Use the `TextSearch` tool to search for a substring within a string.
    - Use the `text_splitter` tool to split a string into smaller chunks of text.
    - If the task requires reading, listening, or analyzing a file, you must use the file specified in the `file_name` field of the task metadata, not the file name mentioned casually inside the question text. Use the `OpenFilesTool` to open the file and read its content.
    - Once you have the final answer, you must call `final_answer("your_answer")` immediately after printing it.
    - Do not retry or execute anything else after calling `final_answer`.
    Be direct and specific. GAIA benchmark requires exact matching answers.
    Example: if asked "What is the capital of France?", respond exactly:
    Thoughts: I need to retrieve the capital of France from Wikipedia and output it directly.
    Code:
    ```py
    print("Paris")
    ```<end_code>
    Based on the above guidelines, answer the following question:
    --begin of question--
    {question_text}
    --end of question--
    If the questions mentions the need to use a file, use the following `file_name` value as the `file_name` parameter in any function calls:
    file_name: {file_name}"""
    return full_prompt
