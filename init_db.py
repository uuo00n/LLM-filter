import asyncio
import motor.motor_asyncio
import os
from dotenv import load_dotenv
from datetime import datetime
from bson import ObjectId
from passlib.context import CryptContext

# 密码加密工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 加载 .env 环境变量，保持与后端一致的配置来源
load_dotenv()

# MongoDB连接配置
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "llm_filter_db")
# 运行模式：仅运行教育版或企业版之一（不混合）
APP_MODE = (os.getenv("APP_MODE", "edu") or "edu").lower()
ADMIN_EDU_PASSWORD = os.getenv("ADMIN_EDU_PASSWORD", "admin123")
USER_EDU_PASSWORD = os.getenv("USER_EDU_PASSWORD", "user123")
ADMIN_BIZ_PASSWORD = os.getenv("ADMIN_BIZ_PASSWORD", "adminbiz123")
USER_BIZ_PASSWORD = os.getenv("USER_BIZ_PASSWORD", "userbiz123")
MANAGER_EDU_PASSWORD = os.getenv("MANAGER_EDU_PASSWORD", "manager123")
LEADER_EDU_PASSWORD = os.getenv("LEADER_EDU_PASSWORD", "leader123")
MASTER_EDU_PASSWORD = os.getenv("MASTER_EDU_PASSWORD", "master123")
MANAGER_BIZ_PASSWORD = os.getenv("MANAGER_BIZ_PASSWORD", "managerbiz123")
LEADER_BIZ_PASSWORD = os.getenv("LEADER_BIZ_PASSWORD", "leaderbiz123")
MASTER_BIZ_PASSWORD = os.getenv("MASTER_BIZ_PASSWORD", "masterbiz123")

