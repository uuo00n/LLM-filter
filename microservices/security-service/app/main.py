from contextlib import asynccontextmanager
from datetime import datetime
import logging

from fastapi import FastAPI, HTTPException

from app.api.v1.endpoints import router as security_router
from app.core.config import settings
from app.core.database import db
from app.services.zabbix_service import ZabbixService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.connect()

    try:
        zabbix_service = ZabbixService()
        sync_status = zabbix_service.get_sync_status()
        if sync_status.get("collector_initialized"):
            logger.info("Zabbix服务初始化成功")
        else:
            logger.warning("Zabbix服务初始化失败，请检查Zabbix配置")
    except Exception as e:
        logger.error(f"Zabbix服务连接检查失败: {e}")

    yield

    db.close()


app = FastAPI(title=settings.PROJECT_NAME, version="2.0.0", lifespan=lifespan)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "security-service", "version": "2.0.0"}


@app.get("/health")
async def detailed_health_check():
    try:
        db_status = "ok" if db.db else "error"

        zabbix_status = {"status": "not_configured"}
        try:
            zabbix_service = ZabbixService()
            sync_status = zabbix_service.get_sync_status()
            if sync_status.get("collector_initialized"):
                zabbix_status = {
                    "status": "ok",
                    "last_sync": sync_status.get("last_sync_time"),
                }
            else:
                zabbix_status = {
                    "status": "error",
                    "message": "Zabbix collector未初始化",
                }
        except Exception as e:
            zabbix_status = {
                "status": "error",
                "message": str(e),
            }

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "security-service",
            "version": "2.0.0",
            "components": {
                "database": {"status": db_status},
                "zabbix": zabbix_status,
            },
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.get("/ready")
async def readiness_check():
    try:
        if not db.db:
            return {
                "status": "not_ready",
                "timestamp": datetime.now().isoformat(),
                "reason": "database_not_connected",
            }

        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "timestamp": datetime.now().isoformat(),
            "reason": str(e),
        }


app.include_router(security_router, prefix=f"{settings.API_V1_STR}/security", tags=["Security"])
