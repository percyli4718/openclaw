#!/bin/bash
# 保客通 (BaokeTong) 一键启动脚本
# 用法：./scripts/start.sh [COMMAND]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 默认参数
ENV_FILE="${ENV_FILE:-.env}"
DOCKER_COMPOSE_FILE="${DOCKER_COMPOSE_FILE:-infra/docker-compose.yml}"
SKIP_ENV_CHECK="${SKIP_ENV_CHECK:-false}"

# 帮助信息
show_help() {
    cat << EOF
保客通 (BaokeTong) 一键启动脚本

用法：$0 [COMMAND]

命令:
    start           启动所有服务（默认）
    stop            停止所有服务
    restart         重启所有服务
    status          查看服务状态
    logs            查看日志
    clean           清理所有数据和容器
    rebuild         重新构建镜像
    test            运行测试

选项:
    -h, --help      显示帮助信息
    -e, --env FILE  指定环境变量文件 (默认：.env)
    --skip-env      跳过环境变量检查

示例:
    $0 start                    # 启动所有服务
    $0 logs                     # 查看实时日志
    $0 -e .env.production start # 使用生产环境配置启动

环境变量:
    POSTGRES_PASSWORD     PostgreSQL 密码
    REDIS_PASSWORD        Redis 密码
    ANTHROPIC_API_KEY     Anthropic API 密钥
    SECRET_KEY            应用密钥
    ENCRYPTION_KEY        数据加密密钥 (32 字节)

EOF
}

# 打印信息
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查环境变量文件
check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        log_warn "环境变量文件不存在：$ENV_FILE"
        log_info "创建默认环境变量文件..."
        cat > "$ENV_FILE" << 'EOF'
# 保客通 (BaokeTong) 环境变量配置

# ============================================================
# 数据库配置
# ============================================================
POSTGRES_PASSWORD=baoke_tong_dev_password
POSTGRES_PORT=5432

# ============================================================
# Redis 配置
# ============================================================
REDIS_PASSWORD=baoke_tong_redis_password
REDIS_PORT=6379

# ============================================================
# Qdrant 配置
# ============================================================
QDRANT_PORT=6333

# ============================================================
# AI 模型配置
# ============================================================
# Anthropic API 密钥 (SaaS 模式)
ANTHROPIC_API_KEY=

# Ollama 地址 (私有化模式)
OLLAMA_BASE_URL=http://host.docker.internal:11434

# ============================================================
# 应用配置
# ============================================================
APP_ENV=development
SECRET_KEY=baoke_tong_secret_key_change_in_production
ENCRYPTION_KEY=baoke_tong_encryption_key_32bytes!
DEFAULT_TENANT_ID=00000000-0000-0000-0000-000000000000

# ============================================================
# 服务端口
# ============================================================
BACKEND_PORT=8000
EOF
        log_info "默认环境变量文件已创建：$ENV_FILE"
    fi
}

