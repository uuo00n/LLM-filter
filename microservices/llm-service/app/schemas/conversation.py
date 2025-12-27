from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class SensitiveWordInfoResponse(BaseModel):
    """敏感词信息结构化模型
    字段说明：
    - word: 敏感词文本
    - category: 一级分类
    - subcategory: 二级分类
    - severity: 严重程度（数值越大越严重）
    """
    word: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    severity: Optional[int] = None

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    role: str
    content: str
    timestamp: datetime
    contains_sensitive_words: bool
    sensitive_words_found: List[SensitiveWordInfoResponse]

class ConversationResponse(BaseModel):
    id: str
    title: Optional[str] = None
    messages: List[MessageResponse]
    created_at: datetime
    updated_at: datetime

class ConversationDocOut(BaseModel):
    id: str
    _id: Optional[str] = None
    user_id: Optional[str] = None
    title: Optional[str] = None
    messages: List[MessageResponse]
    created_at: datetime
    updated_at: datetime

class CreatedId(BaseModel):
    id: str

class DeleteResult(BaseModel):
    deleted: bool
    message: Optional[str] = None

class MessageSendResult(BaseModel):
    contains_sensitive_words: bool
    sensitive_words_found: List[SensitiveWordInfoResponse]
    assistant_response: str