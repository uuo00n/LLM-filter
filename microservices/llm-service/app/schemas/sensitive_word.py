from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class SensitiveWordCreate(BaseModel):
    word: str
    category: str
    subcategory: Optional[str] = None
    severity: Optional[int] = Field(1, ge=1, le=5)

class SensitiveWordBulkImport(BaseModel):
    words: List[SensitiveWordCreate]

class SensitiveWordInfoResponse(BaseModel):
    word: str
    category: str
    subcategory: Optional[str] = None
    severity: Optional[int] = 1

class SensitiveWordResponse(BaseModel):
    id: str
    word: str
    category: str
    subcategory: Optional[str] = None
    severity: Optional[int] = 1
    created_at: datetime
    updated_at: Optional[datetime] = None

class SensitiveRecordResponse(BaseModel):
    id: str
    user_id: str
    conversation_id: str
    message_content: str
    sensitive_words_found: List[SensitiveWordInfoResponse]
    highest_severity: int = 1
    timestamp: datetime

class CategoryCreate(BaseModel):
    name: str
    subcategories: List[str] = []

class CategoryResponse(BaseModel):
    name: str
    subcategories: List[str]

class CategoriesResponse(BaseModel):
    categories: Dict[str, List[str]]