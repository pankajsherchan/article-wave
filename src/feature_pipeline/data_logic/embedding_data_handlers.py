from abc import ABC, abstractmethod

from feature_pipeline.models import ArticleChunkModel, ArticleEmbeddedChunkModel
from feature_pipeline.utils.embeddings import embed_text


class EmbeddingDataHandler(ABC):
    @abstractmethod 
    def embed(self, data_model: ArticleChunkModel) -> ArticleEmbeddedChunkModel: 
        pass

class ArticleEmbeddingHandler(EmbeddingDataHandler):
    def embed(self, data_model: ArticleChunkModel) -> ArticleEmbeddedChunkModel:
        return ArticleEmbeddedChunkModel(
            article_id=data_model.article_id,
            chunk_id=data_model.chunk_id,
            chunk_index=data_model.chunk_index,
            chunk_content=data_model.chunk_content,
            source_url=data_model.source_url,
            canonical_url=data_model.canonical_url,
            platform=data_model.platform,
            title=data_model.title,
            author=data_model.author,
            publication=data_model.publication,
            published_at=data_model.published_at,
            content_hash=data_model.content_hash,
            heading=data_model.heading,
            embedding=embed_text(data_model.chunk_content),
        )

    