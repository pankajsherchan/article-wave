import argparse
from pathlib import Path

from training_pipeline.config import training_settings

from sagemaker.huggingface import HuggingFace

finetuning_dir = Path(__file__).resolve().parent
finetuning_requirements_path = finetuning_dir / "requirements.txt"



def run_finetuning_on_sagemaker(is_dummy: bool = False) -> None:
    if not training_settings.AWS_ARN_ROLE:
        raise ValueError("AWS_ARN_ROLE must be set in .env")

    if not training_settings.HUGGINGFACE_ACCESS_TOKEN:
        raise ValueError("HUGGINGFACE_ACCESS_TOKEN must be set in .env")

    if not training_settings.HUGGINGFACE_WORKSPACE:
        raise ValueError("HUGGINGFACE_WORKSPACE must be set in .env")

    if not training_settings.COMET_API_KEY:
        raise ValueError("COMET_API_KEY must be set in .env")

    if not training_settings.COMET_WORKSPACE:
        raise ValueError("COMET_WORKSPACE must be set in .env")

    if not finetuning_requirements_path.exists():
        raise FileNotFoundError(
            f"The file {finetuning_requirements_path} does not exist."
        )

    hyperparameters = {
        "base_model_name": training_settings.BASE_MODEL_NAME,
        "dataset_id": training_settings.DATASET_ID,
        "model_output_huggingface_workspace": training_settings.HUGGINGFACE_WORKSPACE,
        "num_train_epochs": 3,
        "per_device_train_batch_size": 2,
        "learning_rate": 3e-4,
    }

    if is_dummy:
        hyperparameters["is_dummy"] = True


    huggingface_estimator = HuggingFace(
        entry_point="finetune.py",
        source_dir=str(finetuning_dir),
        instance_type=training_settings.TRAINING_INSTANCE_TYPE,
        instance_count=training_settings.TRAINING_INSTANCE_COUNT,
        role=training_settings.AWS_ARN_ROLE,
        transformers_version="4.36",
        pytorch_version="2.1",
        py_version="py310",
        hyperparameters=hyperparameters,
        requirements_file=str(finetuning_requirements_path),
        environment={
            "HF_TOKEN": training_settings.HUGGINGFACE_ACCESS_TOKEN,
            "HUGGINGFACE_HUB_TOKEN": training_settings.HUGGINGFACE_ACCESS_TOKEN,
            "HUGGING_FACE_HUB_TOKEN": training_settings.HUGGINGFACE_ACCESS_TOKEN,
            "COMET_API_KEY": training_settings.COMET_API_KEY,
            "COMET_WORKSPACE": training_settings.COMET_WORKSPACE,
            "COMET_PROJECT": training_settings.COMET_PROJECT,
        },
        max_run=training_settings.TRAINING_MAX_RUN_SECONDS,
        volume_size=training_settings.TRAINING_VOLUME_SIZE,
    )

    huggingface_estimator.fit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--is-dummy", action="store_true", help="Run in dummy mode")
    args = parser.parse_args()

    run_finetuning_on_sagemaker(is_dummy=args.is_dummy)
