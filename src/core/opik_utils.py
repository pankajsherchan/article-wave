import json
import os
import random
import tempfile
from pathlib import Path

from core.config import settings
from tqdm import tqdm

try:
    import opik
    from comet_ml import Experiment
    from opik.configurator.configure import OpikConfigurator
except ImportError:
    print("Could not import Opik and Comet.")


def configure_opik() -> None:
    if settings.COMET_API_KEY and settings.COMET_PROJECT:
        if settings.COMET_WORKSPACE:
            default_workspace = settings.COMET_WORKSPACE
        else:
            try:
                client = OpikConfigurator(api_key=settings.COMET_API_KEY)
                default_workspace = client._get_default_workspace()
            except Exception:
                print(
                    "Default workspace not found. Setting workspace to None and "
                    "enabling interactive mode."
                )
                default_workspace = None

        os.environ["OPIK_PROJECT_NAME"] = settings.COMET_PROJECT

        opik.configure(
            api_key=settings.COMET_API_KEY,
            workspace=default_workspace,
            use_local=False,
            force=True,
        )
    else:
        print("COMET_API_KEY and COMET_PROJECT are not set")


def create_dataset_from_artifacts(
    dataset_name: str, artifact_names: list[str]
) -> opik.Dataset | None:
    client = opik.Opik()
    try:
        dataset = client.get_dataset(name=dataset_name)
    except Exception:
        dataset = None

    if dataset:
        return dataset

    experiment = Experiment(
        workspace=settings.COMET_WORKSPACE,
        project_name=settings.COMET_PROJECT,
        api_key=settings.COMET_API_KEY,
    )
    dataset_items = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        for artifact_name in tqdm(artifact_names):
            artifact_dir = Path(tmp_dir) / artifact_name
            try:
                logged_artifact = experiment.get_artifact(artifact_name)
                logged_artifact.download(str(artifact_dir))
            except Exception:
                continue

            testing_artifact_file = list(artifact_dir.glob("*_testing.json"))
            assert (
                len(testing_artifact_file) == 1
            ), "Expected exactly one testing artifact file."
            testing_artifact_file = testing_artifact_file[0]

            with open(testing_artifact_file, "r") as file:
                items = json.load(file)

            enhanced_items = [
                {**item, "artifact_name": artifact_name} for item in items
            ]
            dataset_items.extend(enhanced_items)
    experiment.end()

    if len(dataset_items) == 0:
        return None

    dataset = create_dataset(
        name=dataset_name,
        description="Dataset created from artifacts",
        items=dataset_items,
    )

    return dataset


def create_dataset(name: str, description: str, items: list[dict]) -> opik.Dataset:
    client = opik.Opik()

    dataset = client.get_or_create_dataset(name=name, description=description)
    dataset.insert(items)

    dataset = client.get_dataset(name=name)
    return dataset


def add_to_dataset_with_sampling(item: dict, dataset_name: str) -> bool:
    if "1" in random.choices(["0", "1"], weights=[0.3, 0.7]):
        client = opik.Opik()
        dataset = client.get_or_create_dataset(name=dataset_name)
        dataset.insert([item])

        return True

    return False
