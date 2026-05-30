"""合租小程序 API 入口"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import health, posts
from config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("🚀 合租小程序 API 启动中...")
    await init_db()
    print("✅ 数据库初始化完成")
    yield
    print("👋 应用关闭")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置（小程序需要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router)
app.include_router(posts.router)


# 手动触发爬虫刷新的接口
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.aggregator import AggregatorService


@app.post("/api/posts/refresh")
async def refresh_posts(
    city: str = "北京",
    db: AsyncSession = Depends(get_db),
):
    """手动触发爬虫刷新"""
    aggregator = AggregatorService()
    result = await aggregator.refresh(db, city=city)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)