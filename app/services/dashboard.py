from datetime import datetime
from typing import Dict, List, Any
from bson import ObjectId
from fastapi import HTTPException
from app.db.mongodb import db

async def _today_iso() -> str:
    return datetime.now().date().isoformat()

async def _weekday() -> int:
    return datetime.now().isoweekday()

async def _current_period() -> int:
    h = datetime.now().hour
    if h < 10:
        return 1
    if h < 11:
        return 2
    if h < 12:
        return 3
    return 4
 
async def _get_primary_binding(account_id: ObjectId) -> Dict[str, Any]:
    b = await db.db.bindings.find_one({"account_id": account_id, "primary": True})
    if not b:
        raise HTTPException(status_code=404, detail="未绑定人物")
    return b
 
async def _get_student_entity(account_id: ObjectId, binding: Dict[str, Any]) -> Dict[str, Any]:
    s = await db.db.students.find_one({"person_id": binding.get("person_id")})
    if s:
        return s
    raise HTTPException(status_code=404, detail="未找到学生实体")
 
async def _get_teacher_entity(account_id: ObjectId, binding: Dict[str, Any]) -> Dict[str, Any]:
    t = await db.db.teachers.find_one({"person_id": binding.get("person_id")})
    if t:
        return t
    raise HTTPException(status_code=404, detail="未找到教师实体")

async def _get_student_by_user(user_id: ObjectId) -> Dict[str, Any]:
    b = await _get_primary_binding(user_id)
    if b.get("type") != "student":
        raise HTTPException(status_code=404, detail="当前绑定非学生")
    return await _get_student_entity(user_id, b)

async def student_today_summary(current_user: Dict[str, Any]) -> Dict[str, Any]:
    today = await _today_iso()
    weekday = await _weekday()
    student = await _get_student_by_user(current_user["_id"])
    class_id = student.get("class_id") if student else None

    schedules: List[Dict[str, Any]] = []
    if class_id:
        cursor = db.db.schedules.find({"weekday": weekday, "classes.class_id": class_id}).sort("period", 1)
        async for doc in cursor:
            loc = None
            for c in doc.get("classes", []):
                if c.get("class_id") == class_id:
                    loc = c.get("location")
                    break
            schedules.append({
                "lesson_id": doc.get("lesson_id"),
                "period": doc.get("period"),
                "course_name": doc.get("course_name"),
                "location": loc,
            })

    attendance = []
    if student:
        cursor = db.db.attendance.find({"student_id": student.get("student_id"), "date": today})
        async for a in cursor:
            attendance.append({
                "lesson_id": a.get("lesson_id"),
                "status": a.get("status"),
            })

    conduct_doc = await db.db.conduct.find_one({"student_id": student.get("student_id") if student else None, "date": today})
    conduct = {}
    if conduct_doc:
        conduct = {
            "date": conduct_doc.get("date"),
            "metrics": conduct_doc.get("metrics"),
            "teacher_comment": conduct_doc.get("teacher_comment"),
            "head_teacher_comment": conduct_doc.get("head_teacher_comment"),
            "score": conduct_doc.get("score"),
        }

    return {
        "student": {
            "student_id": student.get("student_id") if student else None,
            "name": student.get("name") if student else None,
            "class_id": class_id,
        },
        "today_schedule": schedules,
        "today_attendance": attendance,
        "today_conduct": conduct,
    }

async def homeroom_current_summary(current_user: Dict[str, Any]) -> Dict[str, Any]:
    today = await _today_iso()
    weekday = await _weekday()
    period = await _current_period()
    current_lesson_id = f"W{weekday}-P{period}"
    uid = ObjectId(current_user["_id"])
    classes = []
    cursor = db.db.classes.find({"head_teacher_person_id": uid})
    async for c in cursor:
        classes.append(c)
    class_ids = [c.get("class_id") for c in classes]

    lessons: List[Dict[str, Any]] = []
    for cid in class_ids:
        doc = await db.db.schedules.find_one({"weekday": weekday, "period": period, "classes.class_id": cid})
        if doc:
            loc = None
            for cc in doc.get("classes", []):
                if cc.get("class_id") == cid:
                    loc = cc.get("location")
                    break
            lessons.append({
                "class_id": cid,
                "course_name": doc.get("course_name"),
                "location": loc,
            })

    rates: List[Dict[str, Any]] = []
    for c in classes:
        total = c.get("students_count", 0)
        present = await db.db.attendance.count_documents({
            "class_id": c.get("class_id"),
            "date": today,
            "lesson_id": current_lesson_id,
            "status": "出勤",
        })
        rate = (present / total) if total else 0
        rates.append({"class_id": c.get("class_id"), "present": present, "total": total, "rate": rate})

    leaves: List[Dict[str, Any]] = []
    for cid in class_ids:
        cursor = db.db.leaves.find({"class_id": cid, "from_date": {"$lte": today}, "to_date": {"$gte": today}})
        async for l in cursor:
            leaves.append({
                "student_id": l.get("student_id"),
                "class_id": cid,
                "reason": l.get("reason"),
                "status": l.get("status"),
            })

    directives: List[Dict[str, Any]] = []
    cursor = db.db.directives.find({"level": "department"}).sort("created_at", -1).limit(5)
    async for d in cursor:
        directives.append({
            "content": d.get("content"),
            "created_at": d.get("created_at"),
        })

    return {
        "current_lessons": lessons,
        "attendance_rates": rates,
        "leaves": leaves,
        "directives": directives,
    }

