from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1.endpoints import router as security_router
from app.core.config import settings
from app.core.database import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db.connect()
    yield
    # Shutdown
    db.close()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# 注册路由
app.include_router(security_router, prefix=f"{settings.API_V1_STR}/security", tags=["Security"])

@app.get("/")
def health_check():
    return {"status": "ok", "service": "security-service"}
