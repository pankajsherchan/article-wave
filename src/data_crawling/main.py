import argparse
from pprint import pprint

from data_crawling.dispatcher import CrawlerDispatcher


def crawl_article(link: str) -> None:
    dispatcher = CrawlerDispatcher()
    crawler = dispatcher.get_crawler(link)

    article = crawler.extract(link)

    pprint(article.model_dump())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crawl a public Medium or Substack article URL."
    )
    parser.add_argument("url", help="Public Medium or Substack article URL to crawl.")
    args = parser.parse_args()

    crawl_article(args.url)


if __name__ == "__main__":
    main()
