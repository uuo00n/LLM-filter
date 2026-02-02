from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from app.api.v1.endpoints import router as security_router
from app.core.config import settings
from app.core.database import db
from datetime import datetime
import logging
import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
logger = logging.getLogger(__name__)

@app.get("/")
def health_check():
    """根路径健康检查"""
    return {"status": "ok", "service": "security-service", "version": "2.0.0"}

@app.get("/health")
async def detailed_health_check():
    """详细健康检查端点"""
    try:
        # 检查数据库连接
        db_status = "ok" if db.db else "error"
        
        # 检查Zabbix服务
        zabbix_status = {"status": "not_configured", "message": "Zabbix服务未配置"}
        try:
            from app.services.zabbix_service import ZabbixService
            zabbix_service = ZabbixService()
            sync_status = zabbix_service.get_sync_status()
            if sync_status["collector_initialized"]:
                zabbix_status = {
                    "status": "ok",
                    "last_sync": sync_status["last_sync_time"]
                }
            else:
                zabbix_status = {
                    "status": "error",
                    "message": "Zabbix collector未初始化"
                }
        except Exception as e:
            zabbix_status = {
                "status": "error",
                "message": str(e)
            }
        
        from datetime import datetime
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "security-service",
            "version": "2.0.0",
            "components": {
                "database": {"status": db_status},
                "zabbix": zabbix_status
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/ready")
async def readiness_check():
    """就绪检查端点"""
    try:
        # 检查关键依赖是否就绪
        if not db.db:
            return {
                "status": "not_ready",
                "timestamp": datetime.now().isoformat(),
                "reason": "database_not_connected"
            }
            
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "timestamp": datetime.now().isoformat(),
            "reason": str(e)
        }

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger = logging.getLogger(__name__)
    
    # 连接数据库
    db.connect()
    
    # 初始化Zabbix服务连接检查
    try:
        from app.services.zabbix_service import ZabbixService
        zabbix_service = ZabbixService()
        sync_status = zabbix_service.get_sync_status()
        if sync_status["collector_initialized"]:
            logger.info("✅ Zabbix服务初始化成功")
        else:
            logger.warning("⚠️ Zabbix服务初始化失败，请检查Zabbix配置")
    except Exception as e:
        logger.error(f"❌ Zabbix服务连接检查失败: {e}")
    
    yield
    
    # Shutdown
    db.close()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# 注册路由
app.include_router(security_router, prefix=f"{settings.API_V1_STR}/security", tags=["Security"])

