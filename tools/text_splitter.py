from smolagents import tool


@tool
def text_splitter(text: str, separator: str = "\n") -> list[str]:
    """
    Splits the input text string into a list on `separator` which
    defaults to the newline character. This is useful for when
    you need to browse through a large text file that may contain
    a list your are interested in.


    Args:
        text (str): The input text to be split.
        separator (str): The character(s) to split `text` on.

    Returns:
        list[str]: A list of text chunks.
    """
    # Split the text into chunks of the specified size
    return text.split(separator)
