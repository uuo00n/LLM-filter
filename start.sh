#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD=(docker-compose)
else
    echo "[ERROR] 未检测到 Docker Compose。请安装 Docker Desktop 或 docker-compose。"
    exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
    echo "[ERROR] 未检测到 Docker。"
    exit 1
fi

usage() {
    cat <<'EOF'
LLM Filter 统一脚本

用法:
  ./start.sh init-env        生成 .env（仅首次）
  ./start.sh up [--init-data] 构建并启动所有服务（可选初始化演示数据）
  ./start.sh init-data [--yes] 初始化 PostgreSQL/Mongo 演示数据
  ./start.sh rebuild [svc]   重构容器（默认全部，可指定服务）
  ./start.sh down            停止并删除容器
  ./start.sh rm <svc...>     删除指定容器（可多个）
  ./start.sh reset           停止并删除容器+数据卷（会清空数据库）
  ./start.sh ps              查看容器状态
  ./start.sh logs [service]  查看日志（默认全部）
  ./start.sh help            查看帮助

推荐首次使用:
  1) ./start.sh init-env
  2) 编辑 .env（至少确认 DB_PASSWORD / JWT_SECRET / DIFY_API_KEY_LLM / DIFY_API_KEY_SECURITY）
  3) ./start.sh up --init-data
EOF
}

require_env() {
    if [ ! -f .env ]; then
        echo "[ERROR] .env 不存在。先执行: ./start.sh init-env"
        exit 1
    fi
    if [ ! -r .env ]; then
        echo "[ERROR] .env 不可读。可执行: sudo chown \$USER:staff .env && chmod 640 .env"
        exit 1
    fi
}

cmd_init_env() {
    if [ -f .env ]; then
        echo "[INFO] .env 已存在，跳过生成。"
        echo "[INFO] 如需重建，请先备份后删除 .env 再执行本命令。"
        return 0
    fi
    if ! command -v python3 >/dev/null 2>&1; then
        echo "[ERROR] 未检测到 python3，无法生成 .env。"
        exit 1
    fi
    python3 scripts/generate_secrets.py
    echo "[INFO] .env 生成完成。请检查关键配置后再启动。"
}

load_env_vars() {
    require_env
    # shellcheck disable=SC1091
    set -a
    source .env
    set +a
}

wait_for_postgres() {
    local retries=30
    local i
    for ((i=1; i<=retries; i++)); do
        if "${COMPOSE_CMD[@]}" exec -T -e PGPASSWORD="${DB_PASSWORD}" postgres \
            pg_isready -U "${DB_USER}" -d "${DB_NAME}" >/dev/null 2>&1; then
            return 0
        fi
        sleep 2
    done
    echo "[ERROR] PostgreSQL 未就绪，初始化中止。"
    exit 1
}

cmd_init_data() {
    require_env
    local yes_flag="${1:-}"
    if [ "${yes_flag}" != "--yes" ]; then
        echo "[WARN] 将执行初始化脚本并重置业务数据："
        echo "       - scripts/init_postgres.sql (TRUNCATE + 默认账号)"
        echo "       - scripts/init_edu_postgres.py (教务演示数据)"
        echo "       - scripts/init_mongo.py (敏感词/对话相关集合)"
        read -r -p "确认继续? (yes/no): " answer
        if [ "${answer}" != "yes" ]; then
            echo "[INFO] 已取消。"
            return 0
        fi
    fi

    load_env_vars

    echo "[INFO] 确保初始化所需服务已启动..."
    "${COMPOSE_CMD[@]}" up -d postgres redis mongo llm-service

    echo "[INFO] 等待 PostgreSQL 就绪..."
    wait_for_postgres

    echo "[INFO] 执行 PostgreSQL 基础初始化 (init_postgres.sql)..."
    cat scripts/init_postgres.sql | "${COMPOSE_CMD[@]}" exec -T \
        -e PGPASSWORD="${DB_PASSWORD}" \
        postgres psql -v ON_ERROR_STOP=1 -U "${DB_USER}" -d "${DB_NAME}"

    echo "[INFO] 执行 PostgreSQL 教务演示数据初始化 (init_edu_postgres.py)..."
    "${COMPOSE_CMD[@]}" exec -T \
        -e DB_HOST=postgres \
        -e DB_PORT=5432 \
        -e DB_USER="${DB_USER}" \
        -e DB_PASSWORD="${DB_PASSWORD}" \
        -e DB_NAME="${DB_NAME}" \
        llm-service python /app/scripts/init_edu_postgres.py

    echo "[INFO] 执行 MongoDB 初始化 (init_mongo.py)..."
    "${COMPOSE_CMD[@]}" exec -T llm-service python /app/scripts/init_mongo.py

    echo "[INFO] 数据初始化完成。"
}

