#!/usr/bin/env python3
"""
LLM Filter 系统环境变量生成脚本

功能：
1. 生成安全的随机密钥和密码
2. 创建 .env 文件
3. 执行多重安全检查
4. 验证配置完整性

使用方法：
    python scripts/generate_secrets.py

注意事项：
- 不要将生成的 .env 文件提交到 Git
- 定期更新敏感信息
- 生产环境使用更强的密码
"""

import secrets
import os
import sys
import re
from datetime import datetime
from pathlib import Path

# ANSI 颜色代码
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """打印标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")

def print_success(text):
    """打印成功信息"""
    print(f"{Colors.OKGREEN}[OK] {text}{Colors.ENDC}")

def print_warning(text):
    """打印警告信息"""
    print(f"{Colors.WARNING}[WARN] {text}{Colors.ENDC}")

def print_error(text):
    """打印错误信息"""
    print(f"{Colors.FAIL}[ERROR] {text}{Colors.ENDC}")

def print_info(text):
    """打印信息"""
    print(f"{Colors.OKCYAN}[INFO] {text}{Colors.ENDC}")

def generate_jwt_secret(length=64):
    """
    生成 JWT 密钥
    
    Args:
        length: 密钥长度（字节），默认 64 字节
    
    Returns:
        随机生成的 JWT 密钥字符串
    """
    return secrets.token_urlsafe(length)

def generate_db_password(length=32):
    """
    生成数据库密码
    
    Args:
        length: 密码长度（字节），默认 32 字节
    
    Returns:
        随机生成的数据库密码字符串
    """
    return secrets.token_urlsafe(length)

def generate_admin_password(length=16):
    """
    生成管理员密码
    
    Args:
        length: 密码长度（字节），默认 16 字节
    
    Returns:
        随机生成的管理员密码字符串
    """
    return secrets.token_urlsafe(length)

def generate_api_key():
    """
    生成 API Key 格式
    
    Returns:
        格式为 'app-{random_key}' 的 API Key
    """
    return f"app-{secrets.token_urlsafe(32)}"

def check_secret_strength(secret, min_length=32, secret_type="Secret"):
    """
    检查密钥强度
    
    Args:
        secret: 要检查的密钥
        min_length: 最小长度要求
        secret_type: 密钥类型（用于错误提示）
    
    Returns:
        bool: 是否满足强度要求
    """
    if len(secret) < min_length:
        print_error(f"{secret_type} 长度不足（要求至少 {min_length} 字节，实际 {len(secret)} 字节）")
        return False
    
    if secret in ["your_secret_key_here", "your_secure_password_here"]:
        print_error(f"{secret_type} 使用了默认值，请修改")
        return False
    
    return True

def check_gitignore():
    """
    检查 .gitignore 是否正确配置
    
    Returns:
        bool: .gitignore 是否包含必要规则
    """
    gitignore_path = Path(".gitignore")
    
    if not gitignore_path.exists():
        print_warning(".gitignore 文件不存在")
        return False
    
    try:
        content = gitignore_path.read_text(encoding='utf-8')
    except Exception:
        content = gitignore_path.read_text(encoding='gbk')
    
    required_patterns = [".env", ".env.local", ".env.*.local", "*.key", "credentials.json"]
    missing_patterns = []
    
    for pattern in required_patterns:
        if pattern not in content:
            missing_patterns.append(pattern)
    
    if missing_patterns:
        print_warning(f".gitignore 缺少以下规则：{', '.join(missing_patterns)}")
        return False
    
    print_success(".gitignore 配置正确")
    return True

def check_existing_env(env_file):
    """
    检查是否已存在 .env 文件
    
    Args:
        env_file: .env 文件路径
    
    Returns:
        bool: 是否可以覆盖
    """
    if not env_file.exists():
        return True
    
    print_warning(f"{env_file} 已存在")
    
    # 检查是否包含真实的敏感信息
    try:
        content = env_file.read_text(encoding='utf-8')
    except Exception:
        content = env_file.read_text(encoding='gbk')
    
    # 检查是否有模板值
    template_patterns = [
        "your_secure_password_here",
        "your_jwt_secret_key",
        "your_dify_api_key_here",
        "your_admin_password_here"
    ]
    
    has_real_values = any(pattern not in content for pattern in template_patterns)
    
    if has_real_values:
        print_warning("检测到 .env 文件包含真实配置，覆盖可能导致服务中断")
        print_info("建议备份现有 .env 文件：")
        print(f"  cp {env_file} {env_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    response = input("是否继续覆盖？(y/n): ").strip().lower()
    return response == 'y'

def validate_generated_values(values):
    """
    验证生成的配置值
    
    Args:
        values: 包含所有配置值的字典
    
    Returns:
        bool: 所有值是否有效
    """
    print_header("安全检查")
    
    all_valid = True
    
    # 检查 JWT_SECRET
    if check_secret_strength(values['JWT_SECRET'], 32, "JWT_SECRET"):
        print_success(f"JWT_SECRET 长度：{len(values['JWT_SECRET'])} 字节")
    else:
        all_valid = False
    
    # 检查 DB_PASSWORD
    if check_secret_strength(values['DB_PASSWORD'], 16, "DB_PASSWORD"):
        print_success(f"DB_PASSWORD 长度：{len(values['DB_PASSWORD'])} 字节")
    else:
        all_valid = False
    
    # 检查 ADMIN_PASSWORD
    if check_secret_strength(values['ADMIN_PASSWORD'], 8, "ADMIN_PASSWORD"):
        print_success(f"ADMIN_PASSWORD 长度：{len(values['ADMIN_PASSWORD'])} 字节")
    else:
        all_valid = False
    
    return all_valid

def generate_env_file():
    """
    生成完整的 .env 文件内容
    
    Returns:
        str: .env 文件内容
    """
    values = {
        'JWT_SECRET': generate_jwt_secret(),
        'DB_PASSWORD': generate_db_password(),
        'ADMIN_PASSWORD': generate_admin_password(),
        'DB_HOST': 'postgres',
        'DB_PORT': '5432',
        'DB_USER': 'admin',
        'DB_NAME': 'llm_filter_db',
        'DB_SSL_MODE': 'disable',
        'ALGORITHM': 'HS256',
        'ACCESS_TOKEN_EXPIRE_MINUTES': '30',
        'DIFY_API_URL': 'http://192.168.6.6/v1',
        'DIFY_API_KEY': 'your_dify_api_key_here',
        'DIFY_RESPONSE_MODE': 'streaming',
        'DIFY_MESSAGE_ENDPOINT': 'chat-messages',
        'MONGODB_URL': 'mongodb://mongo:27017',
        'MONGODB_DB_NAME': 'security_service_db',
        'REDIS_HOST': 'redis',
        'REDIS_PORT': '6379',
        'REDIS_PASSWORD': generate_db_password(16),
        'REDIS_DB': '0',
        'REDIS_TIMEOUT': '2000',
        'OLLAMA_BASE_URL': 'http://192.168.6.6:11434/',
        'OLLAMA_MODEL': 'deepseek-r1:14b',
        'APP_BASE_URL': 'http://localhost:8000',
        'API_V1_STR': '/api/v1',
        'APP_MODE': 'edu',
        'TERM_START_DATE': '2025-09-01',
        'CORS_ALLOWED_ORIGINS': '*',
        'SERVER_PORT': '8082',
        'JPA_DDL_AUTO': 'update',
        'JPA_SHOW_SQL': 'true',
        'JPA_FORMAT_SQL': 'true',
        'JPA_DIALECT': 'org.hibernate.dialect.PostgreSQLDialect',
        'LOGGING_LEVEL': 'INFO',
        'ADMIN_USERNAME': 'admin',
        'ADMIN_EMAIL': 'admin@example.com',
        'TZ': 'Asia/Shanghai',
        'GATEWAY_PORT': '8080',
        'AUTH_SERVICE_PORT': '8081',
        'EDU_SERVICE_PORT': '8082',
        'LLM_SERVICE_PORT': '8000',
        'SECURITY_SERVICE_PORT': '8003',
        'POSTGRES_PORT_EXTERNAL': '5433',
        'MONGODB_PORT_EXTERNAL': '27017',
        'REDIS_PORT_EXTERNAL': '6379',
    }
    
    env_content = f"""# ============================================================
