from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ArticleEventType(StrEnum):
    CREATED = "article.created"
    UPDATED = "article.updated"
    DELETED = "article.deleted"


class ArticleChangeEvent(BaseModel):
    event_type: ArticleEventType
    article_id: UUID
    canonical_url: str
    content_hash: str | None = None
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = Field(default_factory=dict)
