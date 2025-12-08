from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from bson import ObjectId
from pydantic_core import core_schema

# 自定义ObjectId字段
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        def validate(v):
            if isinstance(v, ObjectId):
                return v
            if ObjectId.is_valid(v):
                return ObjectId(v)
            raise ValueError("无效的ObjectId")
        return core_schema.no_info_plain_validator_function(validate)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema_, handler):
        json_schema = handler(core_schema_)
        json_schema.update({"type": "string"})
        return json_schema


# 用户模型（修复缩进错误：确保为顶层类定义）
class UserModel(BaseModel):
    # MongoDB 主键，使用别名 _id，序列化时转换为字符串
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    # 用户名
    username: str
    # 邮箱（此处仅为字符串，外层使用 EmailStr 的 Schema 做校验）
    email: str
    # 哈希后的密码
    hashed_password: str
    # 角色字符串（兼容历史中的 "admin"）。建议与 app/models/role.py 中的枚举保持一致
    role: str = "user"
    # 角色等级（1~5），用于统一的权限判断
    role_level: int = 1
    # 版别："edu"（教育版）或 "biz"（企业版）
    edition: str = "edu"
    # 创建与更新时间
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "username": "user1",
                "email": "user1@example.com",
                "hashed_password": "hashed_password_here",
                "role": "user",
                "role_level": 1,
                "edition": "edu",
            }
        },
    )

    @field_serializer("id", when_used="json")
    def serialize_id(self, v: ObjectId):
        return str(v)