async def department_overview(current_user: Dict[str, Any]) -> Dict[str, Any]:
    today = await _today_iso()
    weekday = await _weekday()
    total_students = await db.db.students.count_documents({})
    present_today = await db.db.attendance.count_documents({"date": today, "status": "出勤"})
    absent_or_leave_today = await db.db.attendance.count_documents({"date": today, "status": {"$in": ["缺勤", "请假"]}})

    anomalies: List[Dict[str, Any]] = []
    cursor_classes = db.db.classes.find({})
    async for c in cursor_classes:
        cid = c.get("class_id")
        total = c.get("students_count", 0)
        abnormal = await db.db.attendance.count_documents({
            "class_id": cid,
            "date": today,
            "status": {"$in": ["缺勤", "请假"]}
        })
        rate = (abnormal / total) if total else 0
        if rate > 0.3:
            anomalies.append({"class_id": cid, "anomaly_rate": rate})

    teacher_stats: Dict[str, Dict[str, int]] = {}
    cursor_sched = db.db.schedules.find({"weekday": weekday})
    async for s in cursor_sched:
        tid = s.get("teacher_id")
        if not tid:
            continue
        key = str(tid)
        st = teacher_stats.get(key)
        if not st:
            st = {"present_slots": 0, "total_slots": 0}
            teacher_stats[key] = st
        st["total_slots"] += 1

        ratios: List[float] = []
        for cc in s.get("classes", []):
            cid = cc.get("class_id")
            cls = await db.db.classes.find_one({"class_id": cid})
            total = cls.get("students_count", 0) if cls else 0
            present = await db.db.attendance.count_documents({
                "class_id": cid,
                "date": today,
                "lesson_id": s.get("lesson_id"),
                "status": "出勤",
            })
            ratios.append((present / total) if total else 0)
        avg_ratio = (sum(ratios) / len(ratios)) if ratios else 0
        if avg_ratio >= 0.7:
            st["present_slots"] += 1

    teacher_attendance_rates: List[Dict[str, Any]] = []
    for key, st in teacher_stats.items():
        total_slots = st.get("total_slots", 0)
        present_slots = st.get("present_slots", 0)
        rate = (present_slots / total_slots) if total_slots else 0
        teacher_attendance_rates.append({
            "teacher_id": key,
            "present_slots": present_slots,
            "total_slots": total_slots,
            "rate": rate,
        })

    directives: List[Dict[str, Any]] = []
    cursor_dir = db.db.directives.find({"level": {"$in": ["department", "campus"]}}).sort("created_at", -1).limit(5)
    async for d in cursor_dir:
        directives.append({
            "level": d.get("level"),
            "content": d.get("content"),
            "created_at": d.get("created_at"),
        })

    return {
        "students_attendance": {
            "total": total_students,
            "present": present_today,
            "absent_or_leave": absent_or_leave_today,
        },
        "teacher_attendance_rates": teacher_attendance_rates,
        "anomalies": anomalies,
        "directives": directives,
    }

async def campus_overview(current_user: Dict[str, Any]) -> Dict[str, Any]:
    today = await _today_iso()
    total_students = await db.db.students.count_documents({})
    present = await db.db.attendance.count_documents({"date": today, "status": "出勤"})
    leaves = await db.db.leaves.count_documents({"from_date": {"$lte": today}, "to_date": {"$gte": today}})
    directives_count = await db.db.directives.count_documents({})
    return {
        "total_students": total_students,
        "present": present,
        "leaves": leaves,
        "directives": directives_count,
        "term_goals": [],
        "department_progress": [],
    }