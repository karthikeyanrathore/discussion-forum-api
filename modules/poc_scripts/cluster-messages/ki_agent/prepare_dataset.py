#!/usr/bin/env python3

from pathlib import Path
import asyncio
from crawl4ai import AsyncWebCrawler
import re

_BOILERPLATE_PATTERNS = [
    re.compile(r"(cookie|privacy) policy.*?\n", re.IGNORECASE),
    re.compile(r"subscribe to our newsletter.*?\n", re.IGNORECASE),
    re.compile(r"\[.*?]\(https?://.*?\)"),           # bare markdown links
    re.compile(r"!\[.*?]\(.*?\)"),                   # markdown images
    re.compile(r"-{3,}"),                            # long horizontal rules
    re.compile(r"\n{3,}", re.MULTILINE),             # triple+ blank lines
]

def spawn_url_crawler(urls):
    async def _crawl_website(urls):
        tasks = [_crawl_single(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

    async def _crawl_single(url):
        try:
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await crawler.arun(url=url)
                if not result.success:
                    print("  Crawl failed for %s: %s", url, result.error_message)
                    return None
                return {
                    "text": result.markdown or "",
                    "source_url": url,
                    "doc_title": result.metadata.get("title", url) if result.metadata else url,
                    "source_type": "web",
                    "page_count": None,
                    "used_ocr": False,
                }
        except Exception as exc:
            print("  Exception crawling %s: %s", url, exc)
            return None

    return asyncio.run(_crawl_website(urls))

def clean_text(text):
    for pat in _BOILERPLATE_PATTERNS:
        text = pat.sub("\n", text)
    # normalise whitespace inside lines
    lines = [" ".join(line.split()) for line in text.splitlines()]
    text = "\n".join(lines)
    return text.strip()

if __name__ == "__main__":
    urls = [
        "https://www.b-tu.de/en/artificial-intelligence-ms/faq",
        "https://www.b-tu.de/en/study/during-studies/study-organization/formalities/registering-for-the-following-semester",
    ]
    documents = []
    if urls:
        documents = (spawn_url_crawler(urls))
        assert len(documents) == len(urls), "Missing some URLs data"
        for doc in documents:
            # print(doc["text"])
            doc["text"] = clean_text(doc["text"])
        # print(documents) 

        print(documents[1]["text"])

