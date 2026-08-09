import hashlib
from datetime import datetime
from urllib.parse import urlparse

import httpx
import trafilatura
from trafilatura.metadata import extract_metadata

from core.db.documents import ArticleDocument
from data_crawling.crawlers.base import BaseCrawler


class CustomArticleCrawler(BaseCrawler):
    model = ArticleDocument
    platform: str | None = None

    def extract(self, link: str) -> ArticleDocument:
        response = httpx.get(
            link,
            follow_redirects=True,
            timeout=20,
            headers={"User-Agent": "ArticleWave/0.1"},
        )
        response.raise_for_status()

        html = response.text
        metadata = extract_metadata(html)

        content = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False,
        )

        if not content:
            raise ValueError(f"Could not extract article content from: {link}")

        normalized_content = content.strip()
        canonical_url = metadata.url if metadata and metadata.url else str(response.url)
        content_hash = self._content_hash(normalized_content)
        existing_article = self.model.find(canonical_url=canonical_url)

        article_data = {
            "source_url": link,
            "canonical_url": canonical_url,
            "platform": self.platform or self._platform_from_url(canonical_url),
            "title": metadata.title if metadata else None,
            "author": metadata.author if metadata else None,
            "publication": metadata.sitename if metadata else None,
            "published_at": self._published_at(metadata.date if metadata else None),
            "content": normalized_content,
            "content_hash": content_hash,
            "metadata": {
                "description": metadata.description if metadata else None,
                "hostname": metadata.hostname if metadata else None,
            },
        }

        if existing_article is not None:
            article_data["id"] = existing_article.id

        article = self.model(**article_data)

        if existing_article is not None:
            if existing_article.content_hash == content_hash:
                return existing_article

            article.replace()
            return article

        article.save()

        return article

    def _content_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _platform_from_url(self, url: str) -> str:
        host = urlparse(url).netloc.lower()

        if "medium.com" in host:
            return "medium"

        if "substack.com" in host:
            return "substack"

        return "custom_article"

    def _published_at(self, value: str | None) -> datetime | None:
        if not value:
            return None

        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
