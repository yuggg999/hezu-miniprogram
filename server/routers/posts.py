"""帖子相关 API 路由"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc
from database import get_db
from models.post import Post

router = APIRouter(prefix="/api/posts", tags=["posts"])

# 来源平台映射
SOURCE_MAP = {
    "douban": "豆瓣",
    "xianyu": "闲鱼",
    "58": "58同城",
    "xiaohongshu": "小红书",
    "weibo": "微博",
}


@router.get("")
async def list_posts(
    city: str = Query("北京", description="城市"),
    source: Optional[str] = Query(None, description="来源平台"),
    area: Optional[str] = Query(None, description="区域"),
    min_price: Optional[float] = Query(None, description="最低价格"),
    max_price: Optional[float] = Query(None, description="最高价格"),
    min_credibility: Optional[int] = Query(None, ge=0, le=100, description="最低可信度"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=50, description="每页数量"),
    db: AsyncSession = Depends(get_db),
):
    """获取帖子列表（分页 + 筛选）"""
    query = select(Post).where(Post.city == city)

    if source:
        query = query.where(Post.source == source)
    if area:
        query = query.where(Post.area.contains(area))
    if min_price is not None:
        query = query.where(Post.price >= min_price)
    if max_price is not None:
        query = query.where(Post.price <= max_price)
    if min_credibility is not None:
        query = query.where(Post.credibility_score >= min_credibility)

    # 总数
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # 分页
    query = query.order_by(desc(Post.scraped_at)).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    posts = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [p.to_dict() for p in posts],
    }


@router.get("/search")
async def search_posts(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    city: str = Query("北京", description="城市"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """搜索帖子"""
    query = (
        select(Post)
        .where(Post.city == city)
        .where(
            or_(
                Post.title.contains(q),
                Post.description.contains(q),
                Post.area.contains(q),
            )
        )
    )

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(desc(Post.scraped_at)).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    posts = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [p.to_dict() for p in posts],
    }


@router.get("/sources")
async def list_sources():
    """获取支持的平台列表"""
    return {"sources": SOURCE_MAP}


@router.get("/{post_id}")
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    """获取帖子详情"""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    return post.to_dict()
