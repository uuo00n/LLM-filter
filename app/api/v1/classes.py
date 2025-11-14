from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from app.api.deps import require_edition_for_mode, require_role
from app.db.mongodb import db

router = APIRouter(dependencies=[Depends(require_edition_for_mode())])

class HeadTeacherPayload(BaseModel):
    head_teacher_person_id: str

@router.put("/{class_id}/head-teacher")
async def set_head_teacher(class_id: str, payload: HeadTeacherPayload, current_user: dict = Depends(require_role(3))):
    res = await db.db.classes.update_one({"class_id": class_id}, {"$set": {"head_teacher_person_id": ObjectId(payload.head_teacher_person_id)}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="班级不存在")
    return {"success": True}

@router.get("")
async def list_classes(current_user: dict = Depends(require_role(2))):
    res = []
    cursor = db.db.classes.find({}).sort("class_id", 1)
    async for d in cursor:
        d["_id"] = str(d["_id"]) if d.get("_id") else None
        if d.get("head_teacher_person_id"):
            d["head_teacher_person_id"] = str(d["head_teacher_person_id"])  
        res.append(d)
    return res