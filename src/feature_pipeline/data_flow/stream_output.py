from bytewax.outputs import DynamicSink, StatelessSinkPartition
from qdrant_client.http.models import PointStruct

from core.db.qdrant import QdrantDatabaseConnector
from feature_pipeline.models import ArticleEmbeddedChunkModel


class QdrantOutput(DynamicSink):
    def __init__(self, connection: QdrantDatabaseConnector) -> None:
        self.connection = connection
        self.connection.ensure_collection()

    def build(self, step_id: int, worker_index: int, worker_count: int) -> StatelessSinkPartition:
        return QdrantVectorDataSink(connection=self.connection)


class QdrantVectorDataSink(StatelessSinkPartition):
    def __init__(self, connection: QdrantDatabaseConnector) -> None:
        self.connection = connection

    def write_batch(self, chunks: list[ArticleEmbeddedChunkModel]) -> None:
        points = [
            PointStruct(
                id=chunk.chunk_id,
                payload=chunk.to_qdrant_payload(),
                vector=chunk.embedding,
            )
            for chunk in chunks
        ]

        if not points:
            return

        self.connection.upsert_points(points)
