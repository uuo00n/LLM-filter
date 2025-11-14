from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from app.api.deps import require_edition_for_mode, require_role
from app.db.mongodb import db

router = APIRouter(dependencies=[Depends(require_edition_for_mode())])

class AssignTeacherPayload(BaseModel):
    lesson_id: str
    teacher_person_id: str

@router.put(
    "/assign-teacher",
    summary="为节次设置任课教师人物",
    description="将指定 lesson_id 的节次设置为 teacher_person_id（教师人物）。",
)
async def assign_teacher(payload: AssignTeacherPayload, current_user: dict = Depends(require_role(3))):
    res = await db.db.schedules.update_one({"lesson_id": payload.lesson_id}, {"$set": {"teacher_person_id": ObjectId(payload.teacher_person_id)}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="节次不存在")
    return {"success": True}

@router.get(
    "",
    summary="列出课表节次",
    description="按工作日与节次排序列出共享节次（含各班 location 与 teacher_person_id）。",
)
async def list_schedules(current_user: dict = Depends(require_role(2))):
    res = []
    cursor = db.db.schedules.find({}).sort([("weekday", 1), ("period", 1)])
    async for d in cursor:
        if d.get("teacher_person_id"):
            d["teacher_person_id"] = str(d["teacher_person_id"])  
        res.append({
            "lesson_id": d.get("lesson_id"),
            "weekday": d.get("weekday"),
            "period": d.get("period"),
            "course_name": d.get("course_name"),
            "teacher_person_id": d.get("teacher_person_id"),
            "classes": d.get("classes", []),
        })
    return res