from fastapi import APIRouter, Depends
from app.api.deps import require_edition_for_mode, require_role
from app.services.dashboard import (
    student_today_summary,
    homeroom_current_summary,
    department_overview,
    campus_overview,
)

router = APIRouter(dependencies=[Depends(require_edition_for_mode())])

@router.get("/student/today")
async def student_today(current_user: dict = Depends(require_role(1))):
    return await student_today_summary(current_user)

@router.get("/homeroom/current")
async def homeroom_current(current_user: dict = Depends(require_role(2))):
    return await homeroom_current_summary(current_user)

@router.get("/department/overview")
async def department(current_user: dict = Depends(require_role(3))):
    return await department_overview(current_user)

@router.get("/campus/overview")
async def campus(current_user: dict = Depends(require_role(5))):
    return await campus_overview(current_user)