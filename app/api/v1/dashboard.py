from fastapi import APIRouter, Depends
from app.api.deps import require_role, require_edition_for_mode

# 在路由层挂载版别运行模式依赖，保证仅允许后端设置的版别访问
router = APIRouter(dependencies=[Depends(require_edition_for_mode())])

@router.get("/summary")
async def dashboard_summary(current_user: dict = Depends(require_role(1))):
    """
    仪表盘概要接口：根据角色等级与版别返回不同的首页信息
    - 最低 1 级即可访问，但返回内容随等级与版别递增
    - 关键节点：避免多层嵌套，先取必要信息后按条件构造视图
    """
    role = current_user.get("role", "user")
    level = current_user.get("role_level", 1)
    edition = current_user.get("edition", "edu")

    # 基础公共信息（所有角色可见）
    base = {
        "welcome": f"欢迎 {current_user.get('username','')} 登录",
        "edition": edition,
        "role": role,
        "role_level": level,
    }

    # 教育版视图
    if edition == "edu":
        if level == 1:
            base.update({
                "modules": ["今日出勤", "操行与教师意见"],
            })
            return base
        if level == 2:
            base.update({
                "modules": ["班级出勤率", "课程/地点", "学生请假", "上级指示"],
            })
            return base
        if level == 3:
            base.update({
                "modules": ["系部教师出勤", "学生考勤", "课堂异常指标", "上级指示"],
            })
            return base
        if level == 4:
            base.update({
                "modules": ["校园整体安全", "教师出勤率", "资金预算", "部门进度", "本期目标"],
            })
            return base
        # 系统管理员：与业务最高权限分离
        base.update({
            "modules": ["系统运行", "告警", "运维工具"],
        })
        return base

    # 企业版视图（biz）
    if level == 1:
        base.update({
            "modules": ["今日出勤", "绩效", "上级意见"],
        })
        return base
    if level == 2:
        base.update({
            "modules": ["小组出勤率", "工单/排班", "请假审批", "负责人指示"],
        })
        return base
    if level == 3:
        base.update({
            "modules": ["部门出勤", "任务进度", "异常指标", "负责人指示"],
        })
        return base
    if level == 4:
        base.update({
            "modules": ["企业整体安全", "员工出勤率", "资金预算", "部门进度", "战略目标"],
        })
        return base
    base.update({
        "modules": ["系统运行", "告警", "运维工具"],
    })
    return base