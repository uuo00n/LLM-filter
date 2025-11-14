from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List
from bson import ObjectId
from app.api.deps import require_edition_for_mode, require_role
from app.db.mongodb import db

router = APIRouter(dependencies=[Depends(require_edition_for_mode())])

class PersonCreate(BaseModel):
    person_id: str
    name: str
    type: str = Field(pattern="^(student|teacher|staff)$")

@router.post(
    "/bulk",
    summary="批量导入人物档案",
    description="导入学生/教师/职员的基础人物信息（person_id/name/type）。",
)
async def bulk_create(persons: List[PersonCreate], current_user: dict = Depends(require_role(3))):
    docs = [{"person_id": p.person_id, "name": p.name, "type": p.type} for p in persons]
    if not docs:
        raise HTTPException(status_code=400, detail="空数据")
    await db.db.persons.insert_many(docs)
    return {"inserted": len(docs)}

@router.get(
    "",
    summary="列出人物档案",
    description="按 person_id 排序列出所有人物档案。",
)
async def list_persons(current_user: dict = Depends(require_role(3))):
    res = []
    counts = {}
    cursor = db.db.persons.find({}).sort("person_id", 1)
    async for d in cursor:
        d["_id"] = str(d["_id"])  
        res.append(d)
        t = d.get("type")
        if t:
            counts[t] = counts.get(t, 0) + 1
    return {"items": res, "counts_by_type": counts}