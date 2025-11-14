from bson import ObjectId
from app.db.mongodb import db

async def bind_user_to_student(user_id: str, student_id: str) -> bool:
    uid = ObjectId(user_id)
    exists = await db.db.students.find_one({"user_id": uid})
    if exists:
        return False
    res = await db.db.students.update_one({"student_id": student_id}, {"$set": {"user_id": uid}})
    return res.modified_count == 1

async def unbind_user_from_student(student_id: str) -> bool:
    res = await db.db.students.update_one({"student_id": student_id}, {"$unset": {"user_id": ""}})
    return res.modified_count == 1

async def get_student_by_user(user_id: str):
    return await db.db.students.find_one({"user_id": ObjectId(user_id)})