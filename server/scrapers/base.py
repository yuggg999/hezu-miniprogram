"""爬虫基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
import httpx
import asyncio
import random
from config import get_settings

settings = get_settings()


@dataclass
class ScrapedPost:
    """爬取到的帖子数据"""
    title: str
    price: float | None = None
    area: str | None = None
    city: str = "北京"
    source: str = ""
    source_url: str = ""
    source_id: str | None = None
    images: list[str] = field(default_factory=list)
    description: str | None = None
    contact: str | None = None
    published_at: datetime | None = None


class BaseScraper(ABC):
    """爬虫基类，所有平台爬虫继承此类"""

    source_name: str = ""
    base_url: str = ""

    # 常用 User-Agent 池
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    ]

    def get_headers(self) -> dict:
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

    async def fetch(self, url: str, **kwargs) -> str | None:
        """发送 HTTP 请求"""
        headers = self.get_headers()
        headers.update(kwargs.pop("headers", {}))

        for attempt in range(settings.max_retries):
            try:
                async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
                    resp = await client.get(url, headers=headers, **kwargs)
                    resp.raise_for_status()
                    return resp.text
            except Exception as e:
                if attempt == settings.max_retries - 1:
                    print(f"[{self.source_name}] 请求失败 {url}: {e}")
                    return None
                await asyncio.sleep(random.uniform(1, 3))
        return None

    @abstractmethod
    async def scrape(self, city: str = "北京", keyword: str = "合租") -> list[ScrapedPost]:
        """爬取帖子列表，子类必须实现"""
        ...

    async def run(self, city: str = "北京", keyword: str = "合租") -> list[ScrapedPost]:
        """运行爬虫，带错误处理"""
        try:
            posts = await self.scrape(city=city, keyword=keyword)
            print(f"[{self.source_name}] 爬取到 {len(posts)} 条帖子")
            return posts
        except Exception as e:
            print(f"[{self.source_name}] 爬取异常: {e}")
            return []
