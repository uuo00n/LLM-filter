from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

    def connect(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB_NAME]
        print(f"Connected to MongoDB at {settings.MONGODB_URL}")

    def close(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed")

db = Database()

async def get_database():
    return db.db