cmd_up() {
    require_env
    local init_data_flag="${1:-}"
    if [ "${init_data_flag}" != "" ] && [ "${init_data_flag}" != "--init-data" ]; then
        echo "[ERROR] up 仅支持可选参数: --init-data"
        echo "[INFO] 用法: ./start.sh up [--init-data]"
        exit 1
    fi

    "${COMPOSE_CMD[@]}" up -d --build
    echo "[INFO] 服务启动完成。"
    echo "[INFO] 网关地址: http://localhost:8080"
    echo "[INFO] 文档地址:"
    echo "       - http://localhost:8080/docs/auth/"
    echo "       - http://localhost:8080/docs/edu/"
    echo "       - http://localhost:8080/docs/llm/"
    echo "       - http://localhost:8080/docs/security/"

    if [ "${init_data_flag}" = "--init-data" ]; then
        cmd_init_data --yes
    fi
}

cmd_rebuild() {
    require_env
    if [ "${1:-}" = "" ]; then
        "${COMPOSE_CMD[@]}" up -d --build --force-recreate
        echo "[INFO] 已重构全部服务容器。"
    else
        "${COMPOSE_CMD[@]}" up -d --build --force-recreate "$@"
        echo "[INFO] 已重构服务容器: $*"
    fi
}

cmd_down() {
    "${COMPOSE_CMD[@]}" down
}

cmd_rm() {
    if [ "${1:-}" = "" ]; then
        echo "[ERROR] rm 需要至少一个服务名。"
        echo "[INFO] 用法: ./start.sh rm <service1> [service2 ...]"
        exit 1
    fi
    "${COMPOSE_CMD[@]}" rm -f -s "$@"
}

cmd_reset() {
    echo "[WARN] reset 会删除数据库卷（postgres/mongo/redis 数据将清空）"
    read -r -p "确认继续? (yes/no): " answer
    if [ "$answer" != "yes" ]; then
        echo "[INFO] 已取消。"
        return 0
    fi
    "${COMPOSE_CMD[@]}" down -v
}

cmd_ps() {
    "${COMPOSE_CMD[@]}" ps
}

cmd_logs() {
    if [ "${1:-}" = "" ]; then
        "${COMPOSE_CMD[@]}" logs -f
    else
        "${COMPOSE_CMD[@]}" logs -f "$1"
    fi
}

ACTION="${1:-help}"
case "$ACTION" in
    init-env)
        cmd_init_env
        ;;
    init-data)
        cmd_init_data "${2:-}"
        ;;
    up)
        cmd_up "${2:-}"
        ;;
    rebuild)
        cmd_rebuild "${@:2}"
        ;;
    down)
        cmd_down
        ;;
    rm)
        cmd_rm "${@:2}"
        ;;
    reset)
        cmd_reset
        ;;
    ps)
        cmd_ps
        ;;
    logs)
        cmd_logs "${2:-}"
        ;;
    help|-h|--help)
        usage
        ;;
    *)
        echo "[ERROR] 未知命令: $ACTION"
        usage
        exit 1
        ;;
esac
