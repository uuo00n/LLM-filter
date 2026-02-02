#!/bin/bash
# Security Service 启动脚本 (Linux/MacOS)

echo "============================================================"
echo "   Security Service - Zabbix集成版本"
echo "============================================================"
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -r requirements.txt -q

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  .env文件不存在，复制.env.example..."
    cp .env.example .env
    echo "❗ 请编辑.env文件，配置Zabbix服务器信息"
    echo "❗ 配置完成后重新运行此脚本"
    exit 1
fi

# 启动服务
echo
echo "🚀 启动Security Service..."
echo "📍 服务地址: http://localhost:8002"
echo "📚 API文档: http://localhost:8002/docs"
echo
echo "按 Ctrl+C 停止服务"
echo

python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload