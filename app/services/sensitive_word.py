from typing import List, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import db
from app.utils.sensitive_word_filter import sensitive_word_filter

async def add_sensitive_word(word: str, category: str = None) -> str:
    """添加敏感词"""
    sensitive_word = {
        "word": word,
        "category": category,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    result = await db.db.sensitive_words.insert_one(sensitive_word)
    
    # 更新敏感词过滤器
    await sensitive_word_filter.load_sensitive_words()
    
    return str(result.inserted_id)

async def delete_sensitive_word(word_id: str) -> bool:
    """删除敏感词"""
    result = await db.db.sensitive_words.delete_one({"_id": ObjectId(word_id)})
    
    # 更新敏感词过滤器
    await sensitive_word_filter.load_sensitive_words()
    
    return result.deleted_count > 0

async def get_all_sensitive_words() -> List[Dict[str, Any]]:
    """获取所有敏感词"""
    sensitive_words = []
    cursor = db.db.sensitive_words.find().sort("word", 1)
    
    async for word in cursor:
        word["_id"] = str(word["_id"])
        sensitive_words.append(word)
    
    return sensitive_words

async def get_sensitive_records(
    user_id: str = None, 
    start_date: datetime = None, 
    end_date: datetime = None
) -> List[Dict[str, Any]]:
    """获取敏感词记录"""
    query = {}
    
    if user_id:
        query["user_id"] = ObjectId(user_id)
    
    if start_date and end_date:
        query["timestamp"] = {"$gte": start_date, "$lte": end_date}
    elif start_date:
        query["timestamp"] = {"$gte": start_date}
    elif end_date:
        query["timestamp"] = {"$lte": end_date}
    
    records = []
    cursor = db.db.sensitive_records.find(query).sort("timestamp", -1)
    
    async for record in cursor:
        record["_id"] = str(record["_id"])
        record["user_id"] = str(record["user_id"])
        record["conversation_id"] = str(record["conversation_id"])
        records.append(record)
    
    return records