# 检查必要的环境变量
check_required_env() {
    log_step "检查环境变量..."

    # 加载环境变量文件
    if [ -f "$ENV_FILE" ]; then
        set -a
        source "$ENV_FILE"
        set +a
    fi

    local missing_env=()

    # 检查必需的环境变量
    for var in "ENCRYPTION_KEY" "SECRET_KEY"; do
        if [ -z "${!var}" ]; then
            missing_env+=("$var")
        fi
    done

    # 检查 ENCRYPTION_KEY 长度
    if [ -n "$ENCRYPTION_KEY" ] && [ ${#ENCRYPTION_KEY} -lt 32 ]; then
        log_warn "ENCRYPTION_KEY 长度应至少为 32 字节"
    fi

    if [ ${#missing_env[@]} -gt 0 ]; then
        log_error "缺少必需的环境变量：${missing_env[*]}"
        log_info "请编辑 $ENV_FILE 文件并设置这些变量"
        return 1
    fi

    log_info "环境变量检查通过"
}

# 检查 Docker 和 Docker Compose
check_docker() {
    log_step "检查 Docker 环境..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        return 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        if ! docker compose version &> /dev/null; then
            log_error "Docker Compose 未安装，请先安装 Docker Compose"
            return 1
        fi
    fi

    log_info "Docker 版本：$(docker --version)"
    if docker compose version &> /dev/null; then
        docker compose version
    else
        docker-compose --version
    fi
}

# 检查端口占用
check_ports() {
    log_step "检查端口占用..."

    local ports=("5432" "6379" "6333" "8000")
    local occupied=()

    for port in "${ports[@]}"; do
        if command -v lsof &> /dev/null; then
            if lsof -i :"$port" &> /dev/null; then
                occupied+=("$port")
            fi
        elif command -v netstat &> /dev/null; then
            if netstat -tuln | grep -q ":$port "; then
                occupied+=("$port")
            fi
        fi
    done

    if [ ${#occupied[@]} -gt 0 ]; then
        log_warn "以下端口被占用：${occupied[*]}"
        log_info "如需修改端口，请编辑 $ENV_FILE 文件"
    fi
}

# 启动服务
start_services() {
    log_step "启动保客通服务..."

    check_env_file
    check_required_env || exit 1
    check_docker || exit 1
    check_ports

    log_info "创建 Docker 网络..."
    docker network create baoke-tong-network 2>/dev/null || true

    log_info "启动服务..."

    # 使用 docker compose 或 docker-compose
    if docker compose version &> /dev/null; then
        docker compose -f "$DOCKER_COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    else
        docker-compose -f "$DOCKER_COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    fi

    echo ""
    log_info "================================================"
    log_info "保客通服务已启动！"
    log_info "================================================"
    echo ""
    log_info "服务状态："
    show_status
    echo ""
    log_info "访问地址："
    log_info "  - 后端 API: http://localhost:${BACKEND_PORT:-8000}"
    log_info "  - PostgreSQL: localhost:${POSTGRES_PORT:-5432}"
    log_info "  - Redis: localhost:${REDIS_PORT:-6379}"
    log_info "  - Qdrant: http://localhost:${QDRANT_PORT:-6333}"
    echo ""
    log_info "查看日志：$0 logs"
    log_info "停止服务：$0 stop"
}

# 停止服务
stop_services() {
    log_step "停止服务..."

    if docker compose version &> /dev/null; then
        docker compose -f "$DOCKER_COMPOSE_FILE" down
    else
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
    fi

    log_info "服务已停止"
}

# 重启服务
restart_services() {
    log_step "重启服务..."
    stop_services
    sleep 2
    start_services
}

# 查看服务状态
show_status() {
    if docker compose version &> /dev/null; then
        docker compose -f "$DOCKER_COMPOSE_FILE" ps
    else
        docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    fi
}

# 查看日志
show_logs() {
    local service=$1

    if [ -n "$service" ]; then
        log_info "查看 $service 日志..."
        if docker compose version &> /dev/null; then
            docker compose -f "$DOCKER_COMPOSE_FILE" logs -f "$service"
        else
            docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f "$service"
        fi
    else
        log_info "查看所有服务日志..."
        if docker compose version &> /dev/null; then
            docker compose -f "$DOCKER_COMPOSE_FILE" logs -f
        else
            docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f
        fi
    fi
}

# 清理所有数据
clean_all() {
    log_warn "此操作将删除所有容器、卷和数据！"
    read -p "确认继续？(y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        log_info "已取消"
        return 0
    fi

    log_step "清理所有数据..."

    if docker compose version &> /dev/null; then
        docker compose -f "$DOCKER_COMPOSE_FILE" down -v
    else
        docker-compose -f "$DOCKER_COMPOSE_FILE" down -v
    fi

    # 删除网络
    docker network rm baoke-tong-network 2>/dev/null || true

    log_info "清理完成"
}

# 重新构建镜像
rebuild_images() {
    log_step "重新构建镜像..."

    if docker compose version &> /dev/null; then
        docker compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    else
        docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    fi

    log_info "镜像构建完成"
}

# 运行测试
run_tests() {
    log_step "运行测试..."
    ./scripts/test.sh
}

# 解析参数
COMMAND="start"
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -e|--env)
            ENV_FILE="$2"
            shift 2
            ;;
        --skip-env)
            SKIP_ENV_CHECK=true
            shift
            ;;
        start|stop|restart|status|logs|clean|rebuild|test)
            COMMAND="$1"
            shift
            ;;
        *)
            # 可能是服务名（logs 命令的参数）
            if [ "$COMMAND" = "logs" ]; then
                SERVICE_NAME="$1"
                shift
            else
                log_error "未知参数：$1"
                show_help
                exit 1
            fi
            ;;
    esac
done

# 执行命令
case $COMMAND in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        check_docker || exit 1
        show_status
        ;;
    logs)
        check_docker || exit 1
        show_logs "$SERVICE_NAME"
        ;;
    clean)
        clean_all
        ;;
    rebuild)
        rebuild_images
        ;;
    test)
        run_tests
        ;;
    *)
        show_help
        exit 1
        ;;
esac
