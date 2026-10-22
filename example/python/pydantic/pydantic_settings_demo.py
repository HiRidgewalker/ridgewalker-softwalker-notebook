"""
pydantic-settings 演示：从 .env / 环境变量加载配置

依赖：
    uv add pydantic-settings

跑：
    uv run python example/python/pydantic/pydantic_settings_demo.py
"""
import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ===== 1. 基础用法 =====
class Settings(BaseSettings):
    app_name: str = "demo"
    database_url: str
    debug: bool = False
    port: int = 8000
    allowed_hosts: list[str] = Field(default_factory=list)

    model_config = SettingsConfigDict(
        env_file=".env",                    # 读 .env 文件
        env_file_encoding="utf-8",
        env_prefix="APP_",                  # 环境变量前缀：APP_DATABASE_URL 等
        extra="ignore",                     # 多余的环境变量忽略
        case_sensitive=False,               # 大小写不敏感
    )


# .env 示例（与本文件同目录或项目根目录）：
# APP_DATABASE_URL=postgresql://localhost/mydb
# APP_DEBUG=true
# APP_PORT=9000
# APP_ALLOWED_HOSTS=["localhost","example.com"]

# ===== 2. 嵌套 settings =====
class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_", env_file=".env", extra="ignore")
    url: str = "sqlite:///db.sqlite3"
    pool_size: int = 5


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")
    app_name: str = "demo"
    database: DatabaseSettings = DatabaseSettings()


# APP_DATABASE_URL / DB_URL 都能影响嵌套的 database.url


# ===== 3. 用 lru_cache 单例（FastAPI 推荐）=====
from functools import lru_cache


@lru_cache
def get_settings() -> Settings:
    return Settings()


# FastAPI 里：
# from fastapi import Depends
# @app.get("/info")
# def info(settings: Settings = Depends(get_settings)):
#     return {"app": settings.app_name}


if __name__ == "__main__":
    # 优先级：函数参数 > 环境变量 > .env 文件 > 类默认值
    settings = Settings()
    print(settings.app_name)
    print(settings.database_url)
    print(settings.debug)
    print(settings.port)
    print(settings.allowed_hosts)

    nested = AppSettings()
    print(nested.app_name, nested.database.url)
