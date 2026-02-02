from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Security Service"

    # 鉴权配置 (与 Auth Service 保持一致)
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    # Dify 配置
    DIFY_API_URL: str = os.getenv("DIFY_API_URL", "http://192.168.6.6/v1")
    DIFY_API_KEY: str = os.getenv("DIFY_API_KEY", "")
    DIFY_RESPONSE_MODE: str = os.getenv("DIFY_RESPONSE_MODE", "streaming")

    # MongoDB 配置
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "security_service_db")

    # Redis 配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

    class Config:
        case_sensitive = True

settings = Settings()
