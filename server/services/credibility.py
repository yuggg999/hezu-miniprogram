"""AI 可信度评分服务"""
import json
import re
from openai import AsyncOpenAI
from config import get_settings

settings = get_settings()


class CredibilityService:
    """基于 AI 的帖子可信度评分"""

    def __init__(self):
        self.client = None
        if settings.ai_api_key:
            self.client = AsyncOpenAI(
                api_key=settings.ai_api_key,
                base_url=settings.ai_base_url,
            )

    async def evaluate(self, post) -> dict:
        """评估帖子可信度"""
        # 1. 规则引擎基础评分
        rule_score = self._rule_based_score(post)

        # 2. AI 深度分析（如果有配置 API key）
        ai_score = None
        if self.client:
            ai_score = await self._ai_evaluate(post)

        # 3. 综合评分
        if ai_score:
            return self._merge_scores(rule_score, ai_score)

        return rule_score

    def _rule_based_score(self, post) -> dict:
        """基于规则的评分"""
        scores = {
            "price": 50,
            "comment": 50,
            "poster": 50,
            "image": 50,
            "completeness": 50,
        }

        title = post.title or ""
        desc = post.description or ""

        # 价格合理性
        if post.price:
            if 500 <= post.price <= 8000:
                scores["price"] = 80
            elif 300 <= post.price <= 15000:
                scores["price"] = 60
            else:
                scores["price"] = 30  # 价格异常偏低或偏高

        # 内容完整度
        completeness = 40
        if title and len(title) > 5:
            completeness += 15
        if desc and len(desc) > 20:
            completeness += 15
        if post.area:
            completeness += 10
        if post.contact:
            completeness += 10
        if post.images:
            completeness += 10
        scores["completeness"] = min(completeness, 100)

        # 图片真实性（有图片加分）
        if post.images and len(post.images) >= 2:
            scores["image"] = 70
        elif post.images:
            scores["image"] = 55

        # 负面关键词检测
        negative_keywords = ["骗子", "假的", "诈骗", "黑中介", "虚假", "套路"]
        full_text = f"{title} {desc}"
        for kw in negative_keywords:
            if kw in full_text:
                scores["comment"] = 20
                break

        # 正面信号
        positive_keywords = ["个人", "房东直租", "真实", "急转", "随时看房"]
        for kw in positive_keywords:
            if kw in full_text:
                scores["poster"] = min(scores["poster"] + 10, 90)

        total = sum(scores.values()) // len(scores)

        return {
            "total": total,
            **scores,
            "analysis": self._generate_analysis(scores, post),
        }

    async def _ai_evaluate(self, post) -> dict | None:
        """使用 AI 进行深度分析"""
        prompt = f"""你是一个合租信息可信度分析专家。请分析以下帖子的可信度。

帖子信息：
- 标题：{post.title}
- 价格：{post.price}元/月
- 区域：{post.area}
- 来源：{post.source}
- 描述：{post.description or '无'}
- 联系方式：{post.contact or '无'}
- 图片数量：{len(post.images) if post.images else 0}

请从以下维度评分（0-100），并给出分析理由：
1. price: 价格合理性（对比同区域市场价）
2. comment: 评论区信号（根据描述中的信息判断）
3. poster: 发帖人可信度（根据描述的专业度判断）
4. image: 图片真实性（根据描述判断）
5. completeness: 内容完整度

请严格以 JSON 格式返回，示例：
{{"price": 80, "comment": 60, "poster": 70, "image": 50, "completeness": 85, "analysis": "分析理由..."}}"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.ai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500,
            )
            content = response.choices[0].message.content
            # 提取 JSON
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"[credibility] AI 评分异常: {e}")

        return None

    def _merge_scores(self, rule_score: dict, ai_score: dict) -> dict:
        """合并规则评分和 AI 评分"""
        weights = {"price": 0.4, "comment": 0.3, "poster": 0.3, "image": 0.3, "completeness": 0.2}
        merged = {}
        total_sum = 0
        count = 0

        for key in ["price", "comment", "poster", "image", "completeness"]:
            rule_val = rule_score.get(key, 50)
            ai_val = ai_score.get(key, 50)
            weight = weights.get(key, 0.5)
            merged[key] = int(rule_val * (1 - weight) + ai_val * weight)
            total_sum += merged[key]
            count += 1

        merged["total"] = total_sum // count
        merged["analysis"] = ai_score.get("analysis", rule_score.get("analysis", ""))

        return merged

    def _generate_analysis(self, scores: dict, post) -> str:
        """生成分析文本"""
        parts = []
        if scores["price"] >= 70:
            parts.append("价格合理")
        elif scores["price"] <= 40:
            parts.append("价格异常")

        if scores["completeness"] >= 70:
            parts.append("信息完整")
        elif scores["completeness"] <= 40:
            parts.append("信息不完整")

        if scores["image"] >= 70:
            parts.append("有实拍图")
        elif scores["image"] <= 30:
            parts.append("缺少图片")

        if not parts:
            return "暂无详细分析"

        return "，".join(parts) + "。"
