from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Security Service"
    
    # 鉴权配置 (与 Auth Service 保持一致)
    JWT_SECRET: str = "llm_filter_secure_secret_key_2025_update_must_be_32_bytes"
    ALGORITHM: str = "HS256"
    
    # Dify 配置
    DIFY_API_URL: str = "http://datacenter.dldzxx.cn:8089/v1"
    DIFY_API_KEY: str = "app-lkK33EQOVXXrjD9x3SKbItr7"
    
    # MongoDB 配置
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "security_service_db"
    
    class Config:
        case_sensitive = True

settings = Settings()
