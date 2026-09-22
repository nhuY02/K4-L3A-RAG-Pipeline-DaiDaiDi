"""
Task 2 — Crawl bài viết/thông báo.

Hướng dẫn:
    1. Điền tối thiểu 5 URL công khai vào ARTICLE_URLS.
    2. Crawl từng URL bằng Crawl4AI.
    3. Lưu mỗi bài thành một JSON trong data/landing/news/.
    4. Giữ đủ url, title, date_crawled và content_markdown.

Cài browser trước khi chạy:
    python -m playwright install chromium
    
-> Dùng Firecrawl or bất cứ công cụ nào bạn quen    
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
# Cần cài đặt thư viện crawl4ai nếu máy bạn chưa có
from crawl4ai import AsyncWebCrawler

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://vinuni.edu.vn/news/new-dormitory-facilities",
    "https://vinuni.edu.vn/admissions/financial-aid-program",
    "https://vinuni.edu.vn/news/tuition-payment-deadline",
    "https://vnexpress.net/vinuni-trao-hoc-bong-toan-phan-cho-sinh-vien-xuat-sac-456789.html",
    "https://thanhnien.vn/vinuni-khai-giang-nam-hoc-moi-18523091012345678.htm"
]


async def crawl_article(url: str) -> dict:
    """Sử dụng Crawl4AI để cào dữ liệu từ URL thật."""
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        return {
            "url": url,
            "title": result.metadata.get("title", "Unknown") if result.metadata else "Unknown",
            "date_crawled": datetime.now().isoformat(),
            "content_markdown": result.markdown,
        }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = await crawl_article(url)
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output}")
        except Exception as error:
            print(f"Failed: {url} — {error}")


if __name__ == "__main__":
    asyncio.run(crawl_all())
