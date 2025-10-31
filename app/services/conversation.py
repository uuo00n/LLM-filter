from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import db
from app.services.ollama import generate_response
from app.utils.sensitive_word_filter import sensitive_word_filter

async def create_conversation(user_id: str) -> str:
    """创建新对话"""
    conversation = {
        "user_id": ObjectId(user_id),
        "messages": [],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    result = await db.db.conversations.insert_one(conversation)
    return str(result.inserted_id)

async def get_conversation(conversation_id: str, user_id: str) -> Optional[Dict]:
    """获取对话"""
    conversation = await db.db.conversations.find_one({
        "_id": ObjectId(conversation_id),
        "user_id": ObjectId(user_id)
    })
    
    if conversation:
        conversation["_id"] = str(conversation["_id"])
        conversation["user_id"] = str(conversation["user_id"])
    
    return conversation

async def add_message(conversation_id: str, user_id: str, content: str) -> Dict[str, Any]:
    """
    添加用户消息并获取AI回复
    
    Args:
        conversation_id: 对话ID
        user_id: 用户ID
        content: 用户消息内容
        
    Returns:
        Dict: 包含处理结果的字典
    """
    # 检查敏感词
    contains_sensitive, sensitive_words = sensitive_word_filter.check_text(content)
    
    # 创建用户消息
    user_message = {
        "role": "user",
        "content": content,
        "timestamp": datetime.now(),
        "contains_sensitive_words": contains_sensitive,
        "sensitive_words_found": sensitive_words
    }
    
    # 更新对话
    await db.db.conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {
            "$push": {"messages": user_message},
            "$set": {"updated_at": datetime.now()}
        }
    )
    
    # 如果包含敏感词，记录并返回拒绝回复
    if contains_sensitive:
        # 创建敏感词记录
        sensitive_record = {
            "user_id": ObjectId(user_id),
            "conversation_id": ObjectId(conversation_id),
            "message_content": content,
            "sensitive_words_found": sensitive_words,
            "timestamp": datetime.now()
        }
        
        await db.db.sensitive_records.insert_one(sensitive_record)
        
        # 创建系统回复
        assistant_message = {
            "role": "assistant",
            "content": "当前问题暂无法回答。",
            "timestamp": datetime.now(),
            "contains_sensitive_words": False,
            "sensitive_words_found": []
        }
        
        # 更新对话
        await db.db.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$push": {"messages": assistant_message},
                "$set": {"updated_at": datetime.now()}
            }
        )
        
        return {
            "contains_sensitive_words": True,
            "sensitive_words_found": sensitive_words,
            "assistant_response": "当前问题暂无法回答。"
        }
    
    # 获取对话历史
    conversation = await db.db.conversations.find_one({"_id": ObjectId(conversation_id)})
    messages = conversation.get("messages", [])
    
    # 准备发送给模型的消息（最多取最近10条）
    model_messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in messages[-10:]
    ]
    
    # 调用模型生成回复
    assistant_response = await generate_response(model_messages)
    
    # 创建助手回复消息
    assistant_message = {
        "role": "assistant",
        "content": assistant_response,
        "timestamp": datetime.now(),
        "contains_sensitive_words": False,
        "sensitive_words_found": []
    }
    
    # 更新对话
    await db.db.conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {
            "$push": {"messages": assistant_message},
            "$set": {"updated_at": datetime.now()}
        }
    )
    
    return {
        "contains_sensitive_words": False,
        "sensitive_words_found": [],
        "assistant_response": assistant_response
    }

async def get_user_conversations(user_id: str) -> List[Dict]:
    """获取用户的所有对话"""
    conversations = []
    cursor = db.db.conversations.find({"user_id": ObjectId(user_id)}).sort("updated_at", -1)
    
    async for conversation in cursor:
        conversation["_id"] = str(conversation["_id"])
        conversation["user_id"] = str(conversation["user_id"])
        conversations.append(conversation)
    
    return conversations