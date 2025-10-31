from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.user import PyObjectId

# 敏感词类型枚举（可扩展）
SENSITIVE_WORD_CATEGORIES = [
    "违法活动",
    "不良内容",
    "政治内容",
    "歧视言论",
    "暴力内容",
    "色情内容",
    "毒品相关",
    "赌博相关",
    "诈骗相关",
    "其他"
]

# 敏感词子类型枚举（可扩展）
SENSITIVE_WORD_SUBCATEGORIES = {
    "违法活动": ["贩毒", "赌博", "诈骗", "传销", "其他违法"],
    "不良内容": ["自杀", "自残", "暴力", "血腥", "其他不良"],
    "政治内容": ["敏感人物", "敏感事件", "敏感地区", "其他政治"],
    "歧视言论": ["种族歧视", "性别歧视", "地域歧视", "其他歧视"],
    "暴力内容": ["肢体暴力", "语言暴力", "恐怖主义", "其他暴力"],
    "色情内容": ["露骨描述", "性暗示", "色情服务", "其他色情"],
    "毒品相关": ["毒品名称", "制毒方法", "吸毒工具", "其他毒品"],
    "赌博相关": ["赌博方式", "赌博平台", "赌博工具", "其他赌博"],
    "诈骗相关": ["电信诈骗", "网络诈骗", "金融诈骗", "其他诈骗"],
    "其他": ["未分类"]
}

# 敏感词模型
class SensitiveWordModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    word: str
    category: str = Field(..., description="敏感词主分类")
    subcategory: Optional[str] = Field(None, description="敏感词子分类")
    severity: Optional[int] = Field(1, description="严重程度 1-5，5为最严重", ge=1, le=5)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# 敏感词详细信息
class SensitiveWordInfo(BaseModel):
    word: str
    category: str
    subcategory: Optional[str] = None
    severity: Optional[int] = 1

# 敏感词记录模型
class SensitiveRecordModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    conversation_id: PyObjectId
    message_content: str
    sensitive_words_found: List[SensitiveWordInfo]  # 使用详细信息替代简单字符串列表
    highest_severity: int = 1  # 记录中最高的严重程度
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}