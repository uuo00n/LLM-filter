#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== LLM Filter 项目部署脚本 ===${NC}"

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}未检测到 Docker，请先在宝塔面板安装 Docker。${NC}"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    # 尝试检查 docker compose (v2)
    if ! docker compose version &> /dev/null; then
        echo -e "${YELLOW}未检测到 Docker Compose。${NC}"
        echo "请尝试运行: pip install docker-compose 或在宝塔软件商店安装。"
        exit 1
    fi
    DOCKER_COMPOSE_CMD="docker compose"
else
    DOCKER_COMPOSE_CMD="docker-compose"
fi

echo -e "${GREEN}正在停止旧容器...${NC}"
$DOCKER_COMPOSE_CMD -f docker-compose.prod.yml down

echo -e "${GREEN}正在构建并启动服务 (这可能需要几分钟)...${NC}"
$DOCKER_COMPOSE_CMD -f docker-compose.prod.yml up -d --build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}=== 部署成功! ===${NC}"
    echo "服务状态:"
    $DOCKER_COMPOSE_CMD -f docker-compose.prod.yml ps
    echo ""
    echo "访问地址 (本地部署请使用 localhost，服务器部署请使用服务器IP):"
    echo "- API 网关: http://localhost:8080"
    echo "- Auth Service 文档: http://localhost:8080/docs/auth/"
    echo "- Edu Service 文档: http://localhost:8080/docs/edu/"
    echo "- LLM Service 文档: http://localhost:8080/docs/llm/"
    echo "- Security Service 文档: http://localhost:8080/docs/security/"
else
    echo -e "${YELLOW}部署过程中出现错误，请检查日志。${NC}"
fi
