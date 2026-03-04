@echo off
REM Security Service 启动脚本 (Windows)

echo ============================================================
echo   Security Service - Zabbix集成版本
echo ============================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或未添加到PATH
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo 📥 安装依赖...
pip install -r requirements.txt -q

REM 检查.env文件
if not exist ".env" (
    echo ⚠️  .env文件不存在，复制.env.example...
    copy .env.example .env
    echo ❗ 请编辑.env文件，配置Zabbix服务器信息
    echo ❗ 配置完成后重新运行此脚本
    pause
    exit /b 1
)

REM 启动服务
echo.
echo 🚀 启动Security Service...
echo 📍 服务地址: http://localhost:8002
echo 📚 API文档: http://localhost:8002/docs
echo.
echo 按 Ctrl+C 停止服务
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

pause