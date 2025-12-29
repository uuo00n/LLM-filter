from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_admin(payload: dict = Depends(get_current_user)):
    """仅允许管理员访问"""
    role = payload.get("role")
    # 兼容常见的管理员角色标识
    if role not in ["admin", "administrator", "root"]:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限 (Administrator access required)",
        )
    return payload
