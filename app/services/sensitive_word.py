from typing import List, Dict, Any, Optional
from datetime import datetime
from bson.objectid import ObjectId
from app.db.mongodb import db
from app.utils.sensitive_word_filter import sensitive_word_filter
from app.models.sensitive_word import (
    SensitiveWordModel, SensitiveRecordModel,
    SENSITIVE_WORD_CATEGORIES, SENSITIVE_WORD_SUBCATEGORIES
)
from app.schemas.sensitive_word import SensitiveWordCreate

async def add_sensitive_word(
    word: str, 
    category: str, 
    subcategory: Optional[str] = None,
    severity: int = 1
) -> str:
    """添加敏感词"""
    # 验证分类是否有效
    if category not in SENSITIVE_WORD_CATEGORIES:
        raise ValueError(f"无效的分类: {category}。有效分类: {', '.join(SENSITIVE_WORD_CATEGORIES)}")
    
    # 验证子分类是否有效
    if subcategory and category in SENSITIVE_WORD_SUBCATEGORIES:
        if subcategory not in SENSITIVE_WORD_SUBCATEGORIES[category]:
            raise ValueError(f"无效的子分类: {subcategory}。{category}的有效子分类: {', '.join(SENSITIVE_WORD_SUBCATEGORIES[category])}")
    
    # 使用全局数据库连接
    sensitive_word = SensitiveWordModel(
        word=word,
        category=category,
        subcategory=subcategory,
        severity=severity
    )
    
    result = await db.db.sensitive_words.insert_one(sensitive_word.dict())
    
    # 更新敏感词过滤器
    await sensitive_word_filter.load_sensitive_words()
    
    return str(result.inserted_id)

async def bulk_import_sensitive_words(words: List[SensitiveWordCreate]) -> int:
    """批量导入敏感词"""
    if not words:
        return 0
    
    # 转换为模型对象列表
    word_models = []
    for word_data in words:
        # 验证分类是否有效
        if word_data.category not in SENSITIVE_WORD_CATEGORIES:
            raise ValueError(f"无效的分类: {word_data.category}。有效分类: {', '.join(SENSITIVE_WORD_CATEGORIES)}")
        
        # 验证子分类是否有效
        if word_data.subcategory and word_data.category in SENSITIVE_WORD_SUBCATEGORIES:
            if word_data.subcategory not in SENSITIVE_WORD_SUBCATEGORIES[word_data.category]:
                raise ValueError(f"无效的子分类: {word_data.subcategory}。{word_data.category}的有效子分类: {', '.join(SENSITIVE_WORD_SUBCATEGORIES[word_data.category])}")
        
        word_model = SensitiveWordModel(
            word=word_data.word,
            category=word_data.category,
            subcategory=word_data.subcategory,
            severity=word_data.severity
        )
        word_models.append(word_model.dict())
    
    # 批量插入数据库
    result = await db.db.sensitive_words.insert_many(word_models)
    
    # 更新敏感词过滤器
    await sensitive_word_filter.load_sensitive_words()
    
    return len(result.inserted_ids)

async def delete_sensitive_word(word_id: str) -> bool:
    """删除敏感词"""
    # 使用全局数据库连接
    result = await db.db.sensitive_words.delete_one({"_id": ObjectId(word_id)})
    
    # 更新敏感词过滤器
    if result.deleted_count > 0:
        await sensitive_word_filter.load_sensitive_words()
        return True
    return False

async def get_all_sensitive_words(
    category: str = None,
    subcategory: str = None,
    min_severity: int = None,
    max_severity: int = None
) -> List[Dict[str, Any]]:
    """获取所有敏感词，支持按类型和严重程度筛选"""
    # 使用全局数据库连接
    query = {}
    
    # 按分类筛选
    if category:
        query["category"] = category
    
    # 按子分类筛选
    if subcategory:
        query["subcategory"] = subcategory
    
    # 按严重程度范围筛选
    if min_severity is not None or max_severity is not None:
        query["severity"] = {}
        if min_severity is not None:
            query["severity"]["$gte"] = min_severity
        if max_severity is not None:
            query["severity"]["$lte"] = max_severity
    
    cursor = db.db.sensitive_words.find(query)
    sensitive_words = []
    async for document in cursor:
        sensitive_words.append({
            "id": str(document["_id"]),
            "word": document["word"],
            "category": document.get("category"),
            "subcategory": document.get("subcategory"),
            "severity": document.get("severity", 1),
            "created_at": document.get("created_at", datetime.now())
        })
    return sensitive_words

async def check_sensitive_words(text: str) -> Dict[str, Any]:
    """检查文本中是否包含敏感词"""
    # 使用敏感词过滤器检查文本
    result = sensitive_word_filter.check_text(text)
    return result

