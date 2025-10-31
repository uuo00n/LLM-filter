import asyncio
import motor.motor_asyncio
from datetime import datetime
from bson import ObjectId
from passlib.context import CryptContext

# 密码加密工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB连接配置
MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "llm_filter_db"

async def init_db():
    # 连接到MongoDB
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    # 清空现有集合（如果存在）
    collections = await db.list_collection_names()
    for collection in collections:
        await db[collection].drop()
    
    print("已清空现有集合")
    
    # 创建用户集合并添加假数据
    admin_id = ObjectId()
    user_id = ObjectId()
    
    users = [
        {
            "_id": admin_id,
            "username": "admin",
            "email": "admin@example.com",
            "hashed_password": pwd_context.hash("admin123"),
            "role": "admin",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "_id": user_id,
            "username": "user",
            "email": "user@example.com",
            "hashed_password": pwd_context.hash("user123"),
            "role": "user",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    await db.users.insert_many(users)
    print(f"已创建用户集合并添加 {len(users)} 条记录")
    
    # 创建敏感词集合并添加假数据
    sensitive_words = [
        {
            "word": "赌博",
            "category": "违法活动",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "色情",
            "category": "违法活动",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "毒品",
            "category": "违法活动",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "诈骗",
            "category": "违法活动",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "暴力",
            "category": "不良内容",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "自杀",
            "category": "不良内容",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "政治敏感",
            "category": "政治内容",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    await db.sensitive_words.insert_many(sensitive_words)
    print(f"已创建敏感词集合并添加 {len(sensitive_words)} 条记录")
    
    # 创建对话集合并添加假数据
    conversation_id = ObjectId()
    conversations = [
        {
            "_id": conversation_id,
            "user_id": user_id,
            "messages": [
                {
                    "role": "user",
                    "content": "你好，请问你是谁？",
                    "timestamp": datetime.now(),
                    "contains_sensitive_words": False,
                    "sensitive_words_found": []
                },
                {
                    "role": "assistant",
                    "content": "你好！我是一个AI助手，可以回答你的问题和提供帮助。有什么我可以帮你的吗？",
                    "timestamp": datetime.now(),
                    "contains_sensitive_words": False,
                    "sensitive_words_found": []
                }
            ],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    await db.conversations.insert_many(conversations)
    print(f"已创建对话集合并添加 {len(conversations)} 条记录")
    
    # 创建敏感词记录集合并添加假数据
    sensitive_records = [
        {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "message_content": "我想了解一下赌博的方法",
            "sensitive_words_found": ["赌博"],
            "timestamp": datetime.now()
        }
    ]
    
    await db.sensitive_records.insert_many(sensitive_records)
    print(f"已创建敏感词记录集合并添加 {len(sensitive_records)} 条记录")
    
    print("\n数据库初始化完成！")
    print("\n测试账号:")
    print("管理员账号: admin / admin123")
    print("用户账号: user / user123")

if __name__ == "__main__":
    asyncio.run(init_db())