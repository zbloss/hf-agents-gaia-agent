from bs4 import BeautifulSoup
from smolagents import Tool


class WebpageParser(Tool):
    name: str = "webpage_parser_tool"
    description: str = (
        "This tool parses elements from HTML to make them easily searchable."
    )
    inputs: dict[str, dict[str, str]] = {
        "html_string": {
            "type": "string",
            "description": "The HTML content as a string.",
        },
    }
    output_type: str = "array"

    def forward(self, html_string: str) -> list[str]:
        """
        Parses the HTML string and returns all elements as an array.
        """
        # Create a BeautifulSoup object
        soup = BeautifulSoup(html_string, "html.parser")

        # Extract all elements as strings
        elements = [str(element) for element in soup.find_all()]

        return elements
