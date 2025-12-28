from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.utils.sensitive_word_filter import sensitive_word_filter

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=(
        "LLM 过滤系统后端接口\n\n"
        "本服务仅包含 LLM 对话与敏感词管理功能。\n"
        "认证与用户管理请访问 Auth Service (8081)。\n"
        "教务数据管理请访问 Edu Service (8082)。"
    ),
    openapi_tags=[
        {"name": "管理员", "description": "管理员功能（敏感词、分类等）"},
        {"name": "对话", "description": "对话与敏感词审计接口"},
    ],
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=None,  # 禁用默认的/docs
    redoc_url=None,  # 禁用默认的/redoc
    contact={
        "name": "LLM Filter Team",
        "url": settings.APP_BASE_URL,
        "email": "huangjunbo1107@outlook.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)

origins_cfg = settings.CORS_ALLOWED_ORIGINS
origins = [o.strip() for o in origins_cfg.split(",") if o.strip()] if origins_cfg and origins_cfg != "*" else ["*"]
allow_credentials = False if origins == ["*"] else True
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 自定义Swagger UI，从CDN加载静态资源，解决本地网络问题
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui.css",
    )

# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()
    await sensitive_word_filter.load_sensitive_words()
    base = settings.APP_BASE_URL.rstrip("/")
    print(f"API 文档: {base}/docs")
    print(f"OpenAPI JSON: {base}{settings.API_V1_STR}/openapi.json")

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

@app.get("/")
async def root():
    """根路径，返回应用信息"""
    return {
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "message": "欢迎使用LLM过滤系统API"
    }
