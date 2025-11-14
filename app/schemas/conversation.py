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

class ConversationDocOut(BaseModel):
    _id: str
    user_id: Optional[str] = None
    messages: List[MessageResponse]
    created_at: datetime
    updated_at: datetime

class CreatedId(BaseModel):
    id: str

class MessageSendResult(BaseModel):
    contains_sensitive_words: bool
    sensitive_words_found: List[str]
    assistant_response: str