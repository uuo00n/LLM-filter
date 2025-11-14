from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.api.deps import require_edition_for_mode, get_current_active_user, require_role
from app.services.bindings import create_binding, delete_binding, get_binding_by_account

router = APIRouter(dependencies=[Depends(require_edition_for_mode())])

class BindingPayload(BaseModel):
    person_id: str
    type: str
    primary: bool = True

@router.post("")
async def bind(payload: BindingPayload, current_user: dict = Depends(require_role(2))):
    ok = await create_binding(str(current_user["_id"]), payload.person_id, payload.type, payload.primary)
    if not ok:
        raise HTTPException(status_code=400, detail="主绑定已存在或参数错误")
    return {"success": True}

@router.delete("/{person_id}")
async def unbind(person_id: str, current_user: dict = Depends(require_role(2))):
    ok = await delete_binding(str(current_user["_id"]), person_id)
    if not ok:
        raise HTTPException(status_code=404, detail="未找到绑定")
    return {"success": True}

@router.get("/me")
async def me(current_user: dict = Depends(get_current_active_user)):
    b = await get_binding_by_account(str(current_user["_id"]))
    if not b:
        raise HTTPException(status_code=404, detail="未绑定人物")
    b["account_id"] = str(b["account_id"])  
    b["person_id"] = str(b["person_id"])  
    return b