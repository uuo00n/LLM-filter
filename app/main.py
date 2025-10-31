from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.utils.sensitive_word_filter import sensitive_word_filter

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_db_client():
    """应用启动时连接数据库并加载敏感词"""
    await connect_to_mongo()
    await sensitive_word_filter.load_sensitive_words()

@app.on_event("shutdown")
async def shutdown_db_client():
    """应用关闭时断开数据库连接"""
    await close_mongo_connection()

@app.get("/")
async def root():
    """根路径，返回应用信息"""
    return {
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "message": "欢迎使用LLM过滤系统API"
    }