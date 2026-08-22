from pydantic_settings import BaseSettings, SettingsConfigDict


class TrainingSettings(BaseSettings):
    AWS_REGION: str = "us-east-1"
    AWS_ARN_ROLE: str | None = None

    HUGGINGFACE_ACCESS_TOKEN: str | None = None
    HUGGINGFACE_WORKSPACE: str | None = None

    COMET_API_KEY: str | None = None
    COMET_WORKSPACE: str | None = None
    COMET_PROJECT: str = "article-wave"

    DATASET_ID: str = "articles-instruct-dataset"
    BASE_MODEL_NAME: str = "unsloth/tinyllama-bnb-4bit"

    TRAINING_INSTANCE_TYPE: str = "ml.g5.2xlarge"
    TRAINING_INSTANCE_COUNT: int = 1
    TRAINING_VOLUME_SIZE: int = 100
    TRAINING_MAX_RUN_SECONDS: int = 3600 * 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


training_settings = TrainingSettings()
