"""帖子数据模型"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    price = Column(Float, nullable=True, index=True)
    area = Column(String(100), nullable=True, index=True)       # 区域，如"朝阳区"
    city = Column(String(50), nullable=False, default="北京", index=True)
    source = Column(String(50), nullable=False, index=True)     # 来源平台
    source_url = Column(String(500), nullable=False)             # 原帖链接
    source_id = Column(String(100), nullable=True)               # 平台原帖ID
    images = Column(JSON, nullable=True)                         # 图片URL列表
    description = Column(Text, nullable=True)                    # 描述内容
    contact = Column(String(200), nullable=True)                 # 联系方式
    published_at = Column(DateTime, nullable=True)               # 发布时间
    scraped_at = Column(DateTime, default=datetime.now)          # 爬取时间

    # AI 可信度字段
    credibility_score = Column(Integer, default=0)               # 总分 0-100
    price_score = Column(Integer, default=0)                     # 价格合理性
    comment_score = Column(Integer, default=0)                   # 评论区信号
    poster_score = Column(Integer, default=0)                    # 发帖人可信度
    image_score = Column(Integer, default=0)                     # 图片真实性
    completeness_score = Column(Integer, default=0)              # 内容完整度
    credibility_analysis = Column(Text, nullable=True)           # AI 分析理由

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "price": self.price,
            "area": self.area,
            "city": self.city,
            "source": self.source,
            "source_url": self.source_url,
            "source_id": self.source_id,
            "images": self.images or [],
            "description": self.description,
            "contact": self.contact,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "credibility_score": self.credibility_score,
            "credibility_detail": {
                "price": self.price_score,
                "comment": self.comment_score,
                "poster": self.poster_score,
                "image": self.image_score,
                "completeness": self.completeness_score,
                "analysis": self.credibility_analysis,
            },
        }