async def init_db():
    # 连接到MongoDB
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    # 清空现有集合（如果存在）
    collections = await db.list_collection_names()
    for collection in collections:
        await db[collection].drop()
    
    print("已清空现有集合")
    
    # 创建用户集合并添加假数据
    admin_id = ObjectId()       # 教育版管理员（用户名 admin）
    user_id = ObjectId()        # 教育版普通用户（用户名 user）
    user_biz_id = ObjectId()    # 企业版普通用户（用户名 user_biz）
    
    users = [
        # 系统管理员（标准：administrator，兼容：admin 用户名）
        {
            "_id": admin_id,
            "username": "admin",
            "email": "admin@example.com",
            "hashed_password": pwd_context.hash(ADMIN_EDU_PASSWORD),
            "role": "administrator",   # 统一使用标准角色名，兼容旧数据中的 "admin"
            "role_level": 5,            # 映射到最高等级
            "edition": "edu",          # 默认教育版
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        # 普通用户（教育版）
        {
            "_id": user_id,
            "username": "user",
            "email": "user@example.com",
            "hashed_password": pwd_context.hash(USER_EDU_PASSWORD),
            "role": "user",
            "role_level": 1,
            "edition": "edu",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        # 教育版：班主任、部门负责人、中层与校长
        {
            "_id": ObjectId(),
            "username": "manager_edu",
            "email": "manager_edu@example.com",
            "hashed_password": pwd_context.hash(MANAGER_EDU_PASSWORD),
            "role": "manager",
            "role_level": 2,
            "edition": "edu",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "_id": ObjectId(),
            "username": "leader_edu",
            "email": "leader_edu@example.com",
            "hashed_password": pwd_context.hash(LEADER_EDU_PASSWORD),
            "role": "leader",
            "role_level": 3,
            "edition": "edu",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "_id": ObjectId(),
            "username": "master_edu",
            "email": "master_edu@example.com",
            "hashed_password": pwd_context.hash(MASTER_EDU_PASSWORD),
            "role": "master",
            "role_level": 4,
            "edition": "edu",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        # 企业版：员工、组长、负责人、高管与管理员
        {
            "_id": user_biz_id,
            "username": "user_biz",
            "email": "user_biz@example.com",
            "hashed_password": pwd_context.hash(USER_BIZ_PASSWORD),
            "role": "user",
            "role_level": 1,
            "edition": "biz",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "_id": ObjectId(),
            "username": "manager_biz",
            "email": "manager_biz@example.com",
            "hashed_password": pwd_context.hash(MANAGER_BIZ_PASSWORD),
            "role": "manager",
            "role_level": 2,
            "edition": "biz",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "_id": ObjectId(),
            "username": "leader_biz",
            "email": "leader_biz@example.com",
            "hashed_password": pwd_context.hash(LEADER_BIZ_PASSWORD),
            "role": "leader",
            "role_level": 3,
            "edition": "biz",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "_id": ObjectId(),
            "username": "master_biz",
            "email": "master_biz@example.com",
            "hashed_password": pwd_context.hash(MASTER_BIZ_PASSWORD),
            "role": "master",
            "role_level": 4,
            "edition": "biz",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "_id": ObjectId(),
            "username": "administrator_biz",
            "email": "administrator_biz@example.com",
            "hashed_password": pwd_context.hash(ADMIN_BIZ_PASSWORD),
            "role": "administrator",
            "role_level": 5,
            "edition": "biz",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
    ]
    
    # 根据运行模式筛选用户（不混合）
    mode = APP_MODE if APP_MODE in {"edu", "biz"} else "edu"
    if mode != APP_MODE:
        print(f"警告：APP_MODE={APP_MODE} 非法，默认使用 edu")

    selected_users = [u for u in users if u["edition"] == mode]
    await db.users.insert_many(selected_users)
    print(f"已创建用户集合并添加 {len(selected_users)} 条记录（模式：{mode}）")
    
    # 创建敏感词集合并添加假数据
    sensitive_words = [
        {
            "word": "赌博",
            "category": "违法活动",
            "subcategory": "赌博",
            "severity": 3,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "色情",
            "category": "色情内容",
            "subcategory": "色情服务",
            "severity": 4,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "毒品",
            "category": "毒品相关",
            "subcategory": "毒品名称",
            "severity": 5,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "诈骗",
            "category": "诈骗相关",
            "subcategory": "网络诈骗",
            "severity": 4,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "暴力",
            "category": "暴力内容",
            "subcategory": "语言暴力",
            "severity": 3,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "自杀",
            "category": "不良内容",
            "subcategory": "自杀",
            "severity": 5,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "政治敏感",
            "category": "政治内容",
            "subcategory": "敏感事件",
            "severity": 4,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "种族歧视",
            "category": "歧视言论",
            "subcategory": "种族歧视",
            "severity": 4,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "性别歧视",
            "category": "歧视言论",
            "subcategory": "性别歧视",
            "severity": 3,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "word": "恐怖主义",
            "category": "暴力内容",
            "subcategory": "恐怖主义",
            "severity": 5,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    await db.sensitive_words.insert_many(sensitive_words)
    print(f"已创建敏感词集合并添加 {len(sensitive_words)} 条记录")
    
    # 创建对话集合并添加假数据
    conversation_id = ObjectId()
    # 根据模式选择示例用户用于演示对话与敏感词记录
    sample_user_id = user_id if mode == "edu" else user_biz_id

    conversations = [
        {
            "_id": conversation_id,
            "user_id": sample_user_id,
            "messages": [
                {
                    "role": "user",
                    "content": "你好，请问你是谁？",
                    "timestamp": datetime.now(),
                    "contains_sensitive_words": False,
                    "sensitive_words_found": []
                },
                {
                    "role": "assistant",
                    "content": "你好！我是一个AI助手，可以回答你的问题和提供帮助。有什么我可以帮你的吗？",
                    "timestamp": datetime.now(),
                    "contains_sensitive_words": False,
                    "sensitive_words_found": []
                }
            ],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    await db.conversations.insert_many(conversations)
    print(f"已创建对话集合并添加 {len(conversations)} 条记录")
    
    # 创建敏感词记录集合并添加假数据
    sensitive_records = [
        {
            # 使用真实的 ObjectId，避免与模型类型不一致
            "user_id": sample_user_id,
            "conversation_id": conversation_id,
            "message_content": "我想了解一下赌博的事情",
            "sensitive_words_found": [
                {
                    "word": "赌博",
                    "category": "违法活动",
                    "subcategory": "赌博",
                    "severity": 3
                }
            ],
            "highest_severity": 3,
            "timestamp": datetime.now()
        },
        {
            # 第二条记录同样引用真实的 ObjectId
            "user_id": sample_user_id,
            "conversation_id": conversation_id,
            "message_content": "如何获取毒品和色情内容",
            "sensitive_words_found": [
                {
                    "word": "毒品",
                    "category": "毒品相关",
                    "subcategory": "毒品名称",
                    "severity": 5
                },
                {
                    "word": "色情",
                    "category": "色情内容",
                    "subcategory": "色情服务",
                    "severity": 4
                }
            ],
            "highest_severity": 5,
            "timestamp": datetime.now()
        }
    ]
    
    await db.sensitive_records.insert_many(sensitive_records)
    print(f"已创建敏感词记录集合并添加 {len(sensitive_records)} 条记录")
    
    # 学校业务数据：学生/班级/课表/考勤/操行/请假/指示
    await seed_school_data(db, mode)
    
    print("\n数据库初始化完成！")
    print("\n测试账号 (模式: %s):" % mode)
    if mode == "edu":
        print("教育版管理员: admin / admin123  (role=administrator, edition=edu)")
        print("教育版普通用户: user / user123  (role=user, edition=edu)")
    else:
        print("企业版管理员: administrator_biz / adminbiz123  (role=administrator, edition=biz)")
        print("企业版普通用户: user_biz / userbiz123  (role=user, edition=biz)")

async def seed_school_data(db, mode: str):
    if mode != "edu":
        print("当前为企业版模式，跳过学校业务数据初始化")
        return

    # 索引
    await db.students.create_index("student_id", unique=True)
    await db.students.create_index("class_id")
    await db.students.create_index("user_id", unique=True, sparse=True)
    await db.classes.create_index("class_id", unique=True)
    await db.classes.create_index("head_teacher_id")
    await db.schedules.create_index([("classes.class_id", 1), ("weekday", 1), ("period", 1)])
    await db.schedules.create_index("lesson_id", unique=True)
    await db.attendance.create_index([("lesson_id", 1), ("student_id", 1)])
    await db.attendance.create_index("date")
    await db.conduct.create_index([("student_id", 1), ("date", 1)])
    await db.leaves.create_index([("class_id", 1), ("from_date", 1)])
    await db.leaves.create_index("student_id")
    await db.directives.create_index([("created_at", -1)])
    await db.directives.create_index("level")

    # 选择一个班主任与任课教师
    head_teacher = await db.users.find_one({"role": "manager", "edition": mode})
    teacher_a = await db.users.find_one({"role": "leader", "edition": mode})
    teacher_b = head_teacher

    # 班级
    classes_docs = [
        {
            "class_id": "SW22-1",
            "name": "22级软件技术1班",
            "grade": "22级",
            "major": "软件技术",
            "head_teacher_id": head_teacher["_id"] if head_teacher else None,
            "students_count": 0,
        },
        {
            "class_id": "SW22-2",
            "name": "22级软件技术2班",
            "grade": "22级",
            "major": "软件技术",
            "head_teacher_id": head_teacher["_id"] if head_teacher else None,
            "students_count": 0,
        },
    ]
    await db.classes.insert_many(classes_docs)

    # 学生
    def gen_students(class_id: str, count: int):
        docs = []
        for i in range(1, count + 1):
            sid = f"{class_id}-{i:03d}"
            docs.append({
                "student_id": sid,
                "name": f"{class_id}学生{i:03d}",
                "gender": "男" if i % 2 == 1 else "女",
                "grade": "22级",
                "major": "软件技术",
                "class_id": class_id,
                "status": "在读",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            })
        return docs

    students_docs = gen_students("SW22-1", 12) + gen_students("SW22-2", 12)
    sample_user = await db.users.find_one({"username": "user", "edition": mode})
    if sample_user and students_docs:
        students_docs[0]["user_id"] = sample_user["_id"]
    await db.students.insert_many(students_docs)

    # 更新班级人数
    counts = {
        "SW22-1": 12,
        "SW22-2": 12,
    }
    for cid, c in counts.items():
        await db.classes.update_one({"class_id": cid}, {"$set": {"students_count": c}})

    # 课表（周一～周五，每天 4 节），多班共享同一节次，按班级分别给出教室
    courses = ["C语言基础", "数据库原理", "Web前端", "Java", "软件测试", "数据结构"]
    locations_a = ["A-101", "A-102", "A-201", "A-202"]
    locations_b = ["B-101", "B-102", "B-201", "B-202"]

    schedules_docs = []
    idx = 0
    for weekday in range(1, 6):
        for period in range(1, 5):
            course = courses[idx % len(courses)]
            loc_a = locations_a[idx % len(locations_a)]
            loc_b = locations_b[idx % len(locations_b)]
            teacher_id = (teacher_a or head_teacher)["_id"] if (teacher_a or head_teacher) else None
            lesson_id = f"W{weekday}-P{period}"
            schedules_docs.append({
                "lesson_id": lesson_id,
                "weekday": weekday,
                "period": period,
                "course_name": course,
                "teacher_id": teacher_id,
                "start_time": f"{8 + period - 1}:00",
                "end_time": f"{8 + period}:40",
                "week_range": "1-18",
                "classes": [
                    {"class_id": "SW22-1", "location": loc_a},
                    {"class_id": "SW22-2", "location": loc_b},
                ],
                "created_at": datetime.now(),
            })
            idx += 1

    await db.schedules.insert_many(schedules_docs)

    # 今日考勤样例
    today = datetime.now().date().isoformat()
    sample_attendance = []
    for i in range(1, 6):
        sid = f"SW22-1-{i:03d}"
        sample_attendance.append({
            "lesson_id": "W1-P1",
            "class_id": "SW22-1",
            "student_id": sid,
            "date": today,
            "status": "出勤" if i % 4 != 0 else "请假",
        })
    for i in range(1, 6):
        sid = f"SW22-2-{i:03d}"
        sample_attendance.append({
            "lesson_id": "W1-P1",
            "class_id": "SW22-2",
            "student_id": sid,
            "date": today,
            "status": "出勤" if i % 5 != 0 else "缺勤",
        })
    await db.attendance.insert_many(sample_attendance)

    # 操行样例
    conduct_docs = [
        {
            "student_id": "SW22-1-001",
            "date": today,
            "metrics": {"德育": 90, "纪律": 88, "卫生": 92},
            "teacher_comment": "课堂表现积极",
            "head_teacher_comment": "遵守纪律，乐于助人",
            "score": 90,
        },
        {
            "student_id": "SW22-2-001",
            "date": today,
            "metrics": {"德育": 85, "纪律": 80, "卫生": 86},
            "teacher_comment": "需要提高专注度",
            "head_teacher_comment": "总体良好",
            "score": 84,
        },
    ]
    await db.conduct.insert_many(conduct_docs)

    # 请假样例
    leaves_docs = [
        {
            "student_id": "SW22-1-004",
            "class_id": "SW22-1",
            "from_date": today,
            "to_date": today,
            "reason": "生病",
            "approved_by": head_teacher["_id"] if head_teacher else None,
            "status": "已批准",
        },
    ]
    await db.leaves.insert_many(leaves_docs)

    # 指示样例
    directives_docs = [
        {
            "level": "department",
            "content": "本周开展课堂纪律专项检查",
            "created_at": datetime.now(),
            "issuer_id": teacher_b["_id"] if teacher_b else None,
            "targets": ["软件技术系"],
        },
        {
            "level": "campus",
            "content": "期中考试安排与安全教育",
            "created_at": datetime.now(),
            "issuer_id": teacher_a["_id"] if teacher_a else None,
            "targets": [],
        },
    ]
    await db.directives.insert_many(directives_docs)

    print("学校业务数据初始化完成：students/classes/schedules/attendance/conduct/leaves/directives")

if __name__ == "__main__":
    asyncio.run(init_db())