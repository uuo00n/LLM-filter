from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    # 角色采用 Literal 强校验，同时兼容历史中的 "admin"
    role: Literal["user", "manager", "leader", "master", "administrator", "admin"]
    # 新增：角色等级，便于前端快速展示权限范围
    role_level: int
    # 版别采用 Literal 强校验：教育版/企业版
    edition: Literal["edu", "biz"]

class Token(BaseModel):
    access_token: str = Field(description="访问令牌（JWT）")
    token_type: str = Field(description="令牌类型，固定为 bearer")
    # 扩展：在登录响应中返回关键用户属性，减少额外查询（也可单独提供 /me 接口）
    # 使用 Literal 限定角色取值范围，保持与 UserResponse 一致
    role: Optional[Literal["user", "manager", "leader", "master", "administrator", "admin"]] = Field(default=None, description="系统角色")
    role_level: Optional[int] = Field(default=None, description="角色等级（1~5）")
    # 使用 Literal 限定版别取值范围
    edition: Optional[Literal["edu", "biz"]] = Field(default=None, description="版别（教育/企业）")

    # 绑定信息（实体化）
    person_id: Optional[str] = Field(default=None, description="主绑定的人物ID（persons._id）")
    person_type: Optional[Literal["student", "teacher", "staff"]] = Field(default=None, description="主绑定人物类型")
    bound_primary: Optional[bool] = Field(default=None, description="是否存在主绑定")

class TokenData(BaseModel):
    user_id: Optional[str] = None
    # TokenData 也保持与 Token 一致的角色限定，便于类型安全
    role: Optional[Literal["user", "manager", "leader", "master", "administrator", "admin"]] = None
    role_level: Optional[int] = None
    edition: Optional[Literal["edu", "biz"]] = None