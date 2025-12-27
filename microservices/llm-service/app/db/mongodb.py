from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db = MongoDB()

async def connect_to_mongo():
    """连接到MongoDB数据库"""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.db = db.client[settings.DB_NAME]
    print("Connected to MongoDB")

async def close_mongo_connection():
    """关闭MongoDB连接"""
    if db.client:
        db.client.close()
        print("Closed MongoDB connection")