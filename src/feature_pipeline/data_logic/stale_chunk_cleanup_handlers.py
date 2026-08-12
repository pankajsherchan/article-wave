from abc import ABC, abstractmethod

from qdrant_client.http.models import FieldCondition, Filter, MatchValue

from core.db.qdrant import QdrantDatabaseConnector
from data_cdc.events import ArticleChangeEvent, ArticleEventType


class StaleChunkCleanupHandler(ABC):
    @abstractmethod
    def cleanup(self, event: ArticleChangeEvent) -> ArticleChangeEvent:
        pass


class ArticleStaleChunkCleanupHandler(StaleChunkCleanupHandler):
    def __init__(self, connection: QdrantDatabaseConnector | None = None) -> None:
        self.connection = connection or QdrantDatabaseConnector()

    def cleanup(self, event: ArticleChangeEvent) -> ArticleChangeEvent:
        if event.event_type not in {ArticleEventType.UPDATED, ArticleEventType.DELETED}:
            return event

        self.connection.delete_by_filter(
            Filter(
                must=[
                    FieldCondition(
                        key="article_id",
                        match=MatchValue(value=str(event.article_id)),
                    )
                ]
            )
        )

        return event