from pathlib import Path

from pydantic import AliasChoices, Field, ValidationInfo, field_validator, model_validator
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
    )

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Security Service"

    # 鉴权配置 (与 Auth Service 保持一致)
    JWT_SECRET: str = ""
    ALGORITHM: str = "HS256"

    # Dify 配置
    DIFY_API_URL: str = "http://192.168.6.6/v1"
    # 优先读取 DIFY_API_KEY_SECURITY，兼容旧变量 DIFY_API_KEY
    DIFY_API_KEY: str = Field("", validation_alias=AliasChoices("DIFY_API_KEY_SECURITY", "DIFY_API_KEY"))
    DIFY_RESPONSE_MODE: str = "streaming"

    # MongoDB 配置
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "security_service_db"

    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # Zabbix 配置
    ZABBIX_URL: str = "http://localhost"
    ZABBIX_USERNAME: str = "Admin"
    ZABBIX_PASSWORD: str = "zabbix"
    
    # 数据同步配置
    ZABBIX_SYNC_INTERVAL: int = 3600
    ZABBIX_AUTO_SYNC: bool = True

    @model_validator(mode="before")
    @classmethod
    def _drop_empty_env_values(cls, data):
        if isinstance(data, dict):
            return {key: value for key, value in data.items() if value != ""}
        return data

    @field_validator("REDIS_PORT", "REDIS_DB", "ZABBIX_SYNC_INTERVAL", mode="before")
    @classmethod
    def _fallback_numeric_defaults_for_empty_env(cls, value, info: ValidationInfo):
        if value != "":
            return value

        defaults = {
            "REDIS_PORT": 6379,
            "REDIS_DB": 0,
            "ZABBIX_SYNC_INTERVAL": 3600,
        }
        return defaults[info.field_name]

    @field_validator("ZABBIX_AUTO_SYNC", mode="before")
    @classmethod
    def _fallback_bool_default_for_empty_env(cls, value):
        if value == "":
            return True
        return value

settings = Settings()
