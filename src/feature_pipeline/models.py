from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ArticleCleanedModel(BaseModel):
    article_id: UUID
    source_url: str
    canonical_url: str
    platform: str

    title: str | None = None
    author: str | None = None
    publication: str | None = None
    published_at: datetime | None = None

    content_hash: str
    cleaned_content: str


class ArticleChunkModel(BaseModel):
    article_id: UUID
    chunk_id: str
    chunk_index: int
    chunk_content: str

    source_url: str
    canonical_url: str
    platform: str

    title: str | None = None
    author: str | None = None
    publication: str | None = None
    published_at: datetime | None = None

    content_hash: str
    heading: str | None = None


class ArticleEmbeddedChunkModel(ArticleChunkModel):
    embedding: list[float] = Field(default_factory=list)

    def to_qdrant_payload(self) -> dict:
        return {
            "article_id": str(self.article_id),
            "chunk_id": self.chunk_id,
            "chunk_index": self.chunk_index,
            "content": self.chunk_content,
            "source_url": self.source_url,
            "canonical_url": self.canonical_url,
            "platform": self.platform,
            "title": self.title,
            "author": self.author,
            "publication": self.publication,
            "published_at": (
                self.published_at.isoformat() if self.published_at else None
            ),
            "content_hash": self.content_hash,
            "heading": self.heading,
        }
