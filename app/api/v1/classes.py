from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId
from app.api.deps import require_edition_for_mode, require_role
from app.db.mongodb import db

router = APIRouter(dependencies=[Depends(require_edition_for_mode())])

class HeadTeacherPayload(BaseModel):
    head_teacher_person_id: str

class ActionResult(BaseModel):
    success: bool

class ClassOut(BaseModel):
    _id: Optional[str] = None
    class_id: str
    head_teacher_person_id: Optional[str] = None
    students_count: Optional[int] = 0

@router.put(
    "/{class_id}/head-teacher",
    summary="设置班主任人物",
    description="为班级设置 head_teacher_person_id（指向教师人物）。",
    response_model=ActionResult,
)
async def set_head_teacher(class_id: str, payload: HeadTeacherPayload, current_user: dict = Depends(require_role(3))) -> ActionResult:
    res = await db.db.classes.update_one({"class_id": class_id}, {"$set": {"head_teacher_person_id": ObjectId(payload.head_teacher_person_id)}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="班级不存在")
    return {"success": True}

@router.get(
    "",
    summary="列出班级",
    description="按 class_id 排序列出班级信息（含 head_teacher_person_id）。",
    response_model=List[ClassOut],
)
async def list_classes(current_user: dict = Depends(require_role(2))) -> List[ClassOut]:
    res = []
    cursor = db.db.classes.find({}).sort("class_id", 1)
    async for d in cursor:
        d["_id"] = str(d["_id"]) if d.get("_id") else None
        if d.get("head_teacher_person_id"):
            d["head_teacher_person_id"] = str(d["head_teacher_person_id"])  
        res.append(d)
    return res