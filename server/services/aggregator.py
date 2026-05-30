"""帖子聚合服务 - 整合多平台爬虫数据"""
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.post import Post
from scrapers.douban import DoubanScraper
from scrapers.fifty_eight import FiftyEightScraper
from scrapers.base import ScrapedPost
from services.credibility import CredibilityService


class AggregatorService:
    """聚合服务：运行所有爬虫，去重，存入数据库"""

    def __init__(self):
        self.scrapers = [
            DoubanScraper(),
            FiftyEightScraper(),
        ]
        self.credibility_service = CredibilityService()

    async def refresh(self, db: AsyncSession, city: str = "北京") -> dict:
        """刷新所有平台数据"""
        all_posts: list[ScrapedPost] = []

        # 并发运行所有爬虫
        tasks = [scraper.run(city=city) for scraper in self.scrapers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_posts.extend(result)

        # 去重并存入数据库
        new_count = 0
        for scraped in all_posts:
            exists = await self._exists(db, scraped.source, scraped.source_id or scraped.source_url)
            if exists:
                continue

            post = Post(
                title=scraped.title,
                price=scraped.price,
                area=scraped.area,
                city=scraped.city,
                source=scraped.source,
                source_url=scraped.source_url,
                source_id=scraped.source_id,
                images=scraped.images,
                description=scraped.description,
                contact=scraped.contact,
                published_at=scraped.published_at,
                scraped_at=datetime.now(),
            )

            # AI 可信度评分
            try:
                score = await self.credibility_service.evaluate(post)
                post.credibility_score = score["total"]
                post.price_score = score["price"]
                post.comment_score = score["comment"]
                post.poster_score = score["poster"]
                post.image_score = score["image"]
                post.completeness_score = score["completeness"]
                post.credibility_analysis = score["analysis"]
            except Exception as e:
                print(f"[aggregator] AI评分失败: {e}")
                post.credibility_score = 50  # 默认分数
                post.credibility_analysis = "AI评分暂时不可用"

            db.add(post)
            new_count += 1

        await db.commit()
        return {
            "total_scraped": len(all_posts),
            "new_added": new_count,
            "sources": [s.source_name for s in self.scrapers],
        }

    async def _exists(self, db: AsyncSession, source: str, identifier: str) -> bool:
        """检查帖子是否已存在"""
        query = select(Post).where(
            Post.source == source,
            (Post.source_id == identifier) | (Post.source_url == identifier),
        )
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
