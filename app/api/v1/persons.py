from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Dict
from bson import ObjectId
from app.api.deps import require_edition_for_mode, require_role
from app.db.mongodb import db

router = APIRouter(dependencies=[Depends(require_edition_for_mode())])

class PersonCreate(BaseModel):
    person_id: str
    name: str
    type: str = Field(pattern="^(student|teacher|staff)$")

class BulkInsertResult(BaseModel):
    inserted: int

class PersonOut(BaseModel):
    _id: str
    person_id: str
    name: str
    type: str

class PersonsListResponse(BaseModel):
    items: List[PersonOut]
    counts_by_type: Dict[str, int]

@router.post(
    "/bulk",
    summary="批量导入人物档案",
    description="导入学生/教师/职员的基础人物信息（person_id/name/type）。",
    response_model=BulkInsertResult,
    responses={
        400: {"description": "空数据", "content": {"application/json": {"example": {"detail": "空数据"}}}},
        401: {"description": "认证失败", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
        403: {"description": "权限不足", "content": {"application/json": {"example": {"detail": "权限不足"}}}},
    },
)
async def bulk_create(persons: List[PersonCreate] = Body(..., description="人物档案列表"), current_user: dict = Depends(require_role(3))) -> BulkInsertResult:
    docs = [{"person_id": p.person_id, "name": p.name, "type": p.type} for p in persons]
    if not docs:
        raise HTTPException(status_code=400, detail="空数据")
    await db.db.persons.insert_many(docs)
    return {"inserted": len(docs)}

@router.get(
    "",
    summary="列出人物档案",
    description="按 person_id 排序列出所有人物档案。",
    response_model=PersonsListResponse,
)
async def list_persons(current_user: dict = Depends(require_role(3))) -> PersonsListResponse:
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
