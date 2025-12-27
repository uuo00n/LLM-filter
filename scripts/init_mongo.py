import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

# 配置
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "llm_filter_db")

async def init_mongo():
    print(f"Connecting to MongoDB: {MONGODB_URL} ...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]

    # 清空集合 (彻底清空旧业务数据)
    # 只保留 LLM 相关的集合
    collections = ["sensitive_words", "filter_logs", "audit_trails", 
                   "attendance", "conduct", "leaves", "directives", "conversations"] # 顺便清理掉旧的
    for col in collections:
        await db[col].drop()
    print("Cleaned up MongoDB collections.")

    # 1. 初始化敏感词库 (Sensitive Words)
    print("Initializing sensitive words library...")
    sensitive_words = [
        {"word": "暴力", "category": "violence", "level": "high"},
        {"word": "赌博", "category": "gambling", "level": "high"},
        {"word": "作弊", "category": "academic_misconduct", "level": "medium"},
        {"word": "代写", "category": "academic_misconduct", "level": "medium"},
        {"word": "色情", "category": "pornography", "level": "high"},
        {"word": "自杀", "category": "self_harm", "level": "critical"},
        {"word": "约架", "category": "violence", "level": "high"}
    ]
    
    for sw in sensitive_words:
        await db.sensitive_words.insert_one({
            "word": sw["word"],
            "category": sw["category"],
            "level": sw["level"],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
    
    print(f"Inserted {len(sensitive_words)} sensitive words.")

    print("MongoDB initialization completed successfully! (LLM Filter Data Only)")
    client.close()

if __name__ == "__main__":
    asyncio.run(init_mongo())
