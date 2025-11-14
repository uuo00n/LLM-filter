from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.utils.sensitive_word_filter import sensitive_word_filter

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "LLM 过滤系统后端接口\n\n"
        "角色等级：1 学生、2 班主任、3 中层、4 校级、5 管理员。\n"
        "实体绑定：通过 /bindings 建立账号与人物（students/teachers）的主绑定。\n"
        "运行模式：APP_MODE=edu/biz，路由统一受版别依赖控制。"
    ),
    openapi_tags=[
        {"name": "认证", "description": "注册、登录，返回令牌与用户基础信息（含绑定信息）"},
        {"name": "仪表盘", "description": "学生/班主任/中层/校级看板数据接口"},
        {"name": "学生", "description": "学生实体相关接口（按绑定解析）"},
        {"name": "绑定", "description": "账号与人物绑定管理（主绑定唯一）"},
        {"name": "人员", "description": "人物档案管理（学生/教师/职员等）"},
        {"name": "教师", "description": "教师实体导入与查询（含班主任/干部角色）"},
        {"name": "班级", "description": "班级管理（设置班主任为 head_teacher_person_id）"},
        {"name": "课表", "description": "课表管理（为节次设置 teacher_person_id；共享节次）"},
        {"name": "管理员", "description": "管理员功能（敏感词、分类等）"},
        {"name": "对话", "description": "对话与敏感词审计接口"},
    ],
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