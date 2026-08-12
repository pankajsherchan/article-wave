import hashlib
from abc import ABC, abstractmethod

from feature_pipeline.models import ArticleChunkModel, ArticleCleanedModel
from feature_pipeline.utils.chunking import chunk_text


class ChunkingDataHandler(ABC):
    @abstractmethod
    def chunk(self, data_model: ArticleCleanedModel) -> list[ArticleChunkModel]:
        pass


class ArticleChunkingHandler(ChunkingDataHandler):
    def chunk(self, data_model: ArticleCleanedModel) -> list[ArticleChunkModel]:
        chunks = chunk_text(data_model.cleaned_content)

        return [
            ArticleChunkModel(
                article_id=data_model.article_id,
                chunk_id=build_chunk_id(
                    chunk=chunk,
                ),
                chunk_index=index,
                chunk_content=chunk,
                source_url=data_model.source_url,
                canonical_url=data_model.canonical_url,
                platform=data_model.platform,
                title=data_model.title,
                author=data_model.author,
                publication=data_model.publication,
                published_at=data_model.published_at,
                content_hash=data_model.content_hash,
            )
            for index, chunk in enumerate(chunks)
        ]


def build_chunk_id(chunk: str) -> str:
    chunk_id=hashlib.md5(chunk.encode()).hexdigest()
    return chunk_id
