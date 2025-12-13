from datetime import datetime, timedelta
from typing import Dict, List, Any
from bson import ObjectId
from fastapi import HTTPException
from app.db.mongodb import db
from app.core.config import settings

async def _today_iso() -> str:
    return datetime.now().date().isoformat()

async def _weekday() -> int:
    return datetime.now().isoweekday()

async def _get_current_week() -> int:
    try:
        start_date = datetime.strptime(settings.TERM_START_DATE, "%Y-%m-%d").date()
        today = datetime.now().date()
        delta = today - start_date
        if delta.days < 0:
            return 1
        return (delta.days // 7) + 1
    except Exception:
        return 1

def _is_week_valid(week: int, week_range: str) -> bool:
    if not week_range:
        return True
    try:
        parts = week_range.split(',')
        for part in parts:
            if '-' in part:
                start, end = map(int, part.split('-'))
                if start <= week <= end:
                    return True
            else:
                if int(part) == week:
                    return True
    except:
        pass
    return False

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
    pid = binding.get("person_id")
    if isinstance(pid, str) and ObjectId.is_valid(pid):
        pid = ObjectId(pid)
        
    s = await db.db.students.find_one({"person_id": pid})
    if s:
        return s
    raise HTTPException(status_code=404, detail="未找到学生实体")
 
async def _get_teacher_entity(account_id: ObjectId, binding: Dict[str, Any]) -> Dict[str, Any]:
    pid = binding.get("person_id")
    if isinstance(pid, str) and ObjectId.is_valid(pid):
        pid = ObjectId(pid)

    t = await db.db.teachers.find_one({"person_id": pid})
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

async def student_week_schedule(current_user: Dict[str, Any], week: int = None) -> Dict[str, Any]:
    if week is None:
        week = await _get_current_week()
    
    student = await _get_student_by_user(current_user["_id"])
    class_id = student.get("class_id") if student else None
    
    try:
        start_date = datetime.strptime(settings.TERM_START_DATE, "%Y-%m-%d").date()
        monday_of_week = start_date + timedelta(weeks=week-1)
    except:
        monday_of_week = datetime.now().date()
    
    week_dates = {}
    for i in range(1, 8):
        d = monday_of_week + timedelta(days=i-1)
        week_dates[i] = d.isoformat()

    schedules_by_day = {str(i): [] for i in range(1, 8)}
    
    if class_id:
        cursor = db.db.schedules.find({"classes.class_id": class_id}).sort("period", 1)
        async for doc in cursor:
            w_range = doc.get("week_range", "")
            if not _is_week_valid(week, w_range):
                continue
                
            wd = doc.get("weekday")
            loc = None
            for c in doc.get("classes", []):
                if c.get("class_id") == class_id:
                    loc = c.get("location")
                    break
            
            item = {
                "lesson_id": doc.get("lesson_id"),
                "period": doc.get("period"),
                "course_name": doc.get("course_name"),
                "location": loc,
                "start_time": doc.get("start_time"),
                "end_time": doc.get("end_time"),
                "teacher_person_id": str(doc.get("teacher_person_id")) if doc.get("teacher_person_id") else None
            }
            if str(wd) in schedules_by_day:
                schedules_by_day[str(wd)].append(item)

    return {
        "student": {
            "student_id": student.get("student_id") if student else None,
            "name": student.get("name") if student else None,
            "class_id": class_id,
        },
        "current_week": week,
        "week_dates": week_dates,
        "schedule": schedules_by_day
    }

async def teacher_week_schedule(current_user: Dict[str, Any], week: int = None) -> Dict[str, Any]:
    if week is None:
        week = await _get_current_week()
        
    binding = await _get_primary_binding(current_user["_id"])
    if binding.get("type") != "teacher":
        raise HTTPException(status_code=403, detail="当前绑定非教师")
        
    teacher = await _get_teacher_entity(current_user["_id"], binding)
    teacher_person_id = teacher.get("person_id")
    
    # 确保类型匹配
    if isinstance(teacher_person_id, str) and ObjectId.is_valid(teacher_person_id):
        teacher_person_id = ObjectId(teacher_person_id)

    try:
        start_date = datetime.strptime(settings.TERM_START_DATE, "%Y-%m-%d").date()
        monday_of_week = start_date + timedelta(weeks=week-1)
    except:
        monday_of_week = datetime.now().date()
        
    week_dates = {}
    for i in range(1, 8):
        d = monday_of_week + timedelta(days=i-1)
        week_dates[i] = d.isoformat()
        
    schedules_by_day = {str(i): [] for i in range(1, 8)}
    
    # 查询该教师的所有课程
    # 注意：teacher_person_id 在 schedules 中可能是 ObjectId 也可能是字符串，视具体数据而定
    # 为稳妥起见，如果 teacher_person_id 是 ObjectId，也可以尝试转字符串匹配，或者由数据库层面保证一致性
    # 这里我们使用 $in 查询来兼容
    query_ids = [teacher_person_id]
    if isinstance(teacher_person_id, ObjectId):
        query_ids.append(str(teacher_person_id))
    
    cursor = db.db.schedules.find({"teacher_person_id": {"$in": query_ids}}).sort("period", 1)
    
    async for doc in cursor:
        w_range = doc.get("week_range", "")
        if not _is_week_valid(week, w_range):
            continue
            
        wd = doc.get("weekday")
        
        # 提取班级和地点信息
        classes_info = []
        for c in doc.get("classes", []):
            classes_info.append({
                "class_id": c.get("class_id"),
                "location": c.get("location")
            })
            
        item = {
            "lesson_id": doc.get("lesson_id"),
            "period": doc.get("period"),
            "course_name": doc.get("course_name"),
            "classes": classes_info,
            "start_time": doc.get("start_time"),
            "end_time": doc.get("end_time")
        }
        
        if str(wd) in schedules_by_day:
            schedules_by_day[str(wd)].append(item)
            
    return {
        "teacher": {
            "teacher_id": teacher.get("teacher_id"),
            "name": teacher.get("name"), # 注意：teacher表可能没有name，通常在person表
            "person_id": str(teacher.get("person_id"))
        },
        "current_week": week,
        "week_dates": week_dates,
        "schedule": schedules_by_day
    }

async def homeroom_current_summary(current_user: Dict[str, Any]) -> Dict[str, Any]:
    today = await _today_iso()
    weekday = await _weekday()
    period = await _current_period()
    current_lesson_id = f"W{weekday}-P{period}"
    
    # 获取当前用户的教师绑定信息
    binding = await _get_primary_binding(current_user["_id"])
    if binding.get("type") != "teacher":
        raise HTTPException(status_code=403, detail="当前绑定非教师")
        
    teacher = await _get_teacher_entity(current_user["_id"], binding)
    teacher_person_id = teacher.get("person_id")
    
    if isinstance(teacher_person_id, str) and ObjectId.is_valid(teacher_person_id):
        teacher_person_id = ObjectId(teacher_person_id)
        
    classes = []
    # 使用 person_id 查询班级
    cursor = db.db.classes.find({"head_teacher_person_id": teacher_person_id})
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
            "created_at": d.get("created_at").isoformat() if isinstance(d.get("created_at"), datetime) else d.get("created_at"),
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