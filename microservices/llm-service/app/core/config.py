from pathlib import Path
from pydantic import Field, ValidationInfo, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

def _resolve_env_files():
    """
    Resolve available .env files from project root to service root.
    Load order is far-to-near so closer files can override shared defaults.
    """
    current_file = Path(__file__).resolve()
    env_files = [parent / ".env" for parent in current_file.parents if (parent / ".env").exists()]
    if not env_files:
        return None
    return tuple(reversed(env_files))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_resolve_env_files(),
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_ignore_empty=True,
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

    @model_validator(mode="before")
    @classmethod
    def _drop_empty_env_values(cls, data):
        if isinstance(data, dict):
            return {key: value for key, value in data.items() if value != ""}
        return data

    @field_validator("ACCESS_TOKEN_EXPIRE_MINUTES", "REDIS_PORT", "REDIS_DB", mode="before")
    @classmethod
    def _fallback_numeric_defaults_for_empty_env(cls, value, info: ValidationInfo):
        if value != "":
            return value

        defaults = {
            "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
            "REDIS_PORT": 6379,
            "REDIS_DB": 0,
        }
        return defaults[info.field_name]

settings = Settings()
