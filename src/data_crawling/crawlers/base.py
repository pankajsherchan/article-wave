from abc import ABC, abstractmethod

from core.db.documents import ArticleDocument


class BaseCrawler(ABC):
    @abstractmethod
    def extract(self, link: str) -> ArticleDocument:
        pass
