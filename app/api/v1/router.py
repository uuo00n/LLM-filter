from fastapi import APIRouter
from app.api.v1 import auth, conversation, admin

api_router = APIRouter()

# 注册各模块路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(conversation.router, prefix="/conversations", tags=["对话"])
api_router.include_router(admin.router, prefix="/admin", tags=["管理员"])