# LLM Filter 系统环境变量配置
# ============================================================
# 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 生成脚本：scripts/generate_secrets.py
# 
# ⚠️  安全警告：
#   - 此文件包含敏感信息，不要提交到 Git 仓库
#   - 不要分享此文件或其内容
#   - 生产环境请使用更强的密码和密钥
#   - 定期轮换敏感信息
#
# 📝 配置说明：
#   - 所有敏感信息已自动生成
#   - 保留了原有的服务地址配置
#   - 需要手动填写 DIFY_API_KEY
#   - 可根据实际需求修改其他配置
# ============================================================

# ============================================================
# 📊 数据库配置 (PostgreSQL)
# ============================================================
DB_HOST={values['DB_HOST']}
DB_PORT={values['DB_PORT']}
DB_USER={values['DB_USER']}
DB_PASSWORD={values['DB_PASSWORD']}
DB_NAME={values['DB_NAME']}
DB_SSL_MODE={values['DB_SSL_MODE']}

# ============================================================
# 🔐 JWT 认证配置
# ============================================================
JWT_SECRET={values['JWT_SECRET']}
ALGORITHM={values['ALGORITHM']}
ACCESS_TOKEN_EXPIRE_MINUTES={values['ACCESS_TOKEN_EXPIRE_MINUTES']}

