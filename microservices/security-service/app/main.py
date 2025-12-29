from fastapi import FastAPI
from app.api.v1.endpoints import router as security_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# 注册路由
app.include_router(security_router, prefix=f"{settings.API_V1_STR}/security", tags=["Security"])

@app.get("/")
def health_check():
    return {"status": "ok", "service": "security-service"}
