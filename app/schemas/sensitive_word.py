from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class SensitiveWordCreate(BaseModel):
    word: str
    category: Optional[str] = None

class SensitiveWordResponse(BaseModel):
    id: str
    word: str
    category: Optional[str] = None
    created_at: datetime

class SensitiveRecordResponse(BaseModel):
    id: str
    user_id: str
    conversation_id: str
    message_content: str
    sensitive_words_found: List[str]
    timestamp: datetime