from datetime import datetime

from fastapi import APIRouter, Depends, Query
from app.schemas.payloads import *
from app.services.analysis import SecurityService
from app.services.rss import RSSService
from app.services.zabbix_service import ZabbixService
from app.core.security import get_current_admin

router = APIRouter()
zabbix_service = ZabbixService()
service = SecurityService(zabbix_service=zabbix_service)
rss_service = RSSService()

@router.post("/analysis", response_model=SecurityAnalysisResponse)
async def analyze_risks(request: SecurityAnalysisRequest, admin: dict = Depends(get_current_admin)):
    return await service.analyze_risks(request.devices)

@router.get("/analysis/history", response_model=HistoryQueryResponse)
async def get_analysis_history(
    start_date: Optional[datetime] = Query(None, description="开始时间 (ISO 8601)"),
    end_date: Optional[datetime] = Query(None, description="结束时间 (ISO 8601)"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    admin: dict = Depends(get_current_admin)
):
    """
    查询安全分析历史记录
    """
    return await service.get_analysis_history(start_date, end_date, limit)

@router.post("/attack-advice", response_model=AttackAdviceResponse)
async def get_attack_advice(request: AttackAdviceRequest, admin: dict = Depends(get_current_admin)):
    return await service.get_attack_advice(
        attack_type=request.attack_type,
        target=request.target_device,
        logs=request.logs,
        severity=request.severity,
    )

@router.get("/attack-advice/history", response_model=HistoryQueryResponse)
async def get_attack_advice_history(
    start_date: Optional[datetime] = Query(None, description="开始时间 (ISO 8601)"),
    end_date: Optional[datetime] = Query(None, description="结束时间 (ISO 8601)"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    admin: dict = Depends(get_current_admin)
):
    """
    查询攻击建议历史记录
    """
    return await service.get_attack_advice_history(start_date, end_date, limit)

@router.get("/report", response_model=SecurityReportResponse)
async def generate_report(admin: dict = Depends(get_current_admin)):
    return await service.generate_report()

@router.get("/monitor", response_model=RiskMonitorResponse)
async def monitor_risks(admin: dict = Depends(get_current_admin)):
    return await service.monitor_risks()

@router.get("/rss/news", response_model=RSSFeedResponse)
async def get_security_news(admin: dict = Depends(get_current_admin)):
    """
    获取安全新闻 RSS 订阅 (天融信 / 360 / 绿盟)
    """
    return await rss_service.get_security_news()

@router.post("/zabbix/sync")
async def sync_zabbix_data(admin: dict = Depends(get_current_admin)):
    """
    手动同步Zabbix数据
    """
    try:
        result = await zabbix_service.sync_data()
        return {
            "status": "success",
            "message": "Zabbix数据同步完成",
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Zabbix数据同步失败: {str(e)}",
            "data": None
        }

@router.get("/zabbix/status")
async def get_zabbix_status(admin: dict = Depends(get_current_admin)):
    """
    获取Zabbix服务状态
    """
    status = zabbix_service.get_sync_status()
    return {
        "status": "success",
        "data": status
    }

@router.post("/zabbix/devices")
async def get_zabbix_devices(admin: dict = Depends(get_current_admin)):
    """
    获取Zabbix设备列表
    """
    try:
        device_data = await zabbix_service.collect_device_data()
        return {
            "status": "success",
            "message": f"成功获取 {len(device_data.get('devices', []))} 台设备",
            "data": device_data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"获取设备数据失败: {str(e)}",
            "data": None
        }


