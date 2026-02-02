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

    # Zabbix 配置
    ZABBIX_URL: str = os.getenv("ZABBIX_URL", "http://localhost/zabbix/api_jsonrpc.php")
    ZABBIX_USERNAME: str = os.getenv("ZABBIX_USERNAME", "Admin")
    ZABBIX_PASSWORD: str = os.getenv("ZABBIX_PASSWORD", "zabbix")
    
    # 数据同步配置
    ZABBIX_SYNC_INTERVAL: int = int(os.getenv("ZABBIX_SYNC_INTERVAL", "3600"))  # 1小时
    ZABBIX_AUTO_SYNC: bool = os.getenv("ZABBIX_AUTO_SYNC", "true").lower() == "true"

    class Config:
        case_sensitive = True

settings = Settings()
