from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, Filter, PointStruct, VectorParams

from core.config import settings


class QdrantDatabaseConnector:
    def __init__(self) -> None:
        self.client = QdrantClient(
            host=settings.QDRANT_DATABASE_HOST,
            port=settings.QDRANT_DATABASE_PORT,
        )

    def ensure_collection(self) -> None:
        existing = self.client.collection_exists(settings.QDRANT_COLLECTION_NAME)

        if existing:
            return

        self.client.create_collection(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(
                size=settings.EMBEDDING_SIZE,
                distance=Distance.COSINE,
            ),
        )

    def upsert_points(self, points: list[PointStruct]) -> None:
        self.ensure_collection()
        self.client.upsert(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points=points,
        )

    def delete_by_filter(self, points_filter: Filter) -> None:
        self.ensure_collection()
        self.client.delete(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points_selector=points_filter,
        )