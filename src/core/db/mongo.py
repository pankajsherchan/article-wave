from pymongo import MongoClient
from pymongo.database import Database

from core.config import settings


class MongoDatabaseConnector:
    """Singleton class to connect to MongoDB database."""

    _client: MongoClient | None = None

    def __new__(cls, *args, **kwargs):
        if cls._client is None:
            cls._client = MongoClient(settings.MONGO_DATABASE_HOST)

        return super().__new__(cls)

    def get_database(self) -> Database:
        assert self._client is not None, "Database connection not initialized"

        return self._client[settings.MONGO_DATABASE_NAME]

    def close(self) -> None:
        if self._client:
            self._client.close()


connection = MongoDatabaseConnector()