from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

# 自定义ObjectId字段
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        # Pydantic v2 仍支持生成器形式的验证器
        yield cls.validate

    @classmethod
    def validate(cls, v):
        # 校验传入的值是否是合法的 ObjectId 字符串
        if not ObjectId.is_valid(v):
            raise ValueError("无效的ObjectId")
        return ObjectId(v)

    # Pydantic v2 中不再支持 __modify_schema__；如需自定义
    # JSON Schema，可实现 __get_pydantic_json_schema__。当前
    # 版本先保持默认 Schema，以确保运行稳定。


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

    class Config:
        # 允许使用字段名进行赋值（即使定义了 alias）
        allow_population_by_field_name = True
        # 允许使用自定义类型（如 ObjectId）
        arbitrary_types_allowed = True
        # 将 ObjectId 序列化为字符串，便于前端展示
        json_encoders = {ObjectId: str}
        # 示例数据，便于接口文档和调试
        schema_extra = {
            "example": {
                "username": "user1",
                "email": "user1@example.com",
                "hashed_password": "hashed_password_here",
                "role": "user",
                "role_level": 1,
                "edition": "edu",
            }
        }