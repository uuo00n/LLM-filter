from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from bson import ObjectId
from app.models.user import PyObjectId

# 消息模型
class MessageModel(BaseModel):
    role: str  # "user" 或 "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    contains_sensitive_words: bool = False
    sensitive_words_found: List[str] = []

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

# 对话模型
class ConversationModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    messages: List[MessageModel] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    @field_serializer("id", when_used="json")
    def serialize_id(self, v: ObjectId):
        return str(v)
