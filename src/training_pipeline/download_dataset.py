import json
from pathlib import Path

from comet_ml import Experiment
from datasets import Dataset
from comet_ml.artifacts import ArtifactAsset

class DatasetClient:
    def __init__(self, output_dir: Path = Path("./finetuning_dataset")) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_dataset(self, dataset_id: str, split: str = "train") -> Dataset:
        assert split in ["train", "test"], "Split must be either 'train' or 'test'"

        if "/" in dataset_id:
            tokens = dataset_id.split("/")
            assert (
                len(tokens) == 2
            ), (
                f"Wrong format for {dataset_id}. Expected "
                "'comet_workspace/comet_artifact_name'"
            )

            workspace, artifact_name = tokens
            experiment = Experiment(workspace=workspace)
        else:
            artifact_name = dataset_id
            experiment = Experiment()

        artifact = self._download_artifact(artifact_name, experiment)
        asset = self._artifact_to_asset(artifact, split)
        dataset = self._load_data(asset)

        experiment.end()

        return dataset

    def _download_artifact(self, artifact_name: str, experiment) -> object:
        try:
            logged_artifact = experiment.get_artifact(artifact_name)
            artifact = logged_artifact.download(self.output_dir)
        except Exception as exc:
            print(f"Error retrieving artifact: {str(exc)}")
            raise

        print(f"Successfully downloaded {artifact_name} at {self.output_dir}")

        return artifact

    def _artifact_to_asset(self, artifact: object, split: str) -> ArtifactAsset:
        if len(artifact.assets) == 0:
            raise RuntimeError("Artifact has no assets")

        if len(artifact.assets) != 2:
            raise RuntimeError(
                f"Artifact has {len(artifact.assets)} assets, expected 2."
            )

        print(f"Picking split = '{split}'")
        asset = [asset for asset in artifact.assets if split in asset.logical_path][0]

        return asset

    def _load_data(self, asset: ArtifactAsset) -> Dataset:
        data_file_path = asset.local_path_or_data

        with open(data_file_path) as file:
            data = json.load(file)

        dataset_dict = {key: [str(row[key]) for row in data] for key in data[0].keys()}
        dataset = Dataset.from_dict(dataset_dict)

        print(f"Loaded dataset samples = {len(dataset)}")

        return dataset
