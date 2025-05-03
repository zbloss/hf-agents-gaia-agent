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
    - If the web search only returns titles and short snippets, you MUST visit the actual webpage to read the full content before answering.
    - Use the `WikipediaParser` tool to fetch and read the Wikipedia page when necessary.
    - You just have the ability to read Wikipedia pages only.
    - If the task requires reading, listening, or analyzing a file, you must use the file specified in the `file_name` field of the task metadata, not the file name mentioned casually inside the question text.
    - Comma separated lists MUST contain a single space after each comma.
    - If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise.
    - If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise.
    - If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string.
    - Only answer after you have gathered enough information by reading the actual page contents.
    - Once you have the final answer, you must call `final_answer("your_answer")` immediately after printing it.
    - Do not retry or execute anything else after calling `final_answer`.
    - `final_answer` must wrap the exact printed value.
    Provide ONLY the precise answer requested. 
    Do not include explanations, steps, reasoning, or additional text. 
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
