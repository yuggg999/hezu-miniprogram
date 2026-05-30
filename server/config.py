"""应用配置"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 应用配置
    app_name: str = "合租小程序 API"
    debug: bool = True

    # 数据库
    database_url: str = "sqlite+aiosqlite:///./hezu.db"

    # 爬虫配置
    scrape_interval_minutes: int = 30
    request_timeout: int = 15
    max_retries: int = 3

    # AI 评分配置 (兼容 OpenAI 接口的服务均可)
    ai_api_key: str = ""
    ai_base_url: str = "https://api.deepseek.com"
    ai_model: str = "deepseek-chat"

    # 城市配置
    default_city: str = "北京"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
