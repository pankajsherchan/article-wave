import json


class FileHandler:
    def read_json(self, filename: str) -> list:
        try:
            with open(filename) as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{filename} does not exist.")
        except json.JSONDecodeError:
            raise json.JSONDecodeError(
                f"The file '{filename}' is not properly formatted as JSON."
            )

    def write_json(self, filename: str, data: list) -> None:
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)