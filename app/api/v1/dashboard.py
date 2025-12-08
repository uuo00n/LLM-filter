from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.api.deps import require_edition_for_mode, require_role, require_binding
from app.services.dashboard import (
    student_today_summary,
    homeroom_current_summary,
    department_overview,
    campus_overview,
)

router = APIRouter(dependencies=[Depends(require_edition_for_mode())])

class StudentTodaySchedule(BaseModel):
    lesson_id: Optional[str]
    period: Optional[int]
    course_name: Optional[str]
    location: Optional[str]

class StudentTodayAttendance(BaseModel):
    lesson_id: Optional[str]
    status: Optional[str]

class StudentTodayConduct(BaseModel):
    date: Optional[str]
    metrics: Optional[Dict[str, Any]]
    teacher_comment: Optional[str]
    head_teacher_comment: Optional[str]
    score: Optional[float]

class StudentTodaySummary(BaseModel):
    student: Dict[str, Optional[str]]
    today_schedule: List[StudentTodaySchedule]
    today_attendance: List[StudentTodayAttendance]
    today_conduct: Dict[str, Any]

class HomeroomLesson(BaseModel):
    class_id: Optional[str]
    course_name: Optional[str]
    location: Optional[str]

class HomeroomRate(BaseModel):
    class_id: Optional[str]
    present: int
    total: int
    rate: float

class HomeroomLeave(BaseModel):
    student_id: Optional[str]
    class_id: Optional[str]
    reason: Optional[str]
    status: Optional[str]

class DirectiveItem(BaseModel):
    content: Optional[str]
    created_at: Optional[str]

class HomeroomCurrentSummary(BaseModel):
    current_lessons: List[HomeroomLesson]
    attendance_rates: List[HomeroomRate]
    leaves: List[HomeroomLeave]
    directives: List[DirectiveItem]

class DepartmentTeacherRate(BaseModel):
    teacher_id: Optional[str]
    present_slots: int
    total_slots: int
    rate: float

class DepartmentStudentsAttendance(BaseModel):
    total: int
    present: int
    absent_or_leave: int

class DepartmentOverview(BaseModel):
    students_attendance: DepartmentStudentsAttendance
    teacher_attendance_rates: List[DepartmentTeacherRate]
    anomalies: List[Dict[str, Any]]
    directives: List[Dict[str, Any]]

class CampusOverview(BaseModel):
    total_students: int
    present: int
    leaves: int
    directives: int
    term_goals: List[Dict[str, Any]]
    department_progress: List[Dict[str, Any]]
@router.get(
    "/student/today",
    summary="学生端：今日个人课表、出勤与操行",
    description="需角色等级≥1且主绑定为学生；返回当天课表（共享节次按班级定位教室）、今日出勤记录与操行评语。"
    , response_model=StudentTodaySummary,
    responses={
        401: {"description": "未认证", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
        403: {"description": "权限不足或未绑定学生", "content": {"application/json": {"example": {"detail": "实体绑定不存在或类型不匹配"}}}},
    }
)
async def student_today(current_user: dict = Depends(require_role(1)), _b: dict = Depends(require_binding("student"))) -> StudentTodaySummary:
    return await student_today_summary(current_user)

@router.get(
    "/homeroom/current",
    summary="班主任端：当前节次课程与地点、出勤率、请假、指示",
    description="需角色等级≥2且主绑定为教师；按 head_teacher_person_id 定位所辖班，统计当前节次的课程与地点、节次出勤率、今日请假与部门指示。"
    , response_model=HomeroomCurrentSummary,
    responses={
        401: {"description": "未认证", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
        403: {"description": "权限不足或未绑定教师", "content": {"application/json": {"example": {"detail": "实体绑定不存在或类型不匹配"}}}},
    }
)
async def homeroom_current(current_user: dict = Depends(require_role(2)), _b: dict = Depends(require_binding("teacher"))) -> HomeroomCurrentSummary:
    return await homeroom_current_summary(current_user)

@router.get(
    "/department/overview",
    summary="中层端：教师节次出勤率、学生出勤、异常班级、指示",
    description="需角色等级≥3；按今日工作日统计每位教师的节次出勤率、全校学生出勤聚合、异常班级（缺勤+请假占比>0.3）与近期部门/校园指示。"
    , response_model=DepartmentOverview,
    responses={
        401: {"description": "未认证", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
        403: {"description": "权限不足", "content": {"application/json": {"example": {"detail": "权限不足"}}}},
    }
)
async def department(current_user: dict = Depends(require_role(3))) -> DepartmentOverview:
    return await department_overview(current_user)

@router.get(
    "/campus/overview",
    summary="校级端：校园整体总览",
    description="需角色等级≥4；返回学生总数、今日出勤、请假与指示数量等宏观数据。"
    , response_model=CampusOverview,
    responses={
        401: {"description": "未认证", "content": {"application/json": {"example": {"detail": "无效的认证凭据"}}}},
        403: {"description": "权限不足", "content": {"application/json": {"example": {"detail": "权限不足"}}}},
    }
)
async def campus(current_user: dict = Depends(require_role(4))) -> CampusOverview:
    return await campus_overview(current_user)
