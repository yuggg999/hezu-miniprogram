"""58同城合租爬虫"""
import re
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, ScrapedPost
from utils.text_cleaner import clean_text, extract_price, extract_area


class FiftyEightScraper(BaseScraper):
    source_name = "58"
    base_url = "https://{city}.58.com"

    CITY_CODES = {
        "北京": "bj",
        "上海": "sh",
        "广州": "gz",
        "深圳": "sz",
        "成都": "cd",
        "杭州": "hz",
    }

    async def scrape(self, city: str = "北京", keyword: str = "合租") -> list[ScrapedPost]:
        city_code = self.CITY_CODES.get(city, "bj")
        url = f"https://{city_code}.58.com/hezu/"

        headers = {
            "Referer": f"https://{city_code}.58.com/",
        }

        html = await self.fetch(url, headers=headers)
        if not html:
            return []

        return self._parse_list(html, city)

    def _parse_list(self, html: str, city: str) -> list[ScrapedPost]:
        """解析58同城合租列表"""
        soup = BeautifulSoup(html, "lxml")
        posts = []

        # 58同城房源列表
        items = soup.select(".property-content-list .property-content-detail")
        if not items:
            # 备用选择器
            items = soup.select(".list-info .info-detail")

        for item in items:
            try:
                # 标题和链接
                title_el = item.select_one("a") or item.select_one(".property-content-title a")
                if not title_el:
                    continue

                title = clean_text(title_el.get_text())
                href = title_el.get("href", "")
                if not href.startswith("http"):
                    href = f"https://bj.58.com{href}"

                # 价格
                price_el = item.select_one(".property-price span") or item.select_one(".info-price")
                price = None
                if price_el:
                    price_text = clean_text(price_el.get_text())
                    price_match = re.search(r"(\d+)", price_text)
                    if price_match:
                        price = float(price_match.group(1))

                # 区域
                area_el = item.select_one(".property-area") or item.select_one(".info-area")
                area = None
                if area_el:
                    area = extract_area(clean_text(area_el.get_text()))

                posts.append(ScrapedPost(
                    title=title,
                    price=price,
                    area=area,
                    city=city,
                    source=self.source_name,
                    source_url=href,
                ))
            except Exception as e:
                print(f"[58] 解析帖子异常: {e}")
                continue

        return posts
