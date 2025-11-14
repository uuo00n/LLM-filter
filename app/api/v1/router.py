from fastapi import APIRouter
from app.api.v1 import auth, conversation, admin, dashboard, students, bindings, persons, teachers, classes, schedules

api_router = APIRouter()

# 注册各模块路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(conversation.router, prefix="/conversations", tags=["对话"])
api_router.include_router(admin.router, prefix="/admin", tags=["管理员"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["仪表盘"])
api_router.include_router(students.router, prefix="/students", tags=["学生"])
api_router.include_router(bindings.router, prefix="/bindings", tags=["绑定"])
api_router.include_router(persons.router, prefix="/persons", tags=["人员"])
api_router.include_router(teachers.router, prefix="/teachers", tags=["教师"])
api_router.include_router(classes.router, prefix="/classes", tags=["班级"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["课表"])