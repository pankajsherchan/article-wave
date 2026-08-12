import bytewax.operators as op
from bytewax.dataflow import Dataflow

from core.db.qdrant import QdrantDatabaseConnector
from data_cdc.events import ArticleEventType
from feature_pipeline.data_flow.stream_input import RabbitMQSource
from feature_pipeline.data_flow.stream_output import QdrantOutput
from feature_pipeline.data_logic.dispatchers import (
    ChunkingDispatcher,
    CleaningDispatcher,
    EmbeddingDispatcher,
    RawDispatcher,
    StaleChunkCleanupDispatcher
)


connection = QdrantDatabaseConnector()

flow = Dataflow("Article Wave feature pipeline")

stream = op.input("input", flow, RabbitMQSource())
stream = op.map("raw dispatch", stream, RawDispatcher.handle_mq_message)
stream = op.map(
    "cleanup stale chunks",
    stream,
    StaleChunkCleanupDispatcher.clean_stale_chunks
)
stream = op.filter(
    "skip deleted events",
    stream,
    lambda event: event.event_type != ArticleEventType.DELETED,
)
stream = op.map("clean data", stream, CleaningDispatcher.dispatch_cleaner)
stream = op.flat_map("chunk data", stream, ChunkingDispatcher.dispatch_chunker)
stream = op.map("embedd data", stream, EmbeddingDispatcher.dispatch_embedder)

op.output(
    "embedded article chunks to qdrant",
    stream,
    QdrantOutput(connection=connection),
)
