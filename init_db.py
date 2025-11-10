import asyncio
import motor.motor_asyncio
import os
from dotenv import load_dotenv
from datetime import datetime
from bson import ObjectId
from passlib.context import CryptContext

# 密码加密工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 加载 .env 环境变量，保持与后端一致的配置来源
load_dotenv()

# MongoDB连接配置
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "llm_filter_db")
# 运行模式：仅运行教育版或企业版之一（不混合）
APP_MODE = (os.getenv("APP_MODE", "edu") or "edu").lower()

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
    admin_id = ObjectId()       # 教育版管理员（用户名 admin）
    user_id = ObjectId()        # 教育版普通用户（用户名 user）
    user_biz_id = ObjectId()    # 企业版普通用户（用户名 user_biz）
    
    users = [
        # 系统管理员（标准：administrator，兼容：admin 用户名）
        {
            "_id": admin_id,
            "username": "admin",
            "email": "admin@example.com",
            "hashed_password": pwd_context.hash("admin123"),
            "role": "administrator",   # 统一使用标准角色名，兼容旧数据中的 "admin"
            "role_level": 5,            # 映射到最高等级
            "edition": "edu",          # 默认教育版
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        # 普通用户（教育版）
        {
            "_id": user_id,
            "username": "user",
            "email": "user@example.com",
            "hashed_password": pwd_context.hash("user123"),
            "role": "user",
            "role_level": 1,
            "edition": "edu",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        # 教育版：班主任、部门负责人、中层与校长
        {
            "_id": ObjectId(),
            "username": "manager_edu",
            "email": "manager_edu@example.com",
            "hashed_password": pwd_context.hash("manager123"),
            "role": "manager",
            "role_level": 2,
            "edition": "edu",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "_id": ObjectId(),
            "username": "leader_edu",
            "email": "leader_edu@example.com",
            "hashed_password": pwd_context.hash("leader123"),
            "role": "leader",
            "role_level": 3,
            "edition": "edu",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "_id": ObjectId(),
            "username": "master_edu",
            "email": "master_edu@example.com",
            "hashed_password": pwd_context.hash("master123"),
            "role": "master",
            "role_level": 4,
            "edition": "edu",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        # 企业版：员工、组长、负责人、高管与管理员
        {
            "_id": user_biz_id,
            "username": "user_biz",
            "email": "user_biz@example.com",
            "hashed_password": pwd_context.hash("userbiz123"),
            "role": "user",
            "role_level": 1,
            "edition": "biz",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "_id": ObjectId(),
            "username": "manager_biz",
            "email": "manager_biz@example.com",
            "hashed_password": pwd_context.hash("managerbiz123"),
            "role": "manager",
            "role_level": 2,
            "edition": "biz",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "_id": ObjectId(),
            "username": "leader_biz",
            "email": "leader_biz@example.com",
            "hashed_password": pwd_context.hash("leaderbiz123"),
            "role": "leader",
            "role_level": 3,
            "edition": "biz",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "_id": ObjectId(),
            "username": "master_biz",
            "email": "master_biz@example.com",
            "hashed_password": pwd_context.hash("masterbiz123"),
            "role": "master",
            "role_level": 4,
            "edition": "biz",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "_id": ObjectId(),
            "username": "administrator_biz",
            "email": "administrator_biz@example.com",
            "hashed_password": pwd_context.hash("adminbiz123"),
            "role": "administrator",
            "role_level": 5,
            "edition": "biz",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
    ]
    
    # 根据运行模式筛选用户（不混合）
    mode = APP_MODE if APP_MODE in {"edu", "biz"} else "edu"
    if mode != APP_MODE:
        print(f"警告：APP_MODE={APP_MODE} 非法，默认使用 edu")

    selected_users = [u for u in users if u["edition"] == mode]
    await db.users.insert_many(selected_users)
    print(f"已创建用户集合并添加 {len(selected_users)} 条记录（模式：{mode}）")
    
    # 创建敏感词集合并添加假数据
    sensitive_words = [
        {
            "word": "赌博",
            "category": "违法活动",
            "subcategory": "赌博",
            "severity": 3,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "色情",
            "category": "色情内容",
            "subcategory": "色情服务",
            "severity": 4,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "毒品",
            "category": "毒品相关",
            "subcategory": "毒品名称",
            "severity": 5,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "诈骗",
            "category": "诈骗相关",
            "subcategory": "网络诈骗",
            "severity": 4,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "暴力",
            "category": "暴力内容",
            "subcategory": "语言暴力",
            "severity": 3,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "自杀",
            "category": "不良内容",
            "subcategory": "自杀",
            "severity": 5,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "政治敏感",
            "category": "政治内容",
            "subcategory": "敏感事件",
            "severity": 4,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "种族歧视",
            "category": "歧视言论",
            "subcategory": "种族歧视",
            "severity": 4,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "性别歧视",
            "category": "歧视言论",
            "subcategory": "性别歧视",
            "severity": 3,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "恐怖主义",
            "category": "暴力内容",
            "subcategory": "恐怖主义",
            "severity": 5,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    await db.sensitive_words.insert_many(sensitive_words)
    print(f"已创建敏感词集合并添加 {len(sensitive_words)} 条记录")
    
    # 创建对话集合并添加假数据
    conversation_id = ObjectId()
    # 根据模式选择示例用户用于演示对话与敏感词记录
    sample_user_id = user_id if mode == "edu" else user_biz_id

    conversations = [
        {
            "_id": conversation_id,
            "user_id": sample_user_id,
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
            # 使用真实的 ObjectId，避免与模型类型不一致
            "user_id": sample_user_id,
            "conversation_id": conversation_id,
            "message_content": "我想了解一下赌博的事情",
            "sensitive_words_found": [
                {
                    "word": "赌博",
                    "category": "违法活动",
                    "subcategory": "赌博",
                    "severity": 3
                }
            ],
            "highest_severity": 3,
            "timestamp": datetime.now()
        },
        {
            # 第二条记录同样引用真实的 ObjectId
            "user_id": sample_user_id,
            "conversation_id": conversation_id,
            "message_content": "如何获取毒品和色情内容",
            "sensitive_words_found": [
                {
                    "word": "毒品",
                    "category": "毒品相关",
                    "subcategory": "毒品名称",
                    "severity": 5
                },
                {
                    "word": "色情",
                    "category": "色情内容",
                    "subcategory": "色情服务",
                    "severity": 4
                }
            ],
            "highest_severity": 5,
            "timestamp": datetime.now()
        }
    ]
    
    await db.sensitive_records.insert_many(sensitive_records)
    print(f"已创建敏感词记录集合并添加 {len(sensitive_records)} 条记录")
    
    print("\n数据库初始化完成！")
    print("\n测试账号 (模式: %s):" % mode)
    if mode == "edu":
        print("教育版管理员: admin / admin123  (role=administrator, edition=edu)")
        print("教育版普通用户: user / user123  (role=user, edition=edu)")
    else:
        print("企业版管理员: administrator_biz / adminbiz123  (role=administrator, edition=biz)")
        print("企业版普通用户: user_biz / userbiz123  (role=user, edition=biz)")

if __name__ == "__main__":
    asyncio.run(init_db())