# ============================================================
# 🔧 Dify AI 平台配置
# ============================================================
DIFY_API_URL={values['DIFY_API_URL']}
DIFY_API_KEY={values['DIFY_API_KEY']}
DIFY_RESPONSE_MODE={values['DIFY_RESPONSE_MODE']}
DIFY_MESSAGE_ENDPOINT={values['DIFY_MESSAGE_ENDPOINT']}

# ============================================================
# 🍃 MongoDB 配置
# ============================================================
MONGODB_URL={values['MONGODB_URL']}
DB_NAME={values['DB_NAME']}
MONGODB_DB_NAME={values['MONGODB_DB_NAME']}

# ============================================================
# 🚀 Redis 配置
# ============================================================
REDIS_HOST={values['REDIS_HOST']}
REDIS_PORT={values['REDIS_PORT']}
REDIS_PASSWORD={values['REDIS_PASSWORD']}
REDIS_DB={values['REDIS_DB']}
REDIS_TIMEOUT={values['REDIS_TIMEOUT']}

# ============================================================
# 🤖 Ollama 本地 LLM 配置
# ============================================================
OLLAMA_BASE_URL={values['OLLAMA_BASE_URL']}
OLLAMA_MODEL={values['OLLAMA_MODEL']}

# ============================================================
# 🌐 应用基础配置
# ============================================================
APP_BASE_URL={values['APP_BASE_URL']}
API_V1_STR={values['API_V1_STR']}
APP_MODE={values['APP_MODE']}
TERM_START_DATE={values['TERM_START_DATE']}

# ============================================================
# 🎨 CORS 跨域配置
# ============================================================
CORS_ALLOWED_ORIGINS={values['CORS_ALLOWED_ORIGINS']}

# ============================================================
# 🏢 Java Edu Service 配置
# ============================================================
SERVER_PORT={values['SERVER_PORT']}
JPA_DDL_AUTO={values['JPA_DDL_AUTO']}
JPA_SHOW_SQL={values['JPA_SHOW_SQL']}
JPA_FORMAT_SQL={values['JPA_FORMAT_SQL']}
JPA_DIALECT={values['JPA_DIALECT']}
LOGGING_LEVEL={values['LOGGING_LEVEL']}

# ============================================================
# 🔒 Auth Service 配置
# ============================================================
ADMIN_USERNAME={values['ADMIN_USERNAME']}
ADMIN_PASSWORD={values['ADMIN_PASSWORD']}
ADMIN_EMAIL={values['ADMIN_EMAIL']}

# ============================================================
# 🐳 Docker 配置
# ============================================================
TZ={values['TZ']}

