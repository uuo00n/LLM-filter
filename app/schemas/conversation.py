from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    role: str
    content: str
    timestamp: datetime
    contains_sensitive_words: bool
    sensitive_words_found: List[str]

class ConversationResponse(BaseModel):
    id: str
    messages: List[MessageResponse]
    created_at: datetime
    updated_at: datetime