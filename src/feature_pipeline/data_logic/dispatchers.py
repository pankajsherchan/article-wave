from data_cdc.events import ArticleChangeEvent
from feature_pipeline.data_logic.chunking_data_handlers import ArticleChunkingHandler
from feature_pipeline.data_logic.cleaning_data_handlers import ArticleCleaningHandler
from feature_pipeline.data_logic.embedding_data_handlers import ArticleEmbeddingHandler
from feature_pipeline.data_logic.stale_chunk_cleanup_handlers import ArticleStaleChunkCleanupHandler
from feature_pipeline.models import (
    ArticleChunkModel,
    ArticleCleanedModel,
    ArticleEmbeddedChunkModel,
)

class RawDispatcher:
    @staticmethod
    def handle_mq_message(message: dict) -> ArticleChangeEvent:
        return ArticleChangeEvent(**message)

class StaleChunkCleanupDispatcher:
    cleaning_state_chunks_handler = ArticleStaleChunkCleanupHandler()

    @classmethod
    def clean_stale_chunks(cls, event: ArticleChangeEvent) -> ArticleChangeEvent: 
        return cls.cleaning_state_chunks_handler.cleanup(event)


class CleaningDispatcher:
    cleaning_handler = ArticleCleaningHandler()

    @classmethod
    def dispatch_cleaner(cls, event: ArticleChangeEvent) -> ArticleCleanedModel:
        return cls.cleaning_handler.clean(event)


class ChunkingDispatcher:
    chunking_handler = ArticleChunkingHandler()

    @classmethod
    def dispatch_chunker(
        cls, data_model: ArticleCleanedModel
    ) -> list[ArticleChunkModel]:
        return cls.chunking_handler.chunk(data_model)


class EmbeddingDispatcher:
    embedding_handler = ArticleEmbeddingHandler()

    @classmethod
    def dispatch_embedder(
        cls, data_model: ArticleChunkModel
    ) -> ArticleEmbeddedChunkModel:
        return cls.embedding_handler.embed(data_model)

