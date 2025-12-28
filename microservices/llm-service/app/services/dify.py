import httpx
import json
import re
from typing import Dict, Any, Optional
from app.core.config import settings

class DifyService:
    def __init__(self):
        api_url = (settings.DIFY_API_URL or "").strip()
        api_url = api_url.rstrip("/")
        if api_url and not api_url.endswith("/v1"):
            api_url = f"{api_url}/v1"
        self.api_url = api_url
        self.api_key = settings.DIFY_API_KEY
        self.timeout = 60.0  # 增加超时时间，因为智能体处理可能较慢
        self.response_mode = (settings.DIFY_RESPONSE_MODE or "streaming").strip().lower()
        self.message_endpoint = (settings.DIFY_MESSAGE_ENDPOINT or "chat-messages").strip().strip("/")

    def _parse_safety_answer(self, answer: str) -> Optional[Dict[str, Any]]:
        if not answer:
            return None

        clean = answer.replace("```json", "").replace("```", "").strip()

        try:
            obj = json.loads(clean)
            return obj if isinstance(obj, dict) else None
        except json.JSONDecodeError:
            pass

        m = re.search(r"\{[\s\S]*\}", clean)
        if not m:
            return None
        try:
            obj = json.loads(m.group(0))
            return obj if isinstance(obj, dict) else None
        except json.JSONDecodeError:
            return None

    async def _call_dify_blocking(self, url: str, payload: Dict[str, Any], headers: Dict[str, str]) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=self.timeout)

        if response.status_code != 200:
            print(f"Dify API Error: {response.text}")
            return ""

        data = response.json()
        answer = data.get("answer", "")
        return answer if isinstance(answer, str) else ""

    async def _call_dify_streaming(self, url: str, payload: Dict[str, Any], headers: Dict[str, str]) -> str:
        answer_chunks: list[str] = []

        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=payload, headers=headers, timeout=self.timeout) as response:
                if response.status_code != 200:
                    try:
                        body = await response.aread()
                        print(f"Dify API Error: {body.decode('utf-8', errors='ignore')}")
                    except Exception:
                        print("Dify API Error: <failed to read response body>")
                    return ""

                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if not line.startswith("data:"):
                        continue
                    data_str = line[len("data:") :].strip()
                    if not data_str or data_str == "[DONE]":
                        continue
                    try:
                        event = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    if not isinstance(event, dict):
                        continue

                    ev_type = event.get("event")
                    if ev_type in {"message_end", "agent_message_end", "tts_message_end"}:
                        break

                    part = event.get("answer")
                    if isinstance(part, str) and part:
                        answer_chunks.append(part)

        return "".join(answer_chunks).strip()

    async def check_content_safety(self, content: str, user_id: str) -> Dict[str, Any]:
        """
        使用 Dify 智能体检查内容安全
        
        Args:
            content: 用户输入内容
            user_id: 用户ID
            
        Returns:
            Dict: {
                "safe": bool,          # 是否安全
                "reason": str,         # 如果不安全的原因
                "suggestion": str      # 修改建议（可选）
            }
        """
        # 如果未配置 API Key，默认跳过检查（返回安全）
        if not self.api_key:
            return {"safe": True, "reason": "", "suggestion": ""}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 构造 Dify 聊天消息请求
        # 假设 Dify 应用已配置为返回特定 JSON 结构的文本
        payload = {
            "inputs": {},
            "query": content,
            "response_mode": self.response_mode,
            "conversation_id": "",  # 每次检查作为独立对话，或者可以关联上下文
            "user": user_id
        }

        try:
            if not self.api_url or not self.message_endpoint:
                return {"safe": True, "reason": "Dify config missing", "suggestion": ""}

            url = f"{self.api_url}/{self.message_endpoint}"
            if self.response_mode == "blocking":
                answer = await self._call_dify_blocking(url, payload, headers)
            else:
                answer = await self._call_dify_streaming(url, payload, headers)

            parsed = self._parse_safety_answer(answer)
            if not parsed:
                if answer:
                    print(f"Dify response is not valid JSON: {answer}")
                return {"safe": True, "reason": "Invalid JSON response", "suggestion": ""}

            return {
                "safe": parsed.get("safe", True),
                "reason": parsed.get("reason", ""),
                "suggestion": parsed.get("suggestion", "")
            }

        except Exception as e:
            print(f"Error calling Dify: {str(e)}")
            return {"safe": True, "reason": f"Error: {str(e)}", "suggestion": ""}

dify_service = DifyService()
