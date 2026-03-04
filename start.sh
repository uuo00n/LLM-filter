#!/bin/bash
# LLM Filter 项目启动脚本

echo "=========================================="
echo "  LLM Filter 项目启动脚本"
echo "=========================================="
echo ""

# 检查 Docker 和 Docker Compose
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker 未安装"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "[ERROR] Docker Compose 未安装"
    exit 1
fi

echo "[INFO] Docker 和 Docker Compose 已安装"
echo ""

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "[ERROR] .env 文件不存在，请先运行："
    echo "  python scripts/generate_secrets.py"
    exit 1
fi

echo "[INFO] .env 文件存在"
echo ""

# 步骤 1：停止现有服务
echo "=========================================="
echo "步骤 1: 停止现有服务"
echo "=========================================="
docker-compose down
echo ""

# 步骤 2：启动基础设施
echo "=========================================="
echo "步骤 2: 启动基础设施 (PostgreSQL, Redis, MongoDB)"
echo "=========================================="
docker-compose up -d postgres redis mongo

echo "[INFO] 等待数据库启动..."
sleep 10

echo ""
echo "[INFO] 检查数据库状态..."
docker-compose ps postgres redis mongo
echo ""

# 步骤 3：启动业务服务
echo "=========================================="
echo "步骤 3: 启动业务服务"
echo "=========================================="
docker-compose up -d auth-service edu-service llm-service security-service

echo "[INFO] 等待服务启动..."
sleep 15

echo ""
echo "[INFO] 检查业务服务状态..."
docker-compose ps auth-service edu-service llm-service security-service
echo ""

# 步骤 4：启动网关
echo "=========================================="
echo "步骤 4: 启动 API 网关"
echo "=========================================="
docker-compose up -d gateway

echo "[INFO] 等待网关启动..."
sleep 5

echo ""
echo "[INFO] 检查网关状态..."
docker-compose ps gateway
echo ""

# 步骤 5：验证服务
echo "=========================================="
echo "步骤 5: 验证所有服务"
echo "=========================================="
docker-compose ps
echo ""

echo "=========================================="
echo "  启动完成！"
echo "=========================================="
echo ""
echo "📚 文档地址："
echo "  - Gateway:       http://localhost:8080"
echo "  - Auth Service:  http://localhost:8080/docs/auth/"
echo "  - Edu Service:   http://localhost:8080/docs/edu/"
echo "  - LLM Service:   http://localhost:8080/docs/llm/"
echo "  - Security:      http://localhost:8080/docs/security/"
echo ""
echo "🔑 默认管理员账号："
echo "  - 用户名: admin"
echo "  - 密码: 查看 .env 文件中的 ADMIN_PASSWORD"
echo ""
echo "📊 查看日志："
echo "  - 所有服务:   docker-compose logs -f"
echo "  - 特定服务:   docker-compose logs -f [service-name]"
echo ""
