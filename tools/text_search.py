from smolagents import Tool


class TextSearch(Tool):
    name: str = "text_search_tool"
    description: str = "This tool searches through a string for substrings and returns the indices of all occurances of that substring."
    inputs: dict[str, dict[str, str]] = {
        "source_text": {
            "type": "string",
            "description": "The large text to search through.",
        },
        "search_text": {
            "type": "string",
            "description": "The text to search for within source_text.",
        },
    }
    output_type: str = "array"

    def forward(self, source_text: str, search_text: str) -> list[int]:
        """
        Searches for all occurances of `search_text` in `source_text` and returns the indices of all occurances.
        """

        # drop case sensitivity
        source_text = source_text.lower()
        search_text = search_text.lower()

        indices = []
        # Find all indices of search_text in source_text
        index = source_text.find(search_text)
        while index != -1:
            indices.append(index)
            index = source_text.find(search_text, index + 1)
        return indices
