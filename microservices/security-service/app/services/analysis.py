import json
import httpx
from datetime import datetime
from typing import List, Dict, Any
from app.schemas.payloads import *
from app.core.config import settings

# Mock Data
MOCK_DEVICES = [
    DeviceInfo(id="sw-001", name="Core-Switch-A", type="switch", status="warning", version="v1.2.0", logs=["Port 22 high traffic", "Packet loss detected"]),
    DeviceInfo(id="fw-001", name="Edge-Firewall", type="firewall", status="active", version="v2.1.patch3", logs=["Denied 1000+ requests from IP 192.168.1.50"]),
    DeviceInfo(id="srv-001", name="DB-Server-Prod", type="server", status="active", version="Ubuntu 20.04", logs=["Failed login attempts: 5"]),
]

class SecurityService:
    async def analyze_risks(self, devices: List[DeviceInfo] = None) -> SecurityAnalysisResponse:
        if not devices:
            devices = MOCK_DEVICES
        
        device_str = "\n".join([f"{d.name} ({d.type}): Status={d.status}, Logs={d.logs}" for d in devices])
        prompt = f"请分析以下网络设备的运行状态和日志，找出潜在的安全隐患，并给出风险等级（low, medium, high, critical）和修复建议。请以 JSON 格式返回，包含以下字段：summary, vulnerabilities (list), suggestions (list), risk_level。\n\n设备信息：\n{device_str}"
        
        return await self._call_llm(prompt, "analysis", SecurityAnalysisResponse)

    async def get_attack_advice(self, attack_type: str, target: str, logs: str) -> AttackAdviceResponse:
        prompt = f"当前系统正在遭受攻击！\n攻击类型：{attack_type}\n目标设备：{target}\n相关日志：{logs}\n\n请立即给出应急响应建议。以 JSON 格式返回：immediate_actions (list), analysis, mitigation_plan。"
        return await self._call_llm(prompt, "advice", AttackAdviceResponse)

    async def generate_report(self) -> SecurityReportResponse:
        prompt = f"请根据以下概况生成一份企业安全日报。\n日期：{datetime.now().strftime('%Y-%m-%d')}\n设备状态：3台设备运行中，1台有告警。\n拦截攻击：1500次。\n\n请以 JSON 格式返回：date, overall_status, device_summary, incident_summary, recommendations。"
        return await self._call_llm(prompt, "report", SecurityReportResponse)

    async def monitor_risks(self) -> RiskMonitorResponse:
        recent_vulns = ["CVE-2023-44487 (HTTP/2 Rapid Reset)", "Log4j 变种漏洞", "Nginx 权限提升漏洞"]
        prompt = f"我检索到了以下互联网最新的安全漏洞信息：\n{', '.join(recent_vulns)}\n\n请分析这些漏洞对一般企业（使用 Nginx, Java, Python）的合规风险。请以 JSON 格式返回：detected_vulnerabilities (list), compliance_risks (list), ai_assessment。"
        
        response = await self._call_llm(prompt, "monitor", RiskMonitorResponse)
        if not response.detected_vulnerabilities:
            response.detected_vulnerabilities = recent_vulns
        return response

    async def _call_llm(self, prompt: str, mock_type: str, model_cls):
        try:
            # 尝试调用 Dify
            headers = {"Authorization": f"Bearer {settings.DIFY_API_KEY}", "Content-Type": "application/json"}
            payload = {"inputs": {}, "query": prompt, "response_mode": "blocking", "conversation_id": "", "user": "security-system"}
            url = f"{settings.DIFY_API_URL.rstrip('/')}/chat-messages"
            
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, headers=headers, timeout=60.0)
                if resp.status_code == 200:
                    data = resp.json()
                    answer = data.get("answer", "")
                    json_data = self._extract_json(answer)
                    if json_data:
                        return model_cls(**json_data)
        except Exception as e:
            print(f"LLM Call Error: {e}")
        
        # 降级使用 Mock 数据
        return model_cls(**self._get_mock_data(mock_type))

    def _extract_json(self, text: str) -> Dict[str, Any]:
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
            return json.loads(text)
        except:
            return {}

    def _get_mock_data(self, type: str) -> Dict[str, Any]:
        if type == "analysis":
            return {"summary": "核心交换机存在异常流量。", "vulnerabilities": ["DDoS 攻击迹象"], "suggestions": ["检查端口配置"], "risk_level": "high"}
        elif type == "advice":
            return {"immediate_actions": ["封锁 IP"], "analysis": "暴力破解攻击。", "mitigation_plan": "启用 MFA。"}
        elif type == "report":
            return {"date": datetime.now().strftime('%Y-%m-%d'), "overall_status": "良好", "device_summary": "设备正常", "incident_summary": "拦截 1500 次", "recommendations": "定期更新"}
        elif type == "monitor":
            return {"detected_vulnerabilities": ["CVE-2023-44487"], "compliance_risks": ["服务中断风险"], "ai_assessment": "需立即更新补丁。"}
        return {}
