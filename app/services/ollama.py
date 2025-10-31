import httpx
from typing import List, Dict, Any
from app.core.config import settings

async def generate_response(messages: List[Dict[str, str]]) -> str:
    """
    调用Ollama API生成回复
    
    Args:
        messages: 对话历史消息列表，格式为[{"role": "user", "content": "..."}, ...]
        
    Returns:
        str: 模型生成的回复
    """
    # 转换消息格式为Ollama API所需格式
    prompt = ""
    for msg in messages:
        role_prefix = "User: " if msg["role"] == "user" else "Assistant: "
        prompt += f"{role_prefix}{msg['content']}\n"
    
    prompt += "Assistant: "
    
    # 构建请求数据
    data = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        # 发送请求到Ollama API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json=data,
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "抱歉，我无法生成回复。")
    except Exception as e:
        print(f"调用Ollama API出错: {str(e)}")
        return "抱歉，模型服务暂时不可用。"