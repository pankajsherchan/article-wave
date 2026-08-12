from abc import ABC, abstractmethod
from uuid import UUID

from data_cdc.events import ArticleChangeEvent
from feature_pipeline.models import ArticleCleanedModel
from feature_pipeline.utils.cleaning import clean_text


class CleaningDataHandler(ABC):
    @abstractmethod
    def clean(self, event: ArticleChangeEvent) -> ArticleCleanedModel:
        pass


class ArticleCleaningHandler(CleaningDataHandler):
    def clean(self, event: ArticleChangeEvent) -> ArticleCleanedModel:
        payload = event.payload

        return ArticleCleanedModel(
            article_id=UUID(str(event.article_id)),
            source_url=payload["source_url"],
            canonical_url=payload["canonical_url"],
            platform=payload["platform"],
            title=payload.get("title"),
            author=payload.get("author"),
            publication=payload.get("publication"),
            published_at=payload.get("published_at"),
            content_hash=payload["content_hash"],
            cleaned_content=clean_text(payload.get("content")),
        )
