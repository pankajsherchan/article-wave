from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import UUID4, BaseModel, ConfigDict, Field

from core.db.mongo import connection
from pymongo import ASCENDING, errors


_database = connection.get_database()


class BaseDocument(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_mongo(cls, data: dict):
        if not data:
            return data

        document_id = data.pop("_id", None)

        return cls(**dict(data, id=document_id))


    def to_mongo(self, **kwargs) -> dict:
        # Understand how these two work? 
        exclude_unset = kwargs.pop("exclude_unset", False)
        by_alias = kwargs.pop("by_alias", True)

        parsed = self.model_dump(
            exclude_unset=exclude_unset,
            by_alias=by_alias,
            **kwargs,
        )

        if "_id" not in parsed and "id" in parsed:
            parsed["_id"] = str(parsed.pop("id"))

        return parsed

    def save(self, **kwargs):
        collection = _database[self._get_collection_name()]

        try:
            result = collection.insert_one(self.to_mongo(**kwargs))
            return result.inserted_id
        except errors.WriteError:
            return None

    def replace(self, **kwargs):
        collection = _database[self._get_collection_name()]

        try:
            result = collection.replace_one(
                {"_id": str(self.id)},
                self.to_mongo(**kwargs),
            )
            return result.modified_count
        except errors.WriteError:
            return None

    @classmethod
    def ensure_indexes(cls) -> None:
        collection = _database[cls._get_collection_name()]

        for index in getattr(cls.Settings, "indexes", []):
            collection.create_index(
                index["fields"],
                **index.get("options", {}),
            )

    @classmethod
    def find(cls, **filter_options):
        collection = _database[cls._get_collection_name()]

        try:
            instance = collection.find_one(filter_options)

            if instance:
                return cls.from_mongo(instance)

            return None
        except errors.OperationFailure:
            return None

    @classmethod
    def _get_collection_name(cls) -> str:
        if not hasattr(cls, "Settings") or not hasattr(cls.Settings, "name"):
            raise RuntimeError(
                "Document should define a Settings class with collection name."
            )

        return cls.Settings.name
    



class ArticleDocument(BaseDocument):
    id: UUID = Field(default_factory=uuid4)

    source_url: str
    canonical_url: str
    platform: str

    title: str | None = None
    author: str | None = None
    publication: str | None = None
    published_at: datetime | None = None

    content: str
    content_hash: str

    ingested_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings: 
        name = "articles"
        indexes = [
            {
                "fields": [("canonical_url", ASCENDING)],
                "options": {
                    "name": "uq_articles_canonical_url",
                    "unique": True,
                },
            },
            {
                "fields": [("content_hash", ASCENDING)],
                "options": {"name": "idx_articles_content_hash"},
            },
            {
                "fields": [("platform", ASCENDING), ("canonical_url", ASCENDING)],
                "options": {"name": "idx_articles_platform_canonical_url"},
            },
        ]
