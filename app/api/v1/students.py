from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.api.deps import require_edition_for_mode, require_role
from app.services.student_binding import bind_user_to_student, unbind_user_from_student, get_student_by_user

router = APIRouter(dependencies=[Depends(require_edition_for_mode())])

class BindPayload(BaseModel):
    user_id: str

@router.post("/{student_id}/bind")
async def bind(student_id: str, payload: BindPayload, current_user: dict = Depends(require_role(2))):
    ok = await bind_user_to_student(payload.user_id, student_id)
    if not ok:
        raise HTTPException(status_code=400, detail="用户已绑定其他学生或学生不存在")
    return {"success": True}

@router.delete("/{student_id}/bind")
async def unbind(student_id: str, current_user: dict = Depends(require_role(2))):
    ok = await unbind_user_from_student(student_id)
    if not ok:
        raise HTTPException(status_code=404, detail="学生不存在或未绑定")
    return {"success": True}

@router.get("/me")
async def me(current_user: dict = Depends(require_role(1))):
    s = await get_student_by_user(str(current_user["_id"]))
    if not s:
        raise HTTPException(status_code=404, detail="当前用户未绑定学生")
    s["_id"] = str(s["_id"])  # 简化返回
    return s