async def record_sensitive_word_usage(
    user_id: str,
    conversation_id: str,
    message_content: str,
    sensitive_words_found: List[Dict[str, Any]]
) -> None:
    """记录敏感词使用情况"""
    if not sensitive_words_found:
        return
    
    # 计算最高严重程度
    highest_severity = max([word.get("severity", 1) for word in sensitive_words_found]) if sensitive_words_found else 0
    
    # 使用全局数据库连接
    record = SensitiveRecordModel(
        user_id=user_id,
        conversation_id=conversation_id,
        message_content=message_content,
        sensitive_words_found=sensitive_words_found,
        highest_severity=highest_severity
    )
    await db.db.sensitive_records.insert_one(record.dict())

async def get_sensitive_records(
    user_id: str = None, 
    conversation_id: str = None,
    category: str = None,
    subcategory: str = None,
    min_severity: int = None,
    max_severity: int = None,
    start_date: datetime = None, 
    end_date: datetime = None
) -> List[Dict[str, Any]]:
    """获取敏感词记录，支持按类型、严重程度和时间筛选"""
    # 使用全局数据库连接
    query = {}
    
    # 按用户ID筛选
    if user_id:
        query["user_id"] = user_id
    
    # 按对话ID筛选
    if conversation_id:
        query["conversation_id"] = conversation_id
    
    # 按时间范围筛选
    if start_date and end_date:
        query["timestamp"] = {"$gte": start_date, "$lte": end_date}
    elif start_date:
        query["timestamp"] = {"$gte": start_date}
    elif end_date:
        query["timestamp"] = {"$lte": end_date}
    
    # 按敏感词类型筛选
    if category:
        query["sensitive_words_found.category"] = category
    
    # 按敏感词子类型筛选
    if subcategory:
        query["sensitive_words_found.subcategory"] = subcategory
    
    # 按严重程度范围筛选
    if min_severity is not None or max_severity is not None:
        query["highest_severity"] = {}
        if min_severity is not None:
            query["highest_severity"]["$gte"] = min_severity
        if max_severity is not None:
            query["highest_severity"]["$lte"] = max_severity
    
    cursor = db.db.sensitive_records.find(query).sort("timestamp", -1)
    records = []
    async for document in cursor:
        records.append({
            "id": str(document["_id"]),
            "user_id": document["user_id"],
            "conversation_id": document["conversation_id"],
            "message_content": document["message_content"],
            "sensitive_words_found": document["sensitive_words_found"],
            "highest_severity": document.get("highest_severity", 1),
            "timestamp": document["timestamp"]
        })
    return records

async def get_categories() -> Dict[str, List[str]]:
    """获取所有分类和子分类"""
    # 使用全局数据库连接
    categories = {}
    
    # 添加默认分类
    for category, subcategories in SENSITIVE_WORD_SUBCATEGORIES.items():
        categories[category] = subcategories
    
    # 从数据库中获取额外的分类
    cursor = db.db.sensitive_words.aggregate([
        {"$group": {"_id": "$category", "subcategories": {"$addToSet": "$subcategory"}}}
    ])
    
    async for doc in cursor:
        category = doc["_id"]
        if category and category not in categories:
            # 过滤掉None值
            subcategories = [sub for sub in doc["subcategories"] if sub]
            categories[category] = subcategories
    
    return categories

async def add_category(category: str, subcategories: List[str] = None) -> bool:
    """添加新分类"""
    # 使用全局数据库连接
    if not category:
        return False
    
    # 检查分类是否已存在
    existing = await db.db.sensitive_words.find_one({"category": category})
    if existing:
        return False
    
    # 创建一个占位敏感词来添加分类
    placeholder = SensitiveWordModel(
        word=f"__placeholder_{category}__",
        category=category,
        subcategory=subcategories[0] if subcategories else None,
        severity=1,
        is_placeholder=True
    )
    
    await db.db.sensitive_words.insert_one(placeholder.dict())
    return True

async def update_category(category: str, subcategories: List[str]) -> bool:
    """更新分类的子分类"""
    # 使用全局数据库连接
    if not category:
        return False
    
    # 检查分类是否存在
    existing = await db.db.sensitive_words.find_one({"category": category})
    if not existing:
        return False
    
    # 更新所有使用此分类但子分类不在新列表中的敏感词
    if subcategories:
        await db.db.sensitive_words.update_many(
            {"category": category, "subcategory": {"$nin": subcategories}},
            {"$set": {"subcategory": subcategories[0]}}
        )
    
    return True

async def delete_category(category: str, reassign_to: str = None) -> bool:
    """删除分类"""
    # 使用全局数据库连接
    if not category:
        return False
    
    # 如果提供了重新分配的分类，则更新敏感词
    if reassign_to:
        await db.db.sensitive_words.update_many(
            {"category": category},
            {"$set": {"category": reassign_to, "subcategory": None}}
        )
    else:
        # 否则删除该分类的所有敏感词
        await db.db.sensitive_words.delete_many({"category": category})
    
    # 删除占位敏感词
    await db.db.sensitive_words.delete_many({"category": category, "is_placeholder": True})
    
    # 更新敏感词过滤器
    await sensitive_word_filter.load_sensitive_words()
    
    return True