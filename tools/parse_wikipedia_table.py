from smolagents import Tool
import requests
from bs4 import BeautifulSoup, Tag


class WikipediaParser(Tool):
    name: str = "wikipedia_parser_tool"
    description: str = (
        "This tool parse a Wikipedia page into a clean, readable text format."
    )
    inputs: dict[str, dict[str, str]] = {
        "url": {
            "type": "string",
            "description": "The Wikipedia page url.",
        }
    }
    output_type: str = "string"

    def get_wikipedia_page(self, url: str) -> str:
        """
        Fetches the content of a Wikipedia page given its URL.
        Args:
            url (str): The URL of the Wikipedia page.
        Returns:
            str: The HTML content of the page.
        """

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        content_div = soup.find("div", id="mw-content-text")
        if not content_div:
            return "Content not found."

        elements: list[str] = []
        h_tags: list[str] = [f"h{i}" for i in range(1, 6)]
        extra_tags: list[str] = ["p", "ul", "ol"]
        html_tags: list[str] = h_tags + extra_tags

        for elem in content_div.find_all(html_tags):
            if elem.name in h_tags:
                elements.append("\n\n" + elem.get_text(strip=True) + "\n")
            elif elem.name in extra_tags:
                elements.append(elem.get_text(strip=True))
            elif elem.name == "table":
                elements.append(self.parse_wikipedia_table(elem))

        return "\n\n".join(elements)

    def parse_wikipedia_table(table: Tag) -> str:
        """
        Parses a Wikipedia table into a clean, readable text format.
        Args:
            table (Tag): BeautifulSoup Tag for the table.
        Returns:
            str: Formatted table as readable text.
        """
        rows = []
        headers = []

        # Try to get headers
        thead = table.find("thead")
        if thead:
            for th in thead.find_all("th"):
                header_text = th.get_text(separator=" ", strip=True)
                headers.append(header_text)
            if headers:
                rows.append(" | ".join(headers))

        # Parse table body rows
        tbody = table.find("tbody")
        if not tbody:
            tbody = table  # fallback: some tables have no tbody explicitly

        for tr in tbody.find_all("tr"):
            cells = tr.find_all(["th", "td"])
            cell_texts = []
            for cell in cells:
                # Clean references like [7], [note 1], etc.
                for sup in cell.find_all("sup", class_="reference"):
                    sup.decompose()

                text = cell.get_text(separator=" ", strip=True)
                cell_texts.append(text)

            if cell_texts:
                row_text = " | ".join(cell_texts)
                rows.append(row_text)

        return "\n".join(rows)

    def forward(self, url: str) -> str:
        """
        Parses the Wikipedia page and returns the content as a string.
        Args:
            url (str): The URL of the Wikipedia page.
        Returns:
            str: The parsed content of the page.
        """
        html_string = self.get_wikipedia_page(url)
        return html_string
