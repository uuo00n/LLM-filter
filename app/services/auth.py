from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.db.mongodb import db
from bson import ObjectId
from app.models.role import get_role_level

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """获取密码哈希值"""
    return pwd_context.hash(password)

async def authenticate_user(username: str, password: str):
    """验证用户"""
    user = await db.db.users.find_one({"username": username})
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌
    关键点：
    - 在 JWT 载荷中加入角色与版别信息，便于前端解码后快速展示；
    - 仍以服务端数据库查询为准，避免客户端伪造带来的安全问题。
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str):
    """获取当前用户"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        user = await db.db.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            return None
        
        # 兼容兜底：若用户数据缺少角色等级或版别，则进行补充
        if user.get("role_level") is None:
            user["role_level"] = get_role_level(user.get("role"))
        if user.get("edition") is None:
            user["edition"] = "edu"  # 默认版别为教育版
        return user
    except JWTError:
        return None