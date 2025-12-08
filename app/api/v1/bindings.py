from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from typing import Optional
from app.api.deps import require_edition_for_mode, get_current_active_user, require_role
from app.services.bindings import create_binding, delete_binding, get_binding_by_account

router = APIRouter(dependencies=[Depends(require_edition_for_mode())])

class BindingPayload(BaseModel):
    person_id: str
    type: str
    primary: bool = True

class ActionResult(BaseModel):
    success: bool

class BindingOut(BaseModel):
    _id: str
    account_id: str
    person_id: str
    type: str
    primary: bool

@router.post(
    "",
    summary="创建主绑定",
    description="为当前账号创建人物主绑定（student/teacher），同类型主绑定唯一。",
    response_model=ActionResult,
    responses={
        400: {"description": "主绑定已存在或参数错误", "content": {"application/json": {"example": {"detail": "主绑定已存在或参数错误"}}}},
        401: {"description": "认证失败", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
    },
)
async def bind(payload: BindingPayload, current_user: dict = Depends(require_role(2))) -> ActionResult:
    ok = await create_binding(str(current_user["_id"]), payload.person_id, payload.type, payload.primary)
    if not ok:
        raise HTTPException(status_code=400, detail="主绑定已存在或参数错误")
    return {"success": True}

@router.delete(
    "/{person_id}",
    summary="删除绑定",
    description="删除当前账号与指定人物的绑定。",
    response_model=ActionResult,
    responses={
        404: {"description": "未找到绑定", "content": {"application/json": {"example": {"detail": "未找到绑定"}}}},
        401: {"description": "认证失败", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
    },
)
async def unbind(person_id: str = Path(..., description="人物ID"), current_user: dict = Depends(require_role(2))) -> ActionResult:
    ok = await delete_binding(str(current_user["_id"]), person_id)
    if not ok:
        raise HTTPException(status_code=404, detail="未找到绑定")
    return {"success": True}

@router.get(
    "/me",
    summary="查询当前账号的主绑定",
    description="返回当前账号的主绑定信息（account_id/person_id/type/primary）。",
    response_model=BindingOut,
    responses={
        404: {"description": "未绑定人物", "content": {"application/json": {"example": {"detail": "未绑定人物"}}}},
        401: {"description": "认证失败", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
    },
)
async def me(current_user: dict = Depends(get_current_active_user)) -> BindingOut:
    b = await get_binding_by_account(str(current_user["_id"]))
    if not b:
        raise HTTPException(status_code=404, detail="未绑定人物")
    b["_id"] = str(b["_id"])  
    b["account_id"] = str(b["account_id"])  
    b["person_id"] = str(b["person_id"])  
    return b
