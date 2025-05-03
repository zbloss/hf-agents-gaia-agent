from smolagents import Tool
import os
import json
import csv
import openpyxl
import whisper
import requests


class OpenFilesTool(Tool):
    name = "open_files_tool"
    description = (
        "This tool opens files and returns their content as a string. "
        "It can handle text, CSV, JSON, XLSX, and MP3 file types."
    )
    inputs = {
        "file_path": {
            "type": "string",
            "description": "The path to the file to be opened.",
        },
        "file_type": {
            "type": "string",
            "description": "The type of the file (text, csv, json, xlsx, mp3). Default is 'text'.",
            "nullable": True,
        },
    }
    output_type = "string"


    def download_file(self, file_name: str) -> None:
        if not os.path.exists(file_name):
            url = f"https://agents-course-unit4-scoring.hf.space/files/{file_name.split('.')[0]}"
            r = requests.get(url)
            with open(file_name, "wb") as f:
                f.write(r.content)


    def open_file_as_text(self, file_name: str, filetype: str = "txt") -> str:
        """
        Opens a file and returns its content as readable text.
        Supports 'txt', 'json', 'csv', 'xlsx', and 'mp3' (transcribes speech to text).
        Args:
            file_name (str): The path or name of the file.
            filetype (Optional[str]): Type of file ('txt', 'json', 'csv', 'xlsx', 'mp3'). Defaults to 'txt'.
        Returns:
            str: The content of the file as text, or transcribed speech if 'mp3'.
        """
        self.download_file(file_name)
        try:
            if filetype == "txt":
                with open(file_name, "r", encoding="utf-8") as f:
                    return f.read()

            elif filetype == "json":
                with open(file_name, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return json.dumps(data, indent=2)

            elif filetype == "csv":
                with open(file_name, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                return "\n".join([", ".join(row) for row in rows])

            elif filetype == "xlsx":
                wb = openpyxl.load_workbook(file_name, data_only=True)
                sheet = wb.active
                content = []
                for row in sheet.iter_rows(values_only=True):
                    content.append(", ".join(str(cell) if cell is not None else "" for cell in row))
                return "\n".join(content)

            elif filetype == "mp3":
                w = whisper.load_model("base")
                res = w.transcribe(file_name)
                return res["text"]

            else:
                return f"Unsupported filetype '{filetype}'. Supported types are 'txt', 'json', 'csv', 'xlsx', and 'mp3'."

        except FileNotFoundError:
            return f"File '{file_name}' not found."
        except Exception as e:
            return f"Error opening file '{file_name}': {str(e)}"

    def forward(self, file_path: str, file_type: str = "text") -> str:
        """
        Opens a file and returns its content as a string.
        Args:
            file_path (str): The path to the file to be opened.
            file_type (str): The type of the file (text, csv, json, xlsx, mp3). Default is 'text'.
        Returns:
            str: The content of the file as a string.
        """
        return self.open_file_as_text(file_path, file_type)
