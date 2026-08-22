import json
from pathlib import Path

from comet_ml import Artifact, start
from core.db.qdrant import QdrantDatabaseConnector
from feature_pipeline.generate_dataset.chunk_documents import chunk_documents
from feature_pipeline.generate_dataset.file_handler import FileHandler
from feature_pipeline.generate_dataset.llm_communication import GptCommunicator
from core.config import settings
from sklearn.model_selection import train_test_split

client = QdrantDatabaseConnector()


class DataFormatter:
    @classmethod
    def get_system_prompt(cls, data_type: str) -> str:
        return (
            f"I will give you batches of contents of {data_type}. "
            f"Please generate me exactly 1 instruction for each of them. "
            f"The {data_type} text for which you have to generate the instructions "
            f"is under Content number x lines. Please structure the answer in json "
            f"format, ready to be loaded by json.loads(), a list of objects only "
            f"with fields called instruction and content. For the content field, "
            f"copy the number of the content only!. Please do not add any extra "
            f"characters and make sure it is a list with objects in valid json format!\n"
        )

    @classmethod
    def format_data(cls, data_points: list, is_example: bool, start_index: int) -> str:
        text = ""

        for index, data_point in enumerate(data_points):
            if not is_example:
                text += f"Content number {start_index + index}\n"

            text += str(data_point) + "\n"

        return text

    @classmethod
    def format_batch(cls, context_msg: str, data_points: list, start_index: int) -> str:
        delimiter_msg = context_msg
        delimiter_msg += cls.format_data(data_points, False, start_index)

        return delimiter_msg


    @classmethod
    def format_prompt(
        cls,
        inference_posts: list,
        data_type: str,
        start_index: int,
    ) -> str:
        initial_prompt = cls.get_system_prompt(data_type)

        initial_prompt += (
            f"You must generate exactly a list of {len(inference_posts)} json "
            f"objects, using the contents provided under CONTENTS FOR GENERATION\n"
        )

        initial_prompt += cls.format_batch(
            "\nCONTENTS FOR GENERATION: \n",
            inference_posts,
            start_index,
        )

        return initial_prompt


class DatasetGenerator:
    def __init__(
        self,
        file_handler: FileHandler,
        api_communicator: GptCommunicator,
        data_formatter: DataFormatter,
    ) -> None:
        self.file_handler = file_handler
        self.api_communicator = api_communicator
        self.data_formatter = data_formatter

    def generate_training_data(
        self,
        collection_name: str,
        data_type: str,
        batch_size: int = 3,
    ) -> None:

        assert (
            settings.COMET_API_KEY
        ), "COMET_API_KEY must be set in settings, fill it in your .env file."
        assert (
            settings.COMET_WORKSPACE
        ), "COMET_WORKSPACE must be set in settings, fill it in your .env file."
        assert (
            settings.OPENAI_API_KEY
        ), "OPENAI_API_KEY must be set in settings, fill it in your .env file."

        cleaned_documents = self.fetch_all_cleaned_content(collection_name)
        cleaned_documents = chunk_documents(cleaned_documents)

        generated_instruct_dataset = []

        for i in range(0, len(cleaned_documents), batch_size):
            batch = cleaned_documents[i : i + batch_size]
            prompt = self.data_formatter.format_prompt(
                inference_posts=batch,
                data_type=data_type,
                start_index=i,
            )

            batch_instructions = self.api_communicator.send_prompt(prompt)

            if len(batch_instructions) != len(batch):
                continue

            for instruction, content in zip(batch_instructions, batch, strict=False):
                instruction["content"] = content
                generated_instruct_dataset.append(instruction)

        dataset_split = self._split_dataset(generated_instruct_dataset)
        self.push_to_comet(
            dataset_split=dataset_split,
            data_type=data_type,
            collection_name=collection_name,
        )


    def _split_dataset(
        self,
        generated_instruct_dataset: list[dict],
        test_size: float = 0.1,
    ) -> tuple[list[dict], list[dict]]:
        if len(generated_instruct_dataset) == 0:
            return [], []

        train_data, test_data = train_test_split(
            generated_instruct_dataset,
            test_size=test_size,
            random_state=42,
        )

        return train_data, test_data

    def push_to_comet(
        self,
        dataset_split: tuple[list[dict], list[dict]],
        data_type: str,
        collection_name: str,
        output_dir: Path = Path("generated_dataset"),
    ) -> None:
        output_dir.mkdir(exist_ok=True)

        try:
            experiment = start(
                api_key=settings.COMET_API_KEY,
                workspace=settings.COMET_WORKSPACE,
                project_name=settings.COMET_PROJECT,
            )

            training_data, testing_data = dataset_split

            file_name_training_data = output_dir / f"{collection_name}_training.json"
            file_name_testing_data = output_dir / f"{collection_name}_testing.json"

            with file_name_training_data.open("w") as file:
                json.dump(training_data, file)

            with file_name_testing_data.open("w") as file:
                json.dump(testing_data, file)

            artifact = Artifact(f"{data_type}-instruct-dataset")
            artifact.add(file_name_training_data)
            artifact.add(file_name_testing_data)

            experiment.log_artifact(artifact)
            experiment.end()

        except Exception:
            pass

    def fetch_all_cleaned_content(self, collection_name: str) -> list[str]:
        article_chunks: dict[str, list[tuple[int, str]]] = {}

        scroll_response = client.scroll(collection_name=collection_name, limit=10000)
        points = scroll_response[0]

        for point in points:
            payload = point.payload or {}

            article_id = payload.get("article_id")
            chunk_index = payload.get("chunk_index")
            cleaned_content = payload.get("content")

            if article_id is None or chunk_index is None:
                continue

            if cleaned_content:
                article_chunks.setdefault(article_id, []).append(
                    (chunk_index, cleaned_content)
                )

        all_cleaned_contents = []

        for chunks in article_chunks.values():
            sorted_chunks = sorted(chunks, key=lambda chunk: chunk[0])
            all_cleaned_contents.append(
                "\n".join(chunk_content for _, chunk_content in sorted_chunks)
            )

        return all_cleaned_contents

if __name__ == "__main__":
    file_handler = FileHandler()
    api_communicator = GptCommunicator()
    data_formatter = DataFormatter()

    dataset_generator = DatasetGenerator(
        file_handler=file_handler,
        api_communicator=api_communicator,
        data_formatter=data_formatter,
    )

    collections = [
        (settings.QDRANT_COLLECTION_NAME, "articles"),
    ]

    for collection_name, data_type in collections:
        dataset_generator.generate_training_data(
            collection_name=collection_name,
            data_type=data_type,
        )