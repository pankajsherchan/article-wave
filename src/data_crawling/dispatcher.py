from urllib.parse import urlparse

from data_crawling.crawlers.base import BaseCrawler
from data_crawling.crawlers.medium import MediumCrawler
from data_crawling.crawlers.substack import SubstackCrawler


class CrawlerDispatcher:
    def __init__(self) -> None:
        self._crawlers: dict[str, type[BaseCrawler]] = {
            "medium": MediumCrawler,
            "substack": SubstackCrawler,
        }

    def get_crawler(self, url: str) -> BaseCrawler:
        platform = self._detect_platform(url)
        crawler = self._crawlers.get(platform)

        if crawler is None:
            raise ValueError(f"Unsupported article platform: {url}")

        return crawler()

    def _detect_platform(self, url: str) -> str:
        host = urlparse(url).netloc.lower()

        if host == "medium.com" or host.endswith(".medium.com"):
            return "medium"

        if host == "substack.com" or host.endswith(".substack.com"):
            return "substack"

        raise ValueError(f"Unsupported article platform: {host}")
