from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId
from app.api.deps import require_edition_for_mode, require_role
from app.db.mongodb import db

router = APIRouter(dependencies=[Depends(require_edition_for_mode())])

class TeacherCreate(BaseModel):
    person_id: str
    teacher_id: str
    department: str
    roles: List[str]
    account_id: Optional[str] = None

@router.post(
    "/bulk",
    summary="批量导入教师实体",
    description="导入教师实体（person_id/teacher_id/department/roles），可选绑定 account_id。",
)
async def bulk_create(teachers: List[TeacherCreate], current_user: dict = Depends(require_role(3))):
    docs = []
    for t in teachers:
        doc = {
            "person_id": ObjectId(t.person_id),
            "teacher_id": t.teacher_id,
            "department": t.department,
            "roles": t.roles,
        }
        if t.account_id:
            doc["account_id"] = ObjectId(t.account_id)
        docs.append(doc)
    if not docs:
        raise HTTPException(status_code=400, detail="空数据")
    await db.db.teachers.insert_many(docs)
    return {"inserted": len(docs)}

@router.get(
    "",
    summary="列出教师实体",
    description="按 teacher_id 排序列出所有教师实体（包含 person_id/account_id）。",
)
async def list_teachers(current_user: dict = Depends(require_role(3))):
    res = []
    cursor = db.db.teachers.find({}).sort("teacher_id", 1)
    async for d in cursor:
        d["_id"] = str(d["_id"])  
        d["person_id"] = str(d["person_id"])  
        if d.get("account_id"):
            d["account_id"] = str(d["account_id"])  
        res.append(d)
    return res