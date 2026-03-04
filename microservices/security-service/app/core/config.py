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
    )

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Security Service"

    # 鉴权配置 (与 Auth Service 保持一致)
    JWT_SECRET: str = ""
    ALGORITHM: str = "HS256"

    # Dify 配置
    DIFY_API_URL: str = "http://192.168.6.6/v1"
    # 使用别名从环境变量 DIFY_API_KEY_SECURITY 读取
    DIFY_API_KEY: str = Field("", alias="DIFY_API_KEY_SECURITY")
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

settings = Settings()
