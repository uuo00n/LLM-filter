#!/bin/bash

# =============================================================================
# LLM Filter 项目生产环境部署脚本 (Ubuntu/Debian)
# =============================================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}       LLM Filter 系统 - 生产环境部署脚本 (Ubuntu)    ${NC}"
echo -e "${BLUE}======================================================${NC}"
echo ""

# 1. 权限检查
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}[提示] 请使用 sudo 运行此脚本，以便管理 Docker 服务。${NC}"
    echo -e "示例: sudo ./deploy.sh"
    exit 1
fi

# 2. 系统环境检查与依赖安装
echo -e "${BLUE}[1/5] 检查系统环境...${NC}"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}未检测到 Docker，正在尝试自动安装 (适用于 Ubuntu)...${NC}"
    
    apt-get update
    apt-get install -y ca-certificates curl gnupg
    
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=\"$(dpkg --print-architecture)\" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null
      
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}[错误] Docker 安装失败，请手动安装后重试。${NC}"
        exit 1
    fi
    echo -e "${GREEN}Docker 安装成功!${NC}"
else
    echo -e "${GREEN}Docker 已安装。${NC}"
fi

# 确定 Docker Compose 命令
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo -e "${RED}[错误] 未找到 Docker Compose 插件。${NC}"
    echo "请尝试运行: apt-get install docker-compose-plugin"
    exit 1
fi
echo -e "${GREEN}使用 Compose 命令: $COMPOSE_CMD${NC}"

# 3. 配置检查
echo -e "${BLUE}[2/5] 检查环境配置...${NC}"

if [ ! -f .env ]; then
    echo -e "${YELLOW}.env 文件不存在，正在生成默认配置...${NC}"
    
    # 检查 python3
    if command -v python3 &> /dev/null; then
        python3 scripts/generate_secrets.py
        if [ $? -eq 0 ]; then
             echo -e "${GREEN}.env 文件已生成。请务必检查其中的配置（如数据库密码、API Key）。${NC}"
             echo -e "${YELLOW}是否现在暂停脚本以编辑 .env 文件? (y/n)${NC}"
             read -r -p "输入 y 编辑，n 继续: " choice
             if [[ "$choice" =~ ^[Yy]$ ]]; then
                 echo "请编辑 .env 文件后重新运行此脚本。"
                 exit 0
             fi
        else
             echo -e "${RED}[错误] 生成 .env 失败。${NC}"
             exit 1
        fi
    else
        echo -e "${RED}[错误] 未找到 python3，无法自动生成配置。请手动创建 .env 文件。${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}.env 文件已存在。${NC}"
fi

# 4. 创建必要的目录
echo -e "${BLUE}[3/5] 准备数据目录...${NC}"
mkdir -p logs
mkdir -p postgres_data
mkdir -p mongo_data
mkdir -p redis_data
# 设置权限 (根据实际情况调整，这里设为当前用户或宽松权限)
chmod 777 logs

# 5. 部署服务
echo -e "${BLUE}[4/5] 构建并启动服务...${NC}"
echo "停止旧容器..."
$COMPOSE_CMD -f docker-compose.prod.yml down --remove-orphans

echo "拉取/构建镜像..."
$COMPOSE_CMD -f docker-compose.prod.yml build

echo "启动服务..."
$COMPOSE_CMD -f docker-compose.prod.yml up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}[错误] 服务启动失败，请检查 Docker 日志。${NC}"
    exit 1
fi

# 6. 健康检查与状态展示
echo -e "${BLUE}[5/5] 等待服务就绪...${NC}"
# 简单的等待，生产环境可以使用更复杂的健康检查脚本
progress_bar() {
    local duration=$1
    local interval=0.5
    local steps=$(echo "$duration / $interval" | bc)
    local i=0
    while [ $i -lt $steps ]; do
        echo -ne "Waiting... ["
        for ((j=0; j<i; j++)); do echo -ne "#"; done
        for ((j=i; j<steps; j++)); do echo -ne " "; done
        echo -ne "]\r"
        sleep $interval
        ((i++))
    done
    echo ""
}

# 检查 bc 是否存在，不存在用简单 sleep
if command -v bc &> /dev/null; then
    progress_bar 10
else
    sleep 10
fi

echo -e "${GREEN}=== 部署完成! ===${NC}"
echo ""
echo "服务运行状态:"
$COMPOSE_CMD -f docker-compose.prod.yml ps
echo ""
echo -e "${YELLOW}注意: 如果是首次部署，请确保已初始化数据库。${NC}"
echo -e "查看日志命令: $COMPOSE_CMD -f docker-compose.prod.yml logs -f"
