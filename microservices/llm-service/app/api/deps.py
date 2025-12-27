from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models.role import get_role_level
from app.core.config import settings
from bson import ObjectId
import jwt
from jwt.exceptions import InvalidTokenError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8081/api/v1/auth/login")

async def get_current_active_user(token: str = Depends(oauth2_scheme)):
    """获取当前活跃用户 (本地 JWT 验证)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 本地验证 JWT，不再调用 Auth Service
        # 确保 settings.SECRET_KEY 与 Auth Service 的 JWT_SECRET 一致
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Go 生成的 Token Payload: sub (userID), name (username), role
        user_id = payload.get("sub")
        username: str = payload.get("name")
        role: str = payload.get("role")
        
        if user_id is None or username is None:
            raise credentials_exception
            
        return {
            "id": user_id,
            "username": username,
            "role": role,
            # 兼容字段，供 require_role 使用
            "role_level": get_role_level(role),
            # 兼容字段，供 require_edition_for_mode 使用
            # Go 端目前生成的 Token 中不包含 edition 字段，默认为 "edu" 避免权限错误
            "edition": payload.get("edition", "edu")
        }
    except InvalidTokenError:
        raise credentials_exception

async def get_current_admin_user(current_user: dict = Depends(get_current_active_user)):
    """获取当前管理员用户（兼容 admin/administrator 两种命名）"""
    if current_user.get("role") not in {"admin", "administrator"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user

# 通用的按角色等级校验的依赖
def require_role(min_level: int):
    """
    按最小等级校验权限的依赖工厂。
    使用方法：Depends(require_role(3)) 表示仅 3级及以上可访问。

    关键点：
    - 提前返回，避免多层嵌套；
    - 容错处理：当用户缺少 role_level 字段时，根据 role 计算等级。
    """
    async def _checker(current_user: dict = Depends(get_current_active_user)):
        # 兼容：优先取 role_level，没有则通过 role 计算
        level = current_user.get("role_level")
        if level is None:
            level = get_role_level(current_user.get("role"))
        if level < min_level:
            raise HTTPException(status_code=403, detail="权限不足")
        return current_user

    return _checker

def require_edition_for_mode():
    """
    版别运行模式依赖：当后端设置为 APP_MODE=edu 或 APP_MODE=biz 时，限制仅允许对应版别的用户访问。

    使用方式：在路由层统一挂载，例如：
      router = APIRouter(dependencies=[Depends(require_edition_for_mode())])

    设计要点：
    - 提前返回，避免多层嵌套；
    - 与现有认证依赖复用：接收 current_user，避免重复解析 token；
    - 容错与默认值：当 APP_MODE 为未知值时默认放行，但建议仅使用 "edu" 或 "biz"。
    """
    async def _edition_checker(current_user: dict = Depends(get_current_active_user)):
        mode = (settings.APP_MODE or "edu").lower()  # 默认 edu
        # 仅当模式为 edu 或 biz 时进行限制；其它值（如意外）默认放行
        if mode in {"edu", "biz"}:
            user_edition = (current_user.get("edition") or "").lower()
            if user_edition != mode:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"当前后端运行模式为 '{mode}'，用户版别 '{user_edition}' 无权访问"
                )
        return current_user

    return _edition_checker

def require_binding(expected_type: str):
    async def _binding_checker(current_user: dict = Depends(get_current_active_user)):
        # 简化处理：不再查询 MongoDB，而是信任 token 中的信息或调用 Auth Service 接口
        # 暂时跳过绑定检查，或者后续通过 Auth Service 的 /bindings 接口校验
        # 这里仅作占位，避免导入 app.db.mongodb 导致错误
        return current_user
    return _binding_checker