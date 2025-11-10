from typing import Optional, Literal
from pydantic import BaseModel, EmailStr

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
    access_token: str
    token_type: str
    # 扩展：在登录响应中返回关键用户属性，减少额外查询（也可单独提供 /me 接口）
    # 使用 Literal 限定角色取值范围，保持与 UserResponse 一致
    role: Optional[Literal["user", "manager", "leader", "master", "administrator", "admin"]] = None
    role_level: Optional[int] = None
    # 使用 Literal 限定版别取值范围
    edition: Optional[Literal["edu", "biz"]] = None

class TokenData(BaseModel):
    user_id: Optional[str] = None
    # TokenData 也保持与 Token 一致的角色限定，便于类型安全
    role: Optional[Literal["user", "manager", "leader", "master", "administrator", "admin"]] = None
    role_level: Optional[int] = None
    edition: Optional[Literal["edu", "biz"]] = None