import os
# Pydantic v2 中 BaseSettings 已迁移到 pydantic-settings
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量 (尝试向上查找 .env)
load_dotenv(verbose=True)  # 默认查找当前目录
if not os.getenv("MONGODB_URL"):
    # 如果没找到，尝试向上级目录查找（本地开发场景）
    load_dotenv(dotenv_path="../../.env")
    load_dotenv(dotenv_path="../../../.env") # 备用：防止层级变动

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "LLM过滤系统"
    API_V1_STR: str = "/api/v1"
    APP_BASE_URL: str = os.getenv("APP_BASE_URL", "http://localhost:8000")
    
    # 数据库配置
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DB_NAME: str = os.getenv("DB_NAME", "llm_filter_db")
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key_here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Ollama配置
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama2")

    # Dify配置
    DIFY_API_URL: str = os.getenv("DIFY_API_URL", "http://192.168.6.6/v1")
    DIFY_API_KEY: str = os.getenv("DIFY_API_KEY", "app-sLnrbNjEi1GiTDGgL2B2DwLZ")
    DIFY_RESPONSE_MODE: str = os.getenv("DIFY_RESPONSE_MODE", "streaming")
    DIFY_MESSAGE_ENDPOINT: str = os.getenv("DIFY_MESSAGE_ENDPOINT", "chat-messages")

    # 应用运行模式开关：仅运行教育版或企业版之一
    # 允许的值："edu" / "biz"；若未设置则默认使用 "edu"
    # 注意：不再提供混合模式（mixed），如需混合请显式设置并在依赖中放行
    APP_MODE: str = os.getenv("APP_MODE", "edu")
    CORS_ALLOWED_ORIGINS: str = os.getenv("CORS_ALLOWED_ORIGINS", "*")
    GITHUB_DEFAULT_REPO: str = os.getenv("GITHUB_DEFAULT_REPO", "")
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    
    # 学期配置
    TERM_START_DATE: str = os.getenv("TERM_START_DATE", "2025-09-01")  # 默认开学日期

    # Redis 配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

settings = Settings()
