from typing import Optional, Dict
from bson import ObjectId
from app.db.mongodb import db

async def create_binding(account_id: str, person_id: str, type_: str, primary: bool = True) -> bool:
    aid = ObjectId(account_id)
    pid = ObjectId(person_id)
    if primary:
        existing = await db.db.bindings.find_one({"account_id": aid, "type": type_, "primary": True})
        if existing:
            return False
    res = await db.db.bindings.insert_one({"account_id": aid, "person_id": pid, "type": type_, "primary": primary})
    return bool(res.inserted_id)

async def delete_binding(account_id: str, person_id: str) -> bool:
    aid = ObjectId(account_id)
    pid = ObjectId(person_id)
    res = await db.db.bindings.delete_one({"account_id": aid, "person_id": pid})
    return res.deleted_count == 1

async def get_binding_by_account(account_id: str) -> Optional[Dict]:
    aid = ObjectId(account_id)
    return await db.db.bindings.find_one({"account_id": aid, "primary": True})