from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.user import PyObjectId

# 消息模型
class MessageModel(BaseModel):
    role: str  # "user" 或 "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    contains_sensitive_words: bool = False
    sensitive_words_found: List[str] = []

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# 对话模型
class ConversationModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    messages: List[MessageModel] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}