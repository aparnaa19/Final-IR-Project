# Scrapy-based web crawler for Wikipedia pages (demo corpus)

import scrapy
from pathlib import Path
from scrapy.crawler import CrawlerProcess

class WikipediaIRSpider(scrapy.Spider):  # Wikipedia spider - crawls IR-related pages with depth limit and politeness settings 
    name = "wikipedia_ir"
    start_urls = ["https://en.wikipedia.org/wiki/Information_retrieval"]
    
    custom_settings = {
        "DEPTH_LIMIT": 2,
        "CLOSESPIDER_PAGECOUNT": 100,
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 1.0,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1.0,
        "AUTOTHROTTLE_MAX_DELAY": 5.0,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
        "LOG_LEVEL": "INFO",
        "USER_AGENT": "IRCourseCrawler/1.0 (student project)",
    }
    
    def __init__(self, output_dir="data/wiki_corpus", *args, **kwargs):  # Initialize spider and set output directory for saving HTML files
        super().__init__(*args, **kwargs)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.page_counter = 0
    
    def parse(self, response): # Parse page, save HTML, and follow valid Wikipedia links
        self.page_counter += 1  # Save page with incremental naming
        page_id = f"page_{self.page_counter:03d}"
        filepath = self.output_dir / f"{page_id}.html"
        
        filepath.write_bytes(response.body)
        self.logger.info(f"Saved {filepath} ({response.url})")
        
        # Follow internal Wikipedia links only
        excluded_prefixes = (
            "/wiki/Special:", "/wiki/Talk:", "/wiki/Help:",
            "/wiki/Wikipedia:", "/wiki/File:", "/wiki/Category:"
        )
        
        for href in response.css("a::attr(href)").getall():
            if href.startswith("/wiki/") and not any(
                href.startswith(prefix) for prefix in excluded_prefixes
            ):
                yield response.follow(href, callback=self.parse)


def run_crawler(output_dir="data/wiki_corpus"):
    # Run the Wikipedia crawler and save pages to specified directory
    process = CrawlerProcess()
    process.crawl(WikipediaIRSpider, output_dir=output_dir)
    process.start()


if __name__ == "__main__":
    # Run crawler when script is executed directly
    print("Starting Wikipedia crawler")
    run_crawler()
    print("Crawling complete")