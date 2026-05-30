"""豆瓣合租小组爬虫"""
import re
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, ScrapedPost
from utils.text_cleaner import clean_text, extract_price, extract_area


class DoubanScraper(BaseScraper):
    source_name = "douban"
    base_url = "https://www.douban.com"

    # 豆瓣租房小组 ID（以北京为例，可扩展）
    GROUP_IDS = {
        "北京": "279962",
        "上海": "263422",
        "广州": "278012",
        "深圳": "263423",
    }

    async def scrape(self, city: str = "北京", keyword: str = "合租") -> list[ScrapedPost]:
        group_id = self.GROUP_IDS.get(city, self.GROUP_IDS["北京"])
        url = f"{self.base_url}/group/{group_id}/discussion"
        params = {"type": "rec", "start": 0}

        html = await self.fetch(url, params=params)
        if not html:
            return []

        return self._parse_list(html, city)

    def _parse_list(self, html: str, city: str) -> list[ScrapedPost]:
        """解析帖子列表页"""
        soup = BeautifulSoup(html, "html.parser")
        posts = []

        # 豆瓣小组帖子列表
        table = soup.find("table", class_="olt")
        if not table:
            return []

        rows = table.find_all("tr")
        for row in rows:
            try:
                title_cell = row.find("td", class_="title")
                if not title_cell:
                    continue

                link = title_cell.find("a")
                if not link:
                    continue

                title = clean_text(link.get_text())
                href = link.get("href", "")

                # 过滤非合租帖
                if "合租" not in title and "找室友" not in title:
                    continue

                # 提取帖子ID
                source_id = None
                id_match = re.search(r"/discussion/(\d+)", href)
                if id_match:
                    source_id = id_match.group(1)

                # 提取价格
                price = extract_price(title)

                # 提取区域
                area = extract_area(title)

                # 提取时间
                time_cell = row.find("td", class_="time")
                published_at = None
                if time_cell:
                    time_text = clean_text(time_cell.get_text())
                    try:
                        published_at = datetime.strptime(time_text, "%m-%d %H:%M")
                        published_at = published_at.replace(year=datetime.now().year)
                    except ValueError:
                        pass

                posts.append(ScrapedPost(
                    title=title,
                    price=price,
                    area=area,
                    city=city,
                    source=self.source_name,
                    source_url=href,
                    source_id=source_id,
                    published_at=published_at,
                ))
            except Exception as e:
                print(f"[douban] 解析帖子异常: {e}")
                continue

        return posts

    async def scrape_detail(self, url: str) -> dict | None:
        """爬取帖子详情页"""
        html = await self.fetch(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")
        content = soup.find("div", class_="topic-content")
        if not content:
            return None

        text = clean_text(content.get_text())
        images = []
        for img in content.find_all("img"):
            src = img.get("src", "")
            if src and "doubanio.com" in src:
                images.append(src)

        return {
            "description": text,
            "images": images,
            "contact": self._extract_contact(text),
        }

    def _extract_contact(self, text: str) -> str | None:
        """提取联系方式"""
        # 微信号
        wx_match = re.search(r"[微信Vv][信x号X]?\s*[：:]?\s*(\w+)", text)
        if wx_match:
            return f"微信: {wx_match.group(1)}"

        # 手机号
        phone_match = re.search(r"1[3-9]\d{9}", text)
        if phone_match:
            return phone_match.group(0)

        return None
