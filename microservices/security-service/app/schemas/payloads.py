from typing import List, Optional, Any, Union
from pydantic import BaseModel

class DeviceInfo(BaseModel):
    id: str
    name: str
    type: str  # switch, firewall, server
    status: str
    logs: Optional[List[str]] = None
    version: Optional[str] = None

class SecurityAnalysisRequest(BaseModel):
    devices: Optional[List[DeviceInfo]] = None

class SecurityAnalysisResponse(BaseModel):
    summary: str
    vulnerabilities: List[Union[str, dict, Any]]
    suggestions: List[Union[str, dict, Any]]
    risk_level: Optional[str] = "unknown"

class AttackAdviceRequest(BaseModel):
    attack_type: str
    target_device: str
    severity: str
    logs: Optional[str] = None

class AttackAdviceResponse(BaseModel):
    immediate_actions: List[str]
    analysis: str
    mitigation_plan: str

class SecurityReportResponse(BaseModel):
    date: str
    overall_status: str
    device_summary: str
    incident_summary: str
    recommendations: str

class RiskMonitorResponse(BaseModel):
    detected_vulnerabilities: List[str]
    compliance_risks: List[str]
    ai_assessment: str
