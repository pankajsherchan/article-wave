from data_crawling.crawlers.custom_article import CustomArticleCrawler


class SubstackCrawler(CustomArticleCrawler):
    platform = "substack"
