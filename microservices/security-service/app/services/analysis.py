import json
import httpx
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import ValidationError
from app.schemas.payloads import *
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class SecurityService:
    async def analyze_risks(self, devices: List[DeviceInfo] = None) -> SecurityAnalysisResponse:
        """
        任务：风险分析
        """
        if not devices:
            devices = []
        
        # 1. 准备数据，不再拼接 Prompt，只序列化数据
        device_data = [d.dict() for d in devices] # 假设 Pydantic 模型有 .dict()，或者手动转 dict
        
        # 2. 构造 Dify 所需的变量 inputs
        inputs = {
            "task_type": "analysis",  # 告诉 Dify 执行哪个任务分支
            "context_data": json.dumps(device_data, ensure_ascii=False) # 将复杂数据转为字符串传递
        }
        
        return await self._call_llm(inputs, SecurityAnalysisResponse)

    async def get_attack_advice(self, attack_type: str, target: str, logs: str) -> AttackAdviceResponse:
        """
        任务：攻击应急建议
        """
        # 构造结构化数据
        data = {
            "attack_type": attack_type,
            "target_device": target,
            "logs": logs
        }
        
        inputs = {
            "task_type": "advice",
            "context_data": json.dumps(data, ensure_ascii=False)
        }
        
        return await self._call_llm(inputs, AttackAdviceResponse)

    async def generate_report(self) -> SecurityReportResponse:
        """
        任务：生成日报
        """
        # 注意：此处应从真实数据源获取状态，当前暂无数据源连接
        data = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "device_status": "暂无数据 (需接入数据源)",
            "intercept_count": 0
        }
        
        inputs = {
            "task_type": "report",
            "context_data": json.dumps(data, ensure_ascii=False)
        }
        
        return await self._call_llm(inputs, SecurityReportResponse)

    async def monitor_risks(self) -> RiskMonitorResponse:
        """
        任务：漏洞监测
        """
        # 注意：此处应从外部漏洞库或配置获取关注列表
        recent_vulns = [] 
        
        inputs = {
            "task_type": "monitor",
            "context_data": json.dumps(recent_vulns, ensure_ascii=False)
        }
        
        return await self._call_llm(inputs, RiskMonitorResponse)

    async def _call_llm(self, inputs: Dict[str, Any], model_cls):
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
                "response_mode": "streaming",
                "conversation_id": "",
                "user": "security-system-api",
            }

            # DEBUG LOG: 打印实际发送的 Payload
            logger.info(f"Sending request to Dify. URL: {url}")
            logger.info(f"Payload inputs: {json.dumps(inputs, ensure_ascii=False)}")

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
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = text[start:end]
                return json.loads(json_str)
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
