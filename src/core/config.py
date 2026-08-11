from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGO_DATABASE_HOST: str = (
        "mongodb://mongo1:30001,mongo2:30002,mongo3:30003/"
        "?replicaSet=my-replica-set"
    )
    MONGO_DATABASE_NAME: str = "article_wave"
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5673
    RABBITMQ_DEFAULT_USERNAME: str = "guest"
    RABBITMQ_DEFAULT_PASSWORD: str = "guest"
    RABBITMQ_QUEUE_NAME: str = "article_events"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