# ============================================================
# 📊 服务端口映射（外部访问）
# ============================================================
GATEWAY_PORT={values['GATEWAY_PORT']}
AUTH_SERVICE_PORT={values['AUTH_SERVICE_PORT']}
EDU_SERVICE_PORT={values['EDU_SERVICE_PORT']}
LLM_SERVICE_PORT={values['LLM_SERVICE_PORT']}
SECURITY_SERVICE_PORT={values['SECURITY_SERVICE_PORT']}
POSTGRES_PORT_EXTERNAL={values['POSTGRES_PORT_EXTERNAL']}
MONGODB_PORT_EXTERNAL={values['MONGODB_PORT_EXTERNAL']}
REDIS_PORT_EXTERNAL={values['REDIS_PORT_EXTERNAL']}
"""
    
    return env_content

def print_post_generation_instructions():
    """打印生成后的操作指南"""
    print_header("后续操作步骤")
    
    steps = [
        "1️⃣  填写 DIFY_API_KEY",
        "   编辑 .env 文件，填入您的 Dify API Key",
        "   格式：app-xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "",
        "2️⃣  验证 .gitignore",
        "   确保 .gitignore 包含以下内容：",
        "   - .env",
        "   - .env.local",
        "   - .env.*.local",
        "",
        "3️⃣  重启服务",
        "   docker-compose down",
        "   docker-compose up -d --build",
        "",
        "4️⃣  验证服务启动",
        "   docker-compose ps",
        "   docker-compose logs -f [service-name]",
        "",
        "5️⃣  测试认证",
        "   使用管理员账号登录：",
        f"   用户名：admin",
        "   密码：查看 .env 中的 ADMIN_PASSWORD",
        "",
        "6️⃣  备份配置",
        "   定期备份 .env 文件到安全位置",
    ]
    
    for step in steps:
        print(step)
    
    print_warning("\n⚠️  重要提醒：")
    print("   - 不要将 .env 文件提交到 Git")
    print("   - 定期轮换密码和密钥")
    print("   - 生产环境使用更强的安全措施")

def main():
    """主函数"""
    print_header("LLM Filter 环境变量生成脚本")
    
    # 检查 Python 版本
    if sys.version_info < (3, 6):
        print_error("需要 Python 3.6 或更高版本")
        sys.exit(1)
    
    print_info(f"Python 版本：{sys.version}")
    print_info(f"当前目录：{os.getcwd()}")
    
    # 切换到项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    if (project_root / "docker-compose.yml").exists():
        os.chdir(project_root)
        print_info(f"已切换到项目根目录：{project_root}")
    else:
        print_warning("未检测到 docker-compose.yml，请确保在项目根目录运行脚本")
    
    # 检查 .gitignore
    print_header("环境检查")
    check_gitignore()
    
    # 检查是否已存在 .env 文件
    env_file = Path(".env")
    if not check_existing_env(env_file):
        print_info("操作已取消")
        return
    
    # 生成 .env 文件
    print_header("生成环境变量")
    env_content = generate_env_file()
    
    # 解析生成的值进行验证
    values = {}
    for line in env_content.split('\n'):
        if '=' in line and not line.strip().startswith('#'):
            key, value = line.split('=', 1)
            values[key.strip()] = value.strip()
    
    # 验证生成的值
    if not validate_generated_values(values):
        print_error("生成的密钥不符合安全要求")
        sys.exit(1)
    
    # 写入 .env 文件
    try:
        env_file.write_text(env_content, encoding='utf-8')
        print_success(f"成功生成 {env_file}")
        print_info(f"文件大小：{env_file.stat().st_size} 字节")
    except Exception as e:
        print_error(f"写入文件失败：{e}")
        sys.exit(1)
    
    # 设置文件权限（仅所有者可读写）
    try:
        os.chmod(env_file, 0o600)
        print_success("文件权限已设置为 600（仅所有者可读写）")
    except Exception as e:
        print_warning(f"设置文件权限失败：{e}")
    
    # 打印后续操作指南
    print_post_generation_instructions()
    
    print_success("\n环境变量生成完成！")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print_error(f"\n发生错误：{e}")
        sys.exit(1)
