from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    _ROOT_ENV_PATH = Path(__file__).resolve().parents[4] / ".env"
    _SERVICE_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

    model_config = SettingsConfigDict(
        env_file=(_ROOT_ENV_PATH, _SERVICE_ENV_PATH),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # 应用配置
    APP_NAME: str = "LLM过滤系统"
    API_V1_STR: str = "/api/v1"
    APP_BASE_URL: str = "http://localhost:8000"

    # 数据库配置
    MONGODB_URL: str = "mongodb://localhost:27017"
    DB_NAME: str = "llm_filter_db"

    # JWT配置
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Ollama配置
    OLLAMA_BASE_URL: str = "http://192.168.6.6:11434/"
    OLLAMA_MODEL: str = "deepseek-r1:14b"

    # Dify配置
    DIFY_API_URL: str = "http://192.168.6.6/v1"
    # 使用别名从环境变量 DIFY_API_KEY_LLM 读取，代码中仍通过 settings.DIFY_API_KEY 访问
    DIFY_API_KEY: str = Field("", alias="DIFY_API_KEY_LLM")
    DIFY_RESPONSE_MODE: str = "streaming"
    DIFY_MESSAGE_ENDPOINT: str = "chat-messages"

    # 应用运行模式开关：仅运行教育版或企业版之一
    # 允许的值："edu" / "biz"；若未设置则默认使用 "edu"
    # 注意：不再提供混合模式（mixed），如需混合请显式设置并在依赖中放行
    APP_MODE: str = "edu"
    CORS_ALLOWED_ORIGINS: str = "*"
    GITHUB_DEFAULT_REPO: str = ""
    GITHUB_TOKEN: str = ""

    # 学期配置
    TERM_START_DATE: str = "2025-09-01"  # 默认开学日期

    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

settings = Settings()
