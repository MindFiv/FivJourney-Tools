import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用基础配置
    PROJECT_NAME: str = "FIVC Journey"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./fivc_journey.db"

    # 安全配置
    SECRET_KEY: str = "your-secret-key-here-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS配置
    ALLOWED_HOSTS: List[str] = ["*"]

    # 调试模式
    DEBUG: bool = True

    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    class Config:
        env_file = "config.env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
