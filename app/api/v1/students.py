from fastapi import APIRouter, Depends, HTTPException, Path, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.api.deps import require_edition_for_mode, require_role
from app.services.student_binding import bind_user_to_student, unbind_user_from_student
from app.services.dashboard import _get_student_by_user

router = APIRouter(dependencies=[Depends(require_edition_for_mode())])

class BindPayload(BaseModel):
    user_id: str

class ActionResult(BaseModel):
    success: bool

class StudentOut(BaseModel):
    _id: str
    student_id: Optional[str] = None
    name: Optional[str] = None
    class_id: Optional[str] = None

@router.post(
    "/{student_id}/bind",
    response_model=ActionResult,
    summary="绑定学生",
    description="为指定学生建立主绑定（需角色等级≥2）。",
    responses={
        400: {"description": "绑定失败或学生不存在", "content": {"application/json": {"example": {"detail": "用户已绑定其他学生或学生不存在"}}}},
        401: {"description": "认证失败", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
    },
)
async def bind(student_id: str = Path(..., description="学生ID"), payload: BindPayload = Body(..., description="绑定参数"), current_user: dict = Depends(require_role(2))) -> ActionResult:
    ok = await bind_user_to_student(payload.user_id, student_id)
    if not ok:
        raise HTTPException(status_code=400, detail="用户已绑定其他学生或学生不存在")
    return {"success": True}

@router.delete(
    "/{student_id}/bind",
    response_model=ActionResult,
    summary="解除学生绑定",
    description="解除当前用户与指定学生的主绑定（需角色等级≥2）。",
    responses={
        404: {"description": "未找到或未绑定", "content": {"application/json": {"example": {"detail": "学生不存在或未绑定"}}}},
        401: {"description": "认证失败", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
    },
)
async def unbind(student_id: str = Path(..., description="学生ID"), current_user: dict = Depends(require_role(2))) -> ActionResult:
    ok = await unbind_user_from_student(student_id)
    if not ok:
        raise HTTPException(status_code=404, detail="学生不存在或未绑定")
    return {"success": True}

@router.get(
    "/me",
    response_model=StudentOut,
    summary="查询当前绑定学生",
    description="返回当前用户绑定的学生信息（需角色等级≥1）。",
    responses={
        404: {"description": "未绑定学生", "content": {"application/json": {"example": {"detail": "当前用户未绑定学生"}}}},
        401: {"description": "认证失败", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
    },
)
async def me(current_user: dict = Depends(require_role(1))) -> StudentOut:
    try:
        s = await _get_student_by_user(current_user["_id"])
        if not s:
            raise HTTPException(status_code=404, detail="当前用户未绑定学生")
        s["_id"] = str(s["_id"])
        return s
    except HTTPException as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail="当前用户未绑定学生")
        raise e
