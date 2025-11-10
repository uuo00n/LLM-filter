"""
角色与权限等级的统一定义

设计说明：
- 为避免“神秘命名”和“重复代码”，将角色等级映射集中在一个模块维护。
- 同时兼容历史中的 "admin" 命名，映射为最高等级（5）。
"""

# 角色等级映射，数字越大权限越高
ROLE_ORDER = {
    "user": 1,          # 学生/员工
    "manager": 2,       # 班主任/组长/二级部门管理员
    "leader": 3,        # 中层干部/部门负责人/一级部门管理员
    "master": 4,        # 校长/集团高管/总负责人（业务最高）
    "administrator": 5, # 系统管理员/运维超管（系统最高）
    "admin": 5,         # 历史兼容：旧代码中的 admin
}

# 合法版别（教育/企业）
VALID_EDITIONS = {"edu", "biz"}

def get_role_level(role: str) -> int:
    """根据角色字符串返回对应的权限等级，默认返回 1 级。
    关键点：提前返回，避免多层嵌套。
    """
    return ROLE_ORDER.get((role or "user").lower(), 1)