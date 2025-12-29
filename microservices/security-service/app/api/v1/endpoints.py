from fastapi import APIRouter, Depends
from app.schemas.payloads import *
from app.services.analysis import SecurityService
from app.core.security import get_current_admin

router = APIRouter()
service = SecurityService()

@router.post("/analysis", response_model=SecurityAnalysisResponse)
async def analyze_risks(request: SecurityAnalysisRequest, admin: dict = Depends(get_current_admin)):
    return await service.analyze_risks(request.devices)

@router.post("/attack-advice", response_model=AttackAdviceResponse)
async def get_attack_advice(request: AttackAdviceRequest, admin: dict = Depends(get_current_admin)):
    return await service.get_attack_advice(request.attack_type, request.target_device, request.logs)

@router.get("/report", response_model=SecurityReportResponse)
async def generate_report(admin: dict = Depends(get_current_admin)):
    return await service.generate_report()

@router.get("/monitor", response_model=RiskMonitorResponse)
async def monitor_risks(admin: dict = Depends(get_current_admin)):
    return await service.monitor_risks()
