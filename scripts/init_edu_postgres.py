import asyncio
import os
import random
import json
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import Json

# 配置
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "llm_filter_db")
DB_PORT = os.getenv("DB_PORT", "5432")

# 用户映射 (对应 init_postgres.sql)
PG_USERS = {
    "student_101": 1,
    "student_102": 2,
    "student_103": 3,
    "teacher_101": 4,
    "teacher_102": 5,
    "teacher_103": 6,
    "leader_academic": 7,
    "leader_grade": 8,
    "master_principal": 9,
    "admin_edu": 10,
    "staff_biz": 11,
    "manager_biz": 12
}

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
        port=DB_PORT
    )

def init_postgres_data():
    print(f"Connecting to PostgreSQL: {DB_HOST}:{DB_PORT}/{DB_NAME} ...")
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # 1. 清理旧业务数据 (保留 users 表)
        # 注意表名与 Java Entity @Table(name=...) 对应
        tables = ["attendance", "conduct", "directives", "schedules", "students", "teachers", "classes", "persons", "bindings"]
        for table in tables:
            # 检查表是否存在
            cur.execute(f"SELECT to_regclass('public.{table}')")
            if cur.fetchone()[0]:
                print(f"Truncating table {table}...")
                cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
        
        # 2. 创建班级 (Classes)
        print("Creating classes...")
        class_ids = {} # idx -> class_id (string)
        classes_info = [
            {"name": "软件2301班", "grade": 2023, "major": "软件工程"},
            {"name": "软件2302班", "grade": 2023, "major": "软件工程"},
            {"name": "网络2301班", "grade": 2023, "major": "网络技术"}
        ]
        
        for i, info in enumerate(classes_info):
            cid = f"CLASS-2023-{i+1:02d}"
            class_ids[i+1] = cid
            # Java Entity: ClassEntity (id, classId, name, major, grade, headTeacherPersonId)
            cur.execute("""
                INSERT INTO classes (class_id, name, major, grade, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """, (cid, info["name"], info["major"], info["grade"]))
        
        print(f"Created {len(class_ids)} classes.")

        # 3. 创建人物、绑定、实体
        print("Creating persons, bindings and entities...")
        
        person_ids = {} # username -> person_id

        # --- Students ---
        students_data = [
            {"user": "student_101", "name": "张一", "class_idx": 1, "sid": "S20230101"},
            {"user": "student_102", "name": "李二", "class_idx": 2, "sid": "S20230102"},
            {"user": "student_103", "name": "王三", "class_idx": 3, "sid": "S20230103"}
        ]

        for s in students_data:
            pid = f"PID-{s['user'].upper()}" # 构造一个唯一ID
            person_ids[s["user"]] = pid
            
            # Person
            cur.execute("""
                INSERT INTO persons (person_id, name, type, created_at, updated_at)
                VALUES (%s, %s, 'student', NOW(), NOW())
            """, (pid, s["name"]))

            # Binding
            user_id = PG_USERS[s["user"]]
            cur.execute("""
                INSERT INTO bindings (user_id, person_id, type, "primary", created_at, updated_at)
                VALUES (%s, %s, 'student', true, NOW(), NOW())
            """, (user_id, pid))

            # Student
            cid = class_ids[s["class_idx"]]
            gender = random.choice(["男", "女"])
            cur.execute("""
                INSERT INTO students (student_id, name, gender, class_id, person_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            """, (s["sid"], s["name"], gender, cid, pid))

        # --- Teachers ---
        teachers_data = [
            {"user": "teacher_101", "name": "赵老师", "dept": "软件教研室", "class_idx": 1, "tid": "T001"},
            {"user": "teacher_102", "name": "钱老师", "dept": "基础教研室", "class_idx": 2, "tid": "T002"},
            {"user": "teacher_103", "name": "孙老师", "dept": "网络教研室", "class_idx": 3, "tid": "T003"}
        ]

        for t in teachers_data:
            pid = f"PID-{t['user'].upper()}"
            person_ids[t["user"]] = pid

            # Person
            cur.execute("""
                INSERT INTO persons (person_id, name, type, created_at, updated_at)
                VALUES (%s, %s, 'teacher', NOW(), NOW())
            """, (pid, t["name"]))

            # Binding
            user_id = PG_USERS[t["user"]]
            cur.execute("""
                INSERT INTO bindings (user_id, person_id, type, "primary", created_at, updated_at)
                VALUES (%s, %s, 'teacher', true, NOW(), NOW())
            """, (user_id, pid))

            # Teacher
            cur.execute("""
                INSERT INTO teachers (teacher_id, person_id, department, roles, created_at, updated_at)
                VALUES (%s, %s, %s, 'teacher,homeroom', NOW(), NOW())
            """, (t["tid"], pid, t["dept"]))

            # Update Class Head Teacher
            cid = class_ids[t["class_idx"]]
            cur.execute("""
                UPDATE classes SET head_teacher_person_id = %s WHERE class_id = %s
            """, (pid, cid))

        # --- Leaders ---
        leaders_data = [
            {"user": "leader_academic", "name": "周主任", "dept": "教务处", "role": "cadre", "tid": "L001"},
            {"user": "leader_grade", "name": "吴组长", "dept": "学生处", "role": "cadre", "tid": "L002"},
            {"user": "master_principal", "name": "郑校长", "dept": "校长室", "role": "master", "tid": "M001"}
        ]

        for l in leaders_data:
            pid = f"PID-{l['user'].upper()}"
            person_ids[l["user"]] = pid

            # Person
            cur.execute("""
                INSERT INTO persons (person_id, name, type, created_at, updated_at)
                VALUES (%s, %s, 'teacher', NOW(), NOW())
            """, (pid, l["name"]))

            # Binding
            user_id = PG_USERS[l["user"]]
            cur.execute("""
                INSERT INTO bindings (user_id, person_id, type, "primary", created_at, updated_at)
                VALUES (%s, %s, 'teacher', true, NOW(), NOW())
            """, (user_id, pid))

            # Teacher
            roles = f"teacher,{l['role']}"
            cur.execute("""
                INSERT INTO teachers (teacher_id, person_id, department, roles, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """, (l["tid"], pid, l["dept"], roles))

        # 4. 创建课表 (Schedules)
        print("Creating schedules...")
        weekdays = [1, 2, 3, 4, 5]
        periods = [1, 2, 3, 4, 5, 6, 7, 8]
        courses_pool = ["Java程序设计", "MySQL数据库", "Web前端开发", "计算机网络", "Linux操作系统", "Python编程", "职场英语", "体育与健康", "毛概", "心理健康"]

        for class_idx, cid in class_ids.items():
            homeroom_user = f"teacher_10{class_idx}"
            homeroom_pid = person_ids[homeroom_user]
            
            if class_idx == 1:
                main_course = "Java程序设计"
            elif class_idx == 2:
                main_course = "Web前端开发"
            else:
                main_course = "计算机网络"

            for wd in weekdays:
                for p in periods:
                    teacher_pid = None
                    course = None
                    location = f"实训楼{200+class_idx}"

                    if p == 1:
                        course = main_course
                        teacher_pid = homeroom_pid
                    elif wd == 1 and p == 8:
                        course = "班会"
                        teacher_pid = homeroom_pid
                    else:
                        course = random.choice(courses_pool)
                        if random.random() < 0.1:
                            teacher_pid = person_ids["leader_academic"]
                    
                    lesson_id = f"C{class_idx}-W{wd}-P{p}"
                    
                    # Construct classes JSON
                    # Java entity uses 'classes' column (jsonb)
                    classes_json = [{"class_id": cid, "location": location}]
                    
                    cur.execute("""
                        INSERT INTO schedules (lesson_id, weekday, period, course_name, teacher_person_id, classes, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """, (lesson_id, wd, p, course, teacher_pid, Json(classes_json)))

        # 5. 创建出勤与操行 (Attendance & Conduct) - 迁移自 MongoDB
        print("Creating attendance and conduct (Migrated to Postgres)...")
        today = datetime.now().date()
        
        for s in students_data:
            cid = class_ids[s["class_idx"]]
            sid = s["sid"]
            class_idx = s["class_idx"]

            # 出勤
            cur.execute("""
                INSERT INTO attendance (student_id, class_id, date, lesson_id, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            """, (sid, cid, today, f"C{class_idx}-W1-P1", random.choice(["出勤", "出勤", "出勤", "迟到"])))
            
            # 操行
            metrics = {"discipline": random.randint(3,5), "hygiene": random.randint(3,5)}
            score = random.randint(8, 10)
            comment = random.choice(["表现良好", "积极发言", "需注意纪律"])
            cur.execute("""
                INSERT INTO conduct (student_id, date, metrics, score, teacher_comment, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            """, (sid, today, Json(metrics), score, comment))

        # 6. 创建指示 (Directives) - 迁移自 MongoDB
        print("Creating directives (Migrated to Postgres)...")
        
        directives_data = [
            {"level": "campus", "content": "【重要】关于举办首届'软件杯'程序设计大赛的通知", "issuer": "master_principal"},
            {"level": "grade", "content": "23级软件专业实训周安排", "issuer": "leader_grade"},
            {"level": "department", "content": "软件教研室关于开展Java课程教学研讨", "issuer": "leader_academic"}
        ]

        for d in directives_data:
            issuer_pid = person_ids[d["issuer"]]
            cur.execute("""
                INSERT INTO directives (level, content, issuer_id, created_at, updated_at)
                VALUES (%s, %s, %s, NOW(), NOW())
            """, (d["level"], d["content"], issuer_pid))

        conn.commit()
        print("PostgreSQL initialization completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"Error initializing PostgreSQL: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_postgres_data()
