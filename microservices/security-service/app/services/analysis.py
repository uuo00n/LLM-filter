import json
import httpx
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import ValidationError
from app.schemas.payloads import *
from app.core.config import settings
from app.core.database import db
from app.services.zabbix_service import ZabbixService
import logging

logger = logging.getLogger(__name__)

class SecurityService:
    def __init__(self, zabbix_service: ZabbixService):
        """
        初始化安全服务
        :param zabbix_service: Zabbix数据服务
        """
        self.zabbix_service = zabbix_service
    async def analyze_risks(self, devices: List[DeviceInfo] = None) -> SecurityAnalysisResponse:
        """
        任务：风险分析 - 使用真实Zabbix数据
        """
        if not devices:
            # 从Zabbix自动采集设备数据
            try:
                logger.info("未提供设备数据，从Zabbix自动采集...")
                zabbix_data = await self.zabbix_service.collect_device_data()
                devices_data = zabbix_data.get("devices", [])
                
                # 转换为DeviceInfo对象
                devices = []
                for device_data in devices_data:
                    device = DeviceInfo(
                        id=device_data.get("id", ""),
                        name=device_data.get("name", ""),
                        type=device_data.get("type", "unknown"),
                        status=device_data.get("status", "unknown"),
                        logs=device_data.get("logs", [])
                    )
                    devices.append(device)
                    
                logger.info(f"从Zabbix采集到 {len(devices)} 台设备")
            except Exception as e:
                logger.error(f"从Zabbix采集设备数据失败: {e}")
                # 使用空设备列表继续，让LLM处理
                devices = []
        
        if not devices:
            # 如果依然没有设备数据，创建空的设备列表
            devices = []
        
        # 1. 准备数据，序列化设备数据
        device_data = [d.model_dump() for d in devices]
        
        # 2. 构造 Dify 所需的变量 inputs
        inputs = {
            "task_type": "analysis",  # 告诉 Dify 执行哪个任务分支
            "context_data": json.dumps(device_data, ensure_ascii=False)  # 将复杂数据转为字符串传递
        }
        
        # 3. 调用LLM进行分析
        result = await self._call_llm(inputs, SecurityAnalysisResponse)
        
        # 4. 异步存储结果到 MongoDB
        try:
            if db.db is not None:
                log_entry = result.model_dump()
                log_entry["created_at"] = datetime.now(timezone.utc)
                log_entry["device_count"] = len(devices)
                await db.db.security_analysis_logs.insert_one(log_entry)
                logger.info("安全分析结果已保存到MongoDB")
        except Exception as e:
            logger.error(f"保存分析结果到MongoDB失败: {e}")
        
        return result

    async def get_attack_advice(self, attack_type: str, target: str, logs: str, severity: Optional[str] = None) -> AttackAdviceResponse:
        """
        任务：攻击应急建议
        """
        data = {
            "attack_type": attack_type,
            "target_device": target,
            "severity": severity,
            "logs": logs,
        }

        inputs = {
            "task_type": "advice",
            "context_data": json.dumps(data, ensure_ascii=False),
        }

        result = await self._call_llm(inputs, AttackAdviceResponse)

        try:
            if db.db is not None:
                log_entry = result.model_dump()
                log_entry.update(
                    {
                        "created_at": datetime.now(timezone.utc),
                        "attack_type": attack_type,
                        "target_device": target,
                        "severity": severity,
                    }
                )
                await db.db.attack_advice_logs.insert_one(log_entry)
                logger.info("攻击建议结果已保存到MongoDB")
        except Exception as e:
            logger.error(f"保存攻击建议结果到MongoDB失败: {e}")

        return result

    async def generate_report(self) -> SecurityReportResponse:
        """
        任务：生成日报 - 使用真实数据
        """
        try:
            # 从Zabbix获取实时数据
            logger.info("从Zabbix采集数据生成安全报告...")
            
            # 采集设备数据
            device_data = await self.zabbix_service.collect_device_data()
            devices = device_data.get("devices", [])
            
            # 统计设备状态
            total_devices = len(devices)
            up_devices = sum(1 for d in devices if d.get("status") == "up")
            down_devices = sum(1 for d in devices if d.get("status") == "down")
            problem_devices = sum(1 for d in devices if d.get("logs"))
            
            # 构建报告数据
            report_data = {
                "date": datetime.now().strftime('%Y-%m-%d'),
                "device_status": {
                    "total_devices": total_devices,
                    "up_devices": up_devices,
                    "down_devices": down_devices,
                    "problem_devices": problem_devices
                },
                "incident_summary": {
                    "total_events": sum(len(d.get("logs", [])) for d in devices),
                    "critical_events": 0,  # 可以从Zabbix触发器优先级统计
                    "high_events": 0,
                    "medium_events": 0,
                    "low_events": 0,
                    "resolved_events": 0,
                    "unresolved_events": problem_devices
                },
                "top_issues": self._extract_top_issues(devices),
                "real_time_data": True  # 标识使用真实数据
            }
            
            logger.info(f"成功采集到 {total_devices} 台设备数据，其中 {problem_devices} 台有问题")
            
        except Exception as e:
            logger.error(f"从Zabbix采集数据失败，使用备用数据: {e}")
            # 备用数据（当Zabbix不可用时）
            report_data = {
                "date": datetime.now().strftime('%Y-%m-%d'),
                "device_status": {
                    "total_devices": 0,
                    "up_devices": 0,
                    "down_devices": 0,
                    "problem_devices": 0,
                    "status": "zabbix_unavailable"
                },
                "incident_summary": {
                    "total_events": 0,
                    "critical_events": 0,
                    "high_events": 0,
                    "medium_events": 0,
                    "low_events": 0,
                    "resolved_events": 0,
                    "unresolved_events": 0
                },
                "top_issues": ["Zabbix服务不可用，无法获取实时数据"],
                "real_time_data": False  # 标识使用备用数据
            }
        
        inputs = {
            "task_type": "report",
            "context_data": json.dumps(report_data, ensure_ascii=False)
        }
        
        result = await self._call_llm(inputs, SecurityReportResponse)
        
        # 异步存储结果到 MongoDB
        try:
            if db.db is not None:
                log_entry = result.model_dump()
                log_entry["created_at"] = datetime.now(timezone.utc)
                log_entry["report_date"] = report_data["date"]
                log_entry["real_time_data"] = report_data.get("real_time_data", False)
                await db.db.security_report_logs.insert_one(log_entry)
                logger.info("安全报告结果已保存到MongoDB")
        except Exception as e:
            logger.error(f"保存报告结果到MongoDB失败: {e}")
        
        return result

    async def monitor_risks(self) -> RiskMonitorResponse:
        """
        实时风险监控 - 使用真实数据
        """
        try:
            logger.info("从Zabbix采集监控数据...")
            
            # 采集设备数据
            device_data = await self.zabbix_service.collect_device_data()
            devices = device_data.get("devices", [])
            
            # 分析设备状态
            detected_vulnerabilities = []
            compliance_risks = []
            
            for device in devices:
                device_name = device.get("name", "未知设备")
                device_type = device.get("type", "unknown")
                logs = device.get("logs", [])
                
                # 基于设备类型和日志分析潜在风险
                if device_type == "switch":
                    # 交换机常见风险
                    if any("down" in log.lower() for log in logs):
                        compliance_risks.append(f"交换机 {device_name} 离线 - 网络中断风险")
                    if any("link down" in log.lower() for log in logs):
                        detected_vulnerabilities.append(f"网络接口异常 - {device_name}")
                
                elif device_type == "firewall":
                    # 防火墙常见风险
                    if any("packet loss" in log.lower() for log in logs):
                        detected_vulnerabilities.append(f"防火墙 {device_name} 包丢失 - 性能问题")
                    if any("connection" in log.lower() and "failed" in log.lower() for log in logs):
                        compliance_risks.append(f"防火墙 {device_name} 连接失败 - 安全策略检查")
                
                elif device_type == "server":
                    # 服务器常见风险
                    if any("cpu" in log.lower() and "high" in log.lower() for log in logs):
                        detected_vulnerabilities.append(f"服务器 {device_name} CPU 高负载 - 性能风险")
                    if any("memory" in log.lower() and "usage" in log.lower() for log in logs):
                        compliance_risks.append(f"服务器 {device_name} 内存使用异常 - 资源优化")
                
                # 通用风险检测
                for log in logs:
                    if any(priority in log for priority in ["Priority: 5", "Priority: 4"]):
                        detected_vulnerabilities.append(f"高优先级告警 - {device_name}: {log[:50]}...")
            
            # 如果没有检测到具体风险，提供通用风险评估
            if not detected_vulnerabilities and not compliance_risks:
                detected_vulnerabilities = ["系统运行正常，未检测到明显安全漏洞"]
                compliance_risks = ["系统符合基本安全要求，建议定期审计"]
            
            ai_assessment = f"系统安全状态: {self._assess_security_risk_level(devices)}"
            
            logger.info(f"监控分析完成，发现 {len(detected_vulnerabilities)} 个漏洞和 {len(compliance_risks)} 个合规风险")
            
        except Exception as e:
            logger.error(f"从Zabbix采集监控数据失败: {e}")
            # 备用监控数据
            detected_vulnerabilities = ["监控系统不可用，无法获取实时风险数据"]
            compliance_risks = ["系统状态未知，请检查Zabbix连接"]
            ai_assessment = "监控系统服务异常，无法进行有效风险评估"
        
        return RiskMonitorResponse(
            detected_vulnerabilities=detected_vulnerabilities,
            compliance_risks=compliance_risks,
            ai_assessment=ai_assessment
        )

    async def get_analysis_history(self, start_date: datetime = None, end_date: datetime = None, limit: int = 20) -> HistoryQueryResponse:
        """
        查询安全分析历史
        """
        if db.db is None:
            return HistoryQueryResponse(total=0, items=[])
        
        query = {}
        if start_date or end_date:
            query["created_at"] = {}
            if start_date:
                query["created_at"]["$gte"] = start_date
            if end_date:
                query["created_at"]["$lte"] = end_date
        
        total = await db.db.security_analysis_logs.count_documents(query)
        cursor = db.db.security_analysis_logs.find(query).sort("created_at", -1).limit(limit)
        
        items = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            items.append(AnalysisHistoryItem(**doc))
            
        return HistoryQueryResponse(total=total, items=items)

    async def get_attack_advice_history(self, start_date: datetime = None, end_date: datetime = None, limit: int = 20) -> HistoryQueryResponse:
        """
        查询攻击建议历史
        """
        if db.db is None:
            return HistoryQueryResponse(total=0, items=[])
        
        query = {}
        if start_date or end_date:
            query["created_at"] = {}
            if start_date:
                query["created_at"]["$gte"] = start_date
            if end_date:
                query["created_at"]["$lte"] = end_date
        
        total = await db.db.attack_advice_logs.count_documents(query)
        cursor = db.db.attack_advice_logs.find(query).sort("created_at", -1).limit(limit)
        
        items = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            items.append(AttackAdviceHistoryItem(**doc))
            
        return HistoryQueryResponse(total=total, items=items)

    async def _call_llm(self, inputs: Dict[str, Any], model_cls):
        if not settings.DIFY_API_URL or not settings.DIFY_API_KEY:
            logger.warning("Dify 未配置（缺少 DIFY_API_URL 或 DIFY_API_KEY），跳过 LLM 调用并返回默认结果")
            return self._build_default_response(model_cls)

        try:
            url = f"{settings.DIFY_API_URL.rstrip('/')}/chat-messages"
            headers = {
                "Authorization": f"Bearer {settings.DIFY_API_KEY}",
                "Content-Type": "application/json",
            }

            # 动态构造 Query 以强化指令，确保 LLM 执行正确的任务分支
            task_type = inputs.get("task_type", "analysis")
            query_prompt = f"Please execute the security task: {task_type}."
            
            if task_type == "advice":
                query_prompt += " Output JSON must include: immediate_actions, analysis, mitigation_plan."
            elif task_type == "analysis":
                query_prompt += " Output JSON must include: summary, vulnerabilities, suggestions, risk_level."
            elif task_type == "report":
                query_prompt += " Output JSON must include: date, overall_status, device_summary, incident_summary, recommendations."
            elif task_type == "monitor":
                query_prompt += " Output JSON must include: detected_vulnerabilities, compliance_risks, ai_assessment."
            
            query_prompt += " Strictly follow the requested JSON schema."

            payload = {
                "inputs": inputs,
                "query": query_prompt,
                "response_mode": settings.DIFY_RESPONSE_MODE,
                "conversation_id": "",
                "user": "security-system-api",
            }

            full_answer = ""
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", url, json=payload, headers=headers, timeout=120.0) as resp:
                    if resp.status_code == 200:
                        async for line in resp.aiter_lines():
                            if line.startswith("data: "):
                                try:
                                    json_str = line[6:].strip()
                                    if not json_str:
                                        continue
                                    data = json.loads(json_str)
                                    event = data.get("event")
                                    if event in ["message", "agent_message"]:
                                        full_answer += data.get("answer", "")
                                except Exception:
                                    continue
                    else:
                        error_body = await resp.read()
                        logger.error(
                            f"LLM Call Failed: Status={resp.status_code}, Response={error_body.decode()}"
                        )

            if full_answer:
                clean_json = self._clean_json_string(full_answer)
                json_data = self._extract_json(clean_json)
                if json_data:
                    try:
                        return model_cls(**json_data)
                    except ValidationError as ve:
                        logger.error(f"Response validation failed for {model_cls.__name__}: {ve}")
                else:
                    logger.warning(
                        f"Failed to extract JSON from LLM response. Raw answer: {full_answer[:500]}..."
                    )
            else:
                logger.warning("LLM response was empty.")

        except Exception as e:
            logger.error(f"LLM Call Error: {e}")

        return self._build_default_response(model_cls)

    def _extract_top_issues(self, devices: List[Dict]) -> List[str]:
        """
        从设备日志中提取主要问题
        """
        issues = []
        
        for device in devices:
            device_name = device.get("name", "未知设备")
            logs = device.get("logs", [])
            
            # 分析日志中的关键问题
            for log in logs:
                if any(keyword in log.lower() for keyword in ["critical", "down", "failed", "error", "high priority"]):
                    issues.append(f"{device_name}: {log[:80]}...")
                    break  # 每个设备只取一个问题
        
        # 如果没有问题，返回正常状态
        if not issues:
            issues = ["系统运行正常，未发现明显问题"]
        
        return issues[:5]  # 只返回前5个主要问题

    def _assess_security_risk_level(self, devices: List[Dict]) -> str:
        """
        评估系统整体安全风险等级
        """
        total_devices = len(devices)
        problem_devices = sum(1 for d in devices if d.get("logs"))
        
        if total_devices == 0:
            return "未知 - 无设备数据"
        
        problem_ratio = problem_devices / total_devices
        
        if problem_ratio >= 0.3:
            return "高风险 - 多个设备出现异常"
        elif problem_ratio >= 0.1:
            return "中等风险 - 部分设备存在异常"
        elif problem_ratio > 0:
            return "低风险 - 少量设备出现异常"
        else:
            return "安全 - 所有设备运行正常"

    def _clean_json_string(self, text: str) -> str:
        """清洗 Markdown 代码块标记和思维链标签"""
        import re
        
        # 记录原始长度用于调试
        original_len = len(text)
        
        # 1. 移除 <think>...</think> 思维链内容
        # 优先匹配闭合的标签
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        
        # 2. 处理可能未闭合的 <think> 标签（如果响应被截断）
        # 如果还有 <think> 开头，说明没闭合，直接丢弃后面的所有内容（假设思考过程在最后被截断，或者思考过程包含了整个剩余部分）
        # 但通常思考在前，正文在后。如果没闭合，说明正文还没出来。
        # 这里保守处理：如果剩下内容全是思考，那就全删了，返回空串，由上层处理为空的情况。
        if '<think>' in text:
            text = re.sub(r'<think>.*', '', text, flags=re.DOTALL)

        # 3. 清洗 Markdown 标记
        if "```json" in text:
            text = text.replace("```json", "").replace("```", "")
        elif "```" in text:
            text = text.replace("```", "")
            
        cleaned_text = text.strip()
        if original_len > 0 and len(cleaned_text) == 0:
            logger.warning("Response became empty after cleaning (likely only contained <think> block).")
            
        return cleaned_text

    def _extract_json(self, text: str) -> Dict[str, Any]:
        if not text:
            return {}
        try:
            # 尝试找到第一个 {
            start = text.find('{')
            if start == -1:
                # 尝试直接解析，也许是 list [] 或者是其他合法 JSON
                return json.loads(text)
            
            # 基于括号计数来提取最外层 JSON
            count = 0
            end = -1
            
            for i, char in enumerate(text[start:], start=start):
                if char == '{':
                    count += 1
                elif char == '}':
                    count -= 1
                    if count == 0:
                        end = i + 1
                        break
            
            if end != -1:
                json_str = text[start:end]
                return json.loads(json_str)
                
            # 如果没找到闭合，回退到原来的逻辑
            # start = text.find('{')
            # end = text.rfind('}') + 1
            # ... 但原来的逻辑有问题，这里不如直接尝试解析整个 text 或者报错
            return json.loads(text)
            
        except Exception as e:
            logger.warning(f"JSON extraction error: {e}. Text snippet: {text[:100]}...")
            return {}

    def _build_default_response(self, model_cls):
        if model_cls is SecurityAnalysisResponse:
            return model_cls(
                summary="LLM 调用失败或未返回有效结果",
                vulnerabilities=[],
                suggestions=[],
                risk_level="unknown",
            )
        if model_cls is AttackAdviceResponse:
            return model_cls(
                immediate_actions=[],
                analysis="LLM 调用失败或未返回有效结果，无法提供具体攻击分析。",
                mitigation_plan="请检查安全监控系统与安全策略配置后重试。",
            )
        if model_cls is SecurityReportResponse:
            return model_cls(
                date=datetime.now().strftime("%Y-%m-%d"),
                overall_status="LLM 调用失败或未返回有效结果。",
                device_summary="暂无可用设备统计数据。",
                incident_summary="暂无可用安全事件统计数据。",
                recommendations="请检查安全服务与 LLM 服务的连接状态后重试。",
            )
        if model_cls is RiskMonitorResponse:
            return model_cls(
                detected_vulnerabilities=[],
                compliance_risks=[],
                ai_assessment="LLM 调用失败或未返回有效结果，无法完成有效风险评估。",
            )
        return model_cls()
