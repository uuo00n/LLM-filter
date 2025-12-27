
-- 创建 Users 表 (如果不存在)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    role_level INTEGER DEFAULT 1,
    edition VARCHAR(20) DEFAULT 'edu',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建 Classes 表
CREATE TABLE IF NOT EXISTS classes (
    class_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    major VARCHAR(50),
    grade INTEGER,
    head_teacher_person_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建 Persons 表
CREATE TABLE IF NOT EXISTS persons (
    person_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL, -- student, teacher
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建 Bindings 表 (User -> Person)
CREATE TABLE IF NOT EXISTS bindings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    person_id VARCHAR(50) REFERENCES persons(person_id) ON DELETE CASCADE,
    type VARCHAR(20),
    "primary" BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建 Students 表
CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(10),
    class_id VARCHAR(50) REFERENCES classes(class_id),
    person_id VARCHAR(50) REFERENCES persons(person_id),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建 Teachers 表
CREATE TABLE IF NOT EXISTS teachers (
    teacher_id VARCHAR(50) PRIMARY KEY,
    person_id VARCHAR(50) REFERENCES persons(person_id),
    department VARCHAR(50),
    roles VARCHAR(100), -- comma separated roles
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建 Schedules 表
CREATE TABLE IF NOT EXISTS schedules (
    id SERIAL PRIMARY KEY,
    lesson_id VARCHAR(50),
    weekday INTEGER,
    period INTEGER,
    course_name VARCHAR(100),
    teacher_person_id VARCHAR(50),
    classes JSONB, -- stores array of {class_id, location}
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建 Attendance 表 (考勤)
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) REFERENCES students(student_id),
    class_id VARCHAR(50) REFERENCES classes(class_id),
    date DATE,
    lesson_id VARCHAR(50),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建 Conduct 表 (操行)
CREATE TABLE IF NOT EXISTS conduct (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) REFERENCES students(student_id),
    date DATE,
    metrics JSONB, -- {"discipline": 5, "hygiene": 4}
    score INTEGER,
    teacher_comment TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建 Directives 表 (通知/指示)
CREATE TABLE IF NOT EXISTS directives (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20), -- campus, grade, department
    content TEXT,
    issuer_id VARCHAR(50) REFERENCES persons(person_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 清理旧数据
TRUNCATE TABLE users RESTART IDENTITY CASCADE;
TRUNCATE TABLE classes RESTART IDENTITY CASCADE;
TRUNCATE TABLE persons RESTART IDENTITY CASCADE;
TRUNCATE TABLE bindings RESTART IDENTITY CASCADE;
TRUNCATE TABLE students RESTART IDENTITY CASCADE;
TRUNCATE TABLE teachers RESTART IDENTITY CASCADE;
TRUNCATE TABLE schedules RESTART IDENTITY CASCADE;
TRUNCATE TABLE attendance RESTART IDENTITY CASCADE;
TRUNCATE TABLE conduct RESTART IDENTITY CASCADE;
TRUNCATE TABLE directives RESTART IDENTITY CASCADE;

-- 插入 Edu 版用户 (密码均为 password123 的 bcrypt 哈希)
-- $2b$12$P7tzdKfHMVJd43wyX1Z1GO0W9TMf.oNo2lqbPDTXLH/dfRpB4SgMm

-- 1. 学生 (对应3个班级)
INSERT INTO users (username, email, password, role, role_level, edition, created_at, updated_at) VALUES
('student_101', 'stu101@example.com', '$2b$12$P7tzdKfHMVJd43wyX1Z1GO0W9TMf.oNo2lqbPDTXLH/dfRpB4SgMm', 'user', 1, 'edu', NOW(), NOW()), -- ID: 1, Class 1
('student_102', 'stu102@example.com', '$2b$12$P7tzdKfHMVJd43wyX1Z1GO0W9TMf.oNo2lqbPDTXLH/dfRpB4SgMm', 'user', 1, 'edu', NOW(), NOW()), -- ID: 2, Class 2
('student_103', 'stu103@example.com', '$2b$12$P7tzdKfHMVJd43wyX1Z1GO0W9TMf.oNo2lqbPDTXLH/dfRpB4SgMm', 'user', 1, 'edu', NOW(), NOW()); -- ID: 3, Class 3

-- 2. 班主任 (对应3个班级)
INSERT INTO users (username, email, password, role, role_level, edition, created_at, updated_at) VALUES
('teacher_101', 'tea101@example.com', '$2b$12$P7tzdKfHMVJd43wyX1Z1GO0W9TMf.oNo2lqbPDTXLH/dfRpB4SgMm', 'manager', 2, 'edu', NOW(), NOW()), -- ID: 4, Class 1 Homeroom
('teacher_102', 'tea102@example.com', '$2b$12$P7tzdKfHMVJd43wyX1Z1GO0W9TMf.oNo2lqbPDTXLH/dfRpB4SgMm', 'manager', 2, 'edu', NOW(), NOW()), -- ID: 5, Class 2 Homeroom
('teacher_103', 'tea103@example.com', '$2b$12$P7tzdKfHMVJd43wyX1Z1GO0W9TMf.oNo2lqbPDTXLH/dfRpB4SgMm', 'manager', 2, 'edu', NOW(), NOW()); -- ID: 6, Class 3 Homeroom

-- 3. 教务/中层 (2位)
INSERT INTO users (username, email, password, role, role_level, edition, created_at, updated_at) VALUES
('leader_academic', 'academic@example.com', '$2b$12$P7tzdKfHMVJd43wyX1Z1GO0W9TMf.oNo2lqbPDTXLH/dfRpB4SgMm', 'leader', 3, 'edu', NOW(), NOW()), -- ID: 7, 教务主任
('leader_grade', 'grade@example.com', '$2b$12$P7tzdKfHMVJd43wyX1Z1GO0W9TMf.oNo2lqbPDTXLH/dfRpB4SgMm', 'leader', 3, 'edu', NOW(), NOW());    -- ID: 8, 年级组长

-- 4. 校级领导 (1位)
INSERT INTO users (username, email, password, role, role_level, edition, created_at, updated_at) VALUES
('master_principal', 'principal@example.com', '$2b$12$P7tzdKfHMVJd43wyX1Z1GO0W9TMf.oNo2lqbPDTXLH/dfRpB4SgMm', 'master', 4, 'edu', NOW(), NOW()); -- ID: 9, 校长

-- 5. 系统管理员 (1位)
INSERT INTO users (username, email, password, role, role_level, edition, created_at, updated_at) VALUES
('admin_edu', 'admin_edu@example.com', '$2b$12$P7tzdKfHMVJd43wyX1Z1GO0W9TMf.oNo2lqbPDTXLH/dfRpB4SgMm', 'admin', 5, 'edu', NOW(), NOW()); -- ID: 10

-- 6. Biz 版保留账号 (2位)
INSERT INTO users (username, email, password, role, role_level, edition, created_at, updated_at) VALUES
('staff_biz', 'staff_biz@example.com', '$2b$12$P7tzdKfHMVJd43wyX1Z1GO0W9TMf.oNo2lqbPDTXLH/dfRpB4SgMm', 'user', 1, 'biz', NOW(), NOW()),    -- ID: 11
('manager_biz', 'manager_biz@example.com', '$2b$12$P7tzdKfHMVJd43wyX1Z1GO0W9TMf.oNo2lqbPDTXLH/dfRpB4SgMm', 'manager', 2, 'biz', NOW(), NOW()); -- ID